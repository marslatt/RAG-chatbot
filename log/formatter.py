import logging

# https://medium.com/@balakrishnamaduru/mastering-logging-in-python-a-singleton-logger-with-dynamic-log-levels-17f3e8bfa2cf

class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    RESET = "\033[0m"

class ColoredFormatter(logging.Formatter):
    ''''
    Colored formatter for logging    
    '''   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record):
        color = Colors.WHITE  # default to white
        if record.levelno == logging.DEBUG:
            color = Colors.CYAN
        elif record.levelno == logging.INFO:
            color = Colors.GREEN
        elif record.levelno == logging.WARNING:
            color = Colors.YELLOW
        elif record.levelno == logging.ERROR:
            color = Colors.RED
        elif record.levelno == logging.CRITICAL:
            color = Colors.PURPLE

        record.levelname = f"{color}{record.levelname}{Colors.RESET}" 
        # record.asctime = f"{Colors.GREEN}{record.asctime}{Colors.RESET}" 
        record.filename = f"{Colors.BLUE}{record.filename}{Colors.RESET}" 
        record.lineno = f"{Colors.BLUE}{record.lineno}{Colors.RESET}" 
        return super().format(record)
