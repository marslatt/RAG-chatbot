import openai
import os 
from log import logger
from fastapi import HTTPException 
from config.constants import OPENAI_API_KEY, CHROMA_DIR, FILES_DIR, DB_DIR

class SetupService:
    '''
    Service to setup and validate configuration or other data passed to the application. 
    '''   
    def validate_api_key(): 
        '''
        Load and validate OpenAI API key in .env file   
        '''   
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        try:
            client.models.list()
        except openai.AuthenticationError as e:
            logger.error(e.message)
            raise HTTPException(
            status_code=200,
            detail=e.message,
        )   
 
    def create_dirs(): 
        '''
        Create 'logs', 'chroma', 'files' and 'db' directories in non existant
        ''' 
        # if not os.path.exists(LOGS_DIR):
            # os.makedirs(LOGS_DIR)

        if not os.path.exists(CHROMA_DIR):
            os.makedirs(CHROMA_DIR)

        if not os.path.exists(FILES_DIR):
            os.makedirs(FILES_DIR)

        if not os.path.exists(DB_DIR):
            os.makedirs(DB_DIR)
 