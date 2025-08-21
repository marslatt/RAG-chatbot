import base64
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from config.constants import OPENAI_API_KEY, OPENAI_LLM, FILES_DIR
from log import logger
from fastapi import HTTPException
from langchain_core.documents import Document
# from langchain.schema import Document
import os
import fitz

# https://python.langchain.com/docs/how_to/multimodal_inputs/

class OcrService:
    def __init__(self):
        self._llm = None
        self._chain = None

    def _create_chain(self):
        ocr_sys_prompt = (
            "You are an OCR and text extraction assistant. "
            "Extract and clean all text and tables from the given image, "
            "which represents a scanned document page in Bulgarian. "
            "Strictly preserve the structure and meaning of the text. "
            "Output the extracted transcribed content in plain UTF-8 text."
        )

        # Insert in the prompt template an in-line image as base64 string
        ocr_prompt_template = ChatPromptTemplate.from_messages([
            ("system", ocr_sys_prompt),
            ("user", [
                {
                    "type": "image",
                    "source_type": "base64",
                    "mime_type": "image/png",   
                    "data": "{image}"
                }  
            ])
        ])
        self._chain = ocr_prompt_template | self._llm | StrOutputParser()

    def configure(self):
        self._llm = ChatOpenAI(
            model=OPENAI_LLM,
            openai_api_key=OPENAI_API_KEY,
            temperature=0  
        )
        self._create_chain()
        logger.info("OCR service configured.")

    def transcribe(self, file_path) -> str:
        '''
        Transcribe a file page by page 
        '''
        documents = []

        try:
            with fitz.open(file_path) as pdf_doc:
                for page_num, page in enumerate(pdf_doc):
                    # Render doc page to image, convert to raw image bytes and then to base64 string
                    pix = page.get_pixmap(dpi=300)  
                    image_bytes = pix.tobytes("png")  
                    image_b64 = base64.b64encode(image_bytes).decode("utf-8") 

                    # Transcribe and add metadata
                    text_content = self._chain.invoke({"image": image_b64}) 
                    if text_content:
                        documents.append(Document(
                            page_content=text_content,
                            metadata={"source": os.path.basename(file_path), "page": page_num + 1}
                        ))
            return documents
        except Exception as e:
            err = f"Error occured while transcribing {file_path}: {str(e)}"
            logger.error(err)
            raise HTTPException(
                status_code=500,
                detail=err,
            )