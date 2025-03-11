import os
from dotenv import find_dotenv, load_dotenv 
 
env_file = find_dotenv()
load_dotenv(env_file) 

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 

OPENAI_LLM = "gpt-4o"

CONFIG_DIR = "." + os.sep + "config" 

LOG_DIR = "." + os.sep + "log"

# LOGS_DIR = LOG_DIR + os.sep + "logs"

CHROMA_DIR = "." + os.sep + "chroma" 

DB_DIR = CHROMA_DIR + os.sep + "db"

FILES_DIR = CHROMA_DIR + os.sep + "files" 