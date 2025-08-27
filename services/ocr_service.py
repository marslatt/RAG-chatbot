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
import asyncio
import time 

# https://python.langchain.com/docs/how_to/multimodal_inputs/

MAX_CONCURRENT = 3
MAX_ATTEMPTS = 5
BASE_DELAY = 2

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

    async def transcribe_page(self, page_num, page_bytes, file_path):
        '''
        Transcribe a single page using OCR pipeline.
        ''' 
        # Convert raw image bytes to base64 string
        image_b64 = base64.b64encode(page_bytes).decode("utf-8")
        # Transcribe and add metadata 
        text = await self._chain.ainvoke({"image": image_b64})
        if not text:
            raise ValueError(f"Empty transcription result for page {page_num}")
        logger.info(f"Transcribed page {page_num} of {file_path}.") 
        return Document(page_content=text, metadata={"source": os.path.basename(file_path), "page": page_num})    

    async def transcribe(self, file_path) -> list[Document]:
        '''
        Transcribe a file page by page asynchronously.
        '''
        start = time.time()
        sem = asyncio.Semaphore(MAX_CONCURRENT)
        
        async def sem_task(page_num, page_bytes, file_path):
            for attempt in range(1, MAX_ATTEMPTS + 1):                
                try:
                    async with sem:
                        return await self.transcribe_page(page_num, page_bytes, file_path)
                except Exception as e:                        
                    wait_time = BASE_DELAY * attempt 
                    logger.error(f"{type(e).__name__}: on page {page_num} in {file_path}. Retrying in {wait_time}s.")                            
                    await asyncio.sleep(wait_time)                            
            # Return empty document if transcription unsuccessfull for MAX_ATTEMPTS.  
            return Document(page_content="", metadata={"source": os.path.basename(file_path), "page": page_num})    
        
        try:
            with fitz.open(file_path) as pdf_doc:   
                rendered_pages = [
                    (page_num, page.get_pixmap(dpi=300).tobytes("png"))
                    for page_num, page in enumerate(pdf_doc, start=1)
                ]
            
            tasks = [asyncio.create_task(sem_task(page_num, page_bytes, file_path)) for page_num, page_bytes in rendered_pages] 
            results = await asyncio.gather(*tasks, return_exceptions=True) # TODO
            end = time.time()  
            logger.info(f"Transcribed {len(results)} pages of document {file_path} in {end - start}s.") 
            return results 
        except Exception as e:
            err = f"Error occured while transcribing {file_path}: {str(e)}"
            logger.error(err)
            raise HTTPException(
                status_code=500,
                detail=err,
            )        