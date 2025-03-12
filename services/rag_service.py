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

# https://medium.com/the-modern-scientist/building-generative-ai-applications-using-langchain-and-openai-apis-ee3212400630

class RagService:
    '''
    Service for handling .txt documents for RAG. 
    ''' 
    def __init__(self):
        self.db = None  
    
    def configure_db(self):
        '''
        Set up Chroma vector database.
        '''       
        clname = "doc"
        client = PersistentClient(path=DB_DIR) 

        try: 
            # Create or load collection if exists.
            embedding_func = OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY)
            collection = client.get_or_create_collection(
                name=clname,
                embedding_function=embedding_func
            ) 
        except Exception as e:
            err = f"Error occured while creating or loading collection: {str(e)}"
            logger.error(err)
            raise HTTPException(
            status_code=500,
            detail=err,
        )  
 
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        self.db = Chroma(
            client=client,
            collection_name=clname,
            embedding_function=embeddings,
            persist_directory=DB_DIR,
        )  
        if self.db is None:
            err = "Chroma DB is not initialized properly!"
            logger.error(err)
            raise HTTPException(
            status_code=500,
            detail=err,
            )
      

    async def add_docs(self) -> list[str]:
        '''
        Load, split and add .txt documents to Chroma.
        ''' 
        # Load list of .txt documents.
        loader = DirectoryLoader(
            FILES_DIR,
            glob='**/*.txt',
            loader_cls=TextLoader
        )
        raw_documents = await loader.aload()

        # Split documents into chunks.
        text_splitter = CharacterTextSplitter(
            separator=".",  # split on a full-stop
            chunk_size=1000,
            chunk_overlap=50  # overlap to avoid loss of information
        )

        # Add documents to database.
        try: 
            docs = await text_splitter.atransform_documents(raw_documents) 
            # TODO add only unique_docs
            doc_ids = await self.db.aadd_documents(docs)
        except Exception as e:
            err =  f"Error occured while adding documents to database: {str(e)}"
            logger.error(err)
            raise HTTPException(
            status_code=500,
            detail=err,
        )             
        return doc_ids

    def get_retriever(self) -> VectorStoreRetriever:
        # return db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        return self.db.as_retriever()

    # TODO
    def delete_docs(self): 
        # client.delete_collection(name=clname)
        pass
