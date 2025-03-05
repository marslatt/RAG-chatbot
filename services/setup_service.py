import openai
import os 
from log.logger import logger
from fastapi import HTTPException 
from config.constants import OPENAI_API_KEY, LOG_DIR, FILES_DIR, CHROMA_DIR

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
        Create 'logs', 'files' and 'chroma_db' directories in non existant
        ''' 
        logs_path = f"{LOG_DIR}{os.sep}logs"
        if not os.path.exists(logs_path):
            os.makedirs(logs_path)

        if not os.path.exists(FILES_DIR):
            os.makedirs(FILES_DIR)

        if not os.path.exists(CHROMA_DIR):
            os.makedirs(CHROMA_DIR)
 