import uvicorn
from log.logger import logger 
# from datetime import datetime
# from config.constants import LOG_DIR
from app import app

def start_uvicorn():
    # timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # log_path = os.path.join(LOG_DIR, timestamp + "_uvicorn.log") 

    config = uvicorn.Config(
        app=app,
        port=8000,
        host="127.0.0.1",
        # log_config=log_path,
        # timeout_keep_alive=120,
        # reload=True,
        # log_level="debug",
    )   
    
    logger.info("Starting Uvicorn...")
    server = uvicorn.Server(config)
    server.run() 

if __name__ == "__main__":
    start_uvicorn()   
   