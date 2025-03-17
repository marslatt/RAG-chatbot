import openai
import os 
from log import logger
from fastapi import HTTPException 
from config.constants import OPENAI_API_KEY, CHROMA_DIR, FILES_DIR, DB_DIR

class SetupService:
    '''
    Service to setup and validate configuration or other data. 
    '''   
    def validate_api_key(self): 
        '''
        Load and validate OpenAI API key in .env file   
        '''   
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        try:
            client.models.list()
        except openai.AuthenticationError as e:
            err = f"Could not validate OpenAI API key: {str(e)}"
            logger.error(err)
            raise HTTPException(
                status_code=500, # 500 Internal Server Error
                detail=err,
            )   
 
    def create_dirs(self): 
        '''
        Create 'chroma', 'files' and 'db' directories in non existant
        ''' 
        # if not os.path.exists(LOGS_DIR):
            # os.makedirs(LOGS_DIR)

        if not os.path.exists(CHROMA_DIR):
            os.makedirs(CHROMA_DIR)

        if not os.path.exists(FILES_DIR):
            os.makedirs(FILES_DIR)

        if not os.path.exists(DB_DIR):
            os.makedirs(DB_DIR)

        logger.info("Created 'chroma', 'files' and 'db' directories.")

    def delete_dirs(self):
        '''
        Delete 'chroma', 'files' and 'db' directories if existant
        ''' 
        for f in os.listdir(FILES_DIR): 
            file = os.path.join(FILES_DIR, f)
            if os.path.exists(file):
                os.remove(file)  

        for f in os.listdir(DB_DIR): 
            file = os.path.join(DB_DIR, f)
            if os.path.exists(file):
                os.remove(file) 

        os.rmdir(FILES_DIR)    
        os.rmdir(DB_DIR)    
        os.rmdir(CHROMA_DIR)         
 
        logger.info("Deleted 'chroma', 'files' and 'db' directories.")