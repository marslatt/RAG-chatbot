import os
import uvicorn
# from log.logger import logger
from services import service_provider  
from datetime import datetime
from config.constants import LOG_DIR

 
import logging
import uvicorn
import sys

 

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
file_handler = logging.FileHandler("info.log")
file_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

logger.info('API is starting up')

def main_setup():
    setup_service = service_provider.SetupService
    setup_service.create_dirs()
    setup_service.validate_api_key()
    logger.info("OPENAI API key validated.") 

def start_uvicorn():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = f"{LOG_DIR}{os.sep}logs{os.sep}{timestamp}_uvicorn.log"
    
    config = uvicorn.Config(
        app="app:app",
        port=8000,
        host="127.0.0.1",
        log_config=log_path,
        timeout_keep_alive=120,
        reload=True,
        log_level="info",
        #formatters={'standard'},
    )   
    config["formatters"]["access"]["fmt"] = "UVICORN ___ %(asctime)s - %(levelname)s - %(message)s"
    config["formatters"]["default"]["fmt"] = "UVICORN ___ %(asctime)s - %(levelname)s - %(message)s"

    logger.info("Starting Uvicorn...")
    server = uvicorn.Server(config)
    server.run() 

if __name__ == "__main__":
    main_setup()
    start_uvicorn()   
   