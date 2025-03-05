# https://medium.com/@balakrishnamaduru/mastering-logging-in-python-a-singleton-logger-with-dynamic-log-levels-17f3e8bfa2cf
# https://signoz.io/guides/what-is-pythons-default-logging-formatter/

import os
import logging 
import logging.config  
import threading
from datetime import datetime
from config.constants import LOG_DIR

class SingletonLogger():
  ''''
  Singleton class for logging
  ''' 
  _instance = None
  _lock = threading.Lock()

  def __new__(cls, *args, **kwargs): 
        if not cls._instance:
            with cls._lock:
              if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance._initialize(*args, **kwargs)
        return cls._instance
  
  def _initialize(self):
      config_path = f"{LOG_DIR}{os.sep}logger.ini"
      timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") 
      log_path = os.path.join({LOG_DIR}, timestamp + ".log") 
      
      logging.config.fileConfig(
        config_path,
        disable_existing_loggers=False,
        defaults={"logfilename": log_path},
      )                    
      self.logger = logging.getLogger() 

  def get_logger(self):
    return self.logger 
        
logger = SingletonLogger().get_logger()