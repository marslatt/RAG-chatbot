from config.constants import FILES_DIR, DB_DIR, OPENAI_API_KEY 
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from langchain_chroma import Chroma
from langchain.vectorstores.base import VectorStoreRetriever
from langchain_openai import OpenAIEmbeddings
from log import logger
from fastapi import HTTPException 
import os

# https://medium.com/the-modern-scientist/building-generative-ai-applications-using-langchain-and-openai-apis-ee3212400630

class RagService:
    '''
    Service for handling .txt documents for RAG. 
    ''' 
    def __init__(self):
        self.db = None  
        self.collection = None
    
    def configure_db(self):
        '''
        Set up Chroma vector database.
        '''       
        clname = "doc"
        client = PersistentClient(path=DB_DIR) 

        try: 
            # Create or load collection if exists
            embedding_func = OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY)
            self.collection = client.get_or_create_collection(
                name=clname,
                embedding_function=embedding_func
            )             
            if self.collection is None:
                raise Exception ("Error occured while creating or loading collection")

            embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
            self.db = Chroma(
                client=client,
                collection_name=clname,
                embedding_function=embeddings,
                persist_directory=DB_DIR,
            )  
            if self.db is None:
                raise Exception("Chroma DB is not initialized properly!") 
            logger.info("Chroma DB initialized and configured.") 
        except Exception as e:
            err = f"Error occured while creating Chroma DB: {str(e)}"
            logger.error(err)
            raise HTTPException(
                status_code=500, # 500 Internal Server Error
                detail=err,
            )  
      
    async def add_docs(self):
        '''
        Load, split and add .txt documents to Chroma.
        ''' 
        try:
            # Load list of .txt documents
            loader = DirectoryLoader(
                FILES_DIR,
                glob='**/*.txt',
                loader_cls=TextLoader
            )
            raw_documents = await loader.aload()
            logger.info(f"{len(raw_documents)} documents loaded by DirectoryLoader.")

            text_splitter = CharacterTextSplitter(
                separator=".",  # split on a full-stop
                chunk_size=1000,
                chunk_overlap=50  # overlap to avoid loss of information
            )
                
            # Takes in a list of documents and splits each document into smaller chunks based on a specified size. 
            # Returns a list of text chunks, each of which is a substring of the original document.           
            chunks = await text_splitter.atransform_documents(raw_documents)  
            logger.info(f"{len(chunks)} chunks created by CharacterTextSplitter.")

            # Generates embeddings (mappings) for a collection of documents to be stored in the Chroma database. 
            # Stores embeddings as vectors (and optionally their metadata), allowing for efficient vector searches.
            embed_ids = await self.db.aadd_documents(chunks)
            logger.info(f"{len(embed_ids)} embeddings added successfully to Chroma DB.")
        except Exception as e:
            err =  f"Error occured while adding documents to database: {str(e)}"
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

    def get_retriever(self) -> VectorStoreRetriever: 
        return self.db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        # return self.db.as_retriever()
 
    def delete_docs(self): 
        '''
        Delete douments from collection.
        '''
        doc_ids = self.collection.get()["ids"]
        self.collection.delete(ids=doc_ids)
        
        # self.db.delete_collection("doc")
        # self.db.reset_collection(name="doc")
        # self.client.delete_collection(name="doc")
        # self.client.create_collection(name="doc")
        # self.db._client._system.stop()
         
