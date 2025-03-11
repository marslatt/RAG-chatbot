import os
import logging   
import threading
# from datetime import datetime
from config.constants import LOG_DIR
from log.formatter import ColoredFormatter

# https://docs.python.org/3/library/configparser.html#supported-ini-file-structure
# https://signoz.io/guides/what-is-pythons-default-logging-formatter/

class SingletonLogger():
  ''''
  Singleton logger class 
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
      config_path = os.path.join(LOG_DIR, "logger.ini") 
      # timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") 
      # log_path = os.path.join(LOG_DIR, timestamp + ".log")
      log_path = os.path.join(LOG_DIR, "info.log")
      
      logging.config.fileConfig(
        config_path,
        disable_existing_loggers=False,
        defaults={"logfilename": log_path}
      )                    
      self.logger = logging.getLogger() 
      self._set_formatter() 

  def _set_formatter(self):
      format = "%(levelname)s - [%(asctime)s.%(msecs)03d] - [%(filename)s:%(lineno)s - %(funcName)s] - %(message)s"
      formatter = ColoredFormatter(format)
      if self.logger.hasHandlers():
         for handler in self.logger.handlers:
            if not isinstance(handler, logging.FileHandler):
              handler.formatter = formatter 
      else:
         handler = logging.StreamHandler()
         handler.setFormatter(formatter)
         self.logger.addHandler(handler)        
     
  def get_logger(self):   
     return self.logger
            
logger = SingletonLogger().get_logger() 