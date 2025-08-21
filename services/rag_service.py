from config.constants import FILES_DIR, DB_DIR, OPENAI_API_KEY
#from langchain_community.document_loaders import DirectoryLoader
#from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from langchain_chroma import Chroma
from langchain.vectorstores.base import VectorStoreRetriever
from langchain_openai import OpenAIEmbeddings 
from langchain_core.documents import Document
from log import logger
from fastapi import HTTPException 
import os
from services.ocr_service import OcrService

# https://medium.com/the-modern-scientist/building-generative-ai-applications-using-langchain-and-openai-apis-ee3212400630

class RagService:
    '''
    Service for handling documents for RAG. 
    ''' 
    def __init__(self):
        self._db = None  
        self._collection = None
        self._ocr_service = None
    
    def _configure_db(self):
        '''
        Set up Chroma vector database.
        '''       
        clname = "doc"
        client = PersistentClient(path=DB_DIR) 

        try: 
            # Create or load collection if exists
            embedding_func = OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY)
            self._collection = client.get_or_create_collection(
                name=clname,
                embedding_function=embedding_func
            )             
            if self._collection is None:
                raise Exception ("Error occured while creating or loading collection")

            embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
            self._db = Chroma(
                client=client,
                collection_name=clname,
                embedding_function=embeddings,
                persist_directory=DB_DIR,
            )  
            if self._db is None:
                raise Exception("Chroma DB is not initialized properly!") 
            logger.info("Chroma DB initialized and configured.") 
        except Exception as e:
            err = f"Error occured while creating Chroma DB: {str(e)}"
            logger.error(err)
            raise HTTPException(
                status_code=500, # 500 Internal Server Error
                detail=err,
            )  
 
    def configure(self, ocr_service: OcrService):
        self._configure_db() 
        self._ocr_service = ocr_service
        logger.info("RAG service configured.")    
      
    async def add_doc(self, file_path):
        '''
        Load, transcribe, chunk and add documents to Chroma.
        ''' 
        try:
            # Transcribe file page by page 
            raw_documents = self._ocr_service.transcribe(file_path)    
            logger.info(f"{len(raw_documents)} documents received after transcribing.")    
            
            text_splitter = CharacterTextSplitter(
                separator=".",  # split on a full-stop
                chunk_size=2000, # 8000 if one full page = one chunk
                chunk_overlap=50  # overlap just for safety to avoid loss of information
            ) 
                
            # Takes in a list of documents, splits each document into smaller chunks and returns a list of text chunks.
            chunks = await text_splitter.atransform_documents(raw_documents)  
            logger.info(f"{len(chunks)} chunks created by CharacterTextSplitter.")

            # Add chunk index in metadata for extraction and sorting purposes      
            idx_chunks = []
            for i, chunk in enumerate(chunks, start=1):
                chunk.metadata["chunk"] = i  
                idx_chunks.append(chunk)            

            # Generates embeddings for a collection of documents and stores them as vectors in the Chroma database.  
            embed_ids = await self._db.aadd_documents(idx_chunks)
            logger.info(f"{len(embed_ids)} embeddings added successfully to Chroma DB.") 
        except Exception as e:
            err =  f"Error occured while adding {file_path} to database: {str(e)}"
            logger.error(err)
            raise HTTPException(
                status_code=500, # 500 Internal Server Error
                detail=err,
            )    
        finally:
            # Clean up
            for f in os.listdir(FILES_DIR): 
                file = os.path.join(FILES_DIR, f)
                if os.path.exists(file):
                    os.remove(file)  

    # TODO
    def extract_doc(self, resource_name):
        '''
        Extract and sort all chunks from the database which belong to a given file.
        '''
        meta_docs_sorted = []

        try: 
            # Filter content by metadata
            docs = self._collection.get(where={"source": resource_name})
            if docs:  
                # Pair content with metadata
                meta_docs = [
                    Document(page_content=content, metadata=meta)
                    for content, meta in zip(docs["documents"], docs["metadatas"])
                ]

                # Sort by page, then by chunk
                meta_docs_sorted = sorted(
                    meta_docs,
                    key=lambda d: (int(d.metadata.get("page", 0)), int(d.metadata.get("chunk", 0)))
                )
            return meta_docs_sorted
        except Exception as e:
            err =  f"Error occured while extracting {resource_name} from database: {str(e)}"
            logger.error(err)
            raise HTTPException(
                status_code=500, # 500 Internal Server Error
                detail=err,
            )  

    def get_retriever(self) -> VectorStoreRetriever: 
        return self._db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        # return self.db.as_retriever()
 
    def delete_docs(self): 
        '''
        Delete douments from collection.
        '''
        doc_ids = self._collection.get()["ids"]
        self._collection.delete(ids=doc_ids)        
        # self.db.delete_collection("doc")
        # self.db.reset_collection(name="doc")
        # self.client.delete_collection(name="doc")
        # self.client.create_collection(name="doc")
        # self.db._client._system.stop()
         
