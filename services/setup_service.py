import shutil
import openai
import os 
from log import logger
from fastapi import HTTPException 
from config.constants import OPENAI_API_KEY, CHROMA_DIR, FILES_DIR, DB_DIR

class SetupService:
    '''
    Service to setup and validate configuration or other data. 
    '''   
    def _validate_api_key(self): 
        '''
        Load and validate OpenAI API key in .env file   
        '''   
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        try:
            client.models.list()
            logger.info("OPENAI API key validated.") 
        except openai.AuthenticationError as e:
            err = f"Could not validate OpenAI API key: {str(e)}"
            logger.error(err)
            raise HTTPException(
                status_code=500, # 500 Internal Server Error
                detail=err,
            )   
 
    def _create_dirs(self): 
        '''
        Create 'chroma', 'files' and 'db' directories in non existant
        ''' 
        try:            
            if os.path.exists(FILES_DIR):
                shutil.rmtree(os.path.abspath(FILES_DIR))
                logger.info("Deleted 'files' directory.")
            
            if os.path.exists(DB_DIR):
                shutil.rmtree(os.path.abspath(DB_DIR))
                logger.info("Deleted 'db' directory.")            

            if os.path.exists(CHROMA_DIR):
                shutil.rmtree(os.path.abspath(CHROMA_DIR))
                logger.info("Deleted 'chroma' directory.")

            os.makedirs(CHROMA_DIR)
            os.makedirs(FILES_DIR)
            os.makedirs(DB_DIR) 
            logger.info("Created new 'chroma', 'files' and 'db' directories.")
        except Exception as e:
            err =  f"Error occured while creating directories: {str(e)}"
            logger.error(err)
            raise HTTPException(
                status_code=500, # 500 Internal Server Error
                detail=err,
            )     

    def configure(self): 
        self._validate_api_key()        
        self._create_dirs()
        logger.info("Setup service configured.") 