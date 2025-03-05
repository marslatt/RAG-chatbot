import os
from dotenv import find_dotenv, load_dotenv 
 
env_file = find_dotenv()
load_dotenv(env_file) 

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 

OPENAI_LLM = "gpt-4o"

CONFIG_DIR = f".{os.sep}config" 

LOG_DIR = f".{os.sep}log"

CHROMA_DIR = f".{os.sep}chroma_db" 

FILES_DIR = f".{os.sep}files" 