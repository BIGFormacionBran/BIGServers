import logging
from .paths_util import Paths

class Logger:
    @staticmethod
    def get_logger(name):
        logger = logging.getLogger(name)
        
        if not logger.handlers:
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s | %(levelname)-7s | %(name)s | %(message)s')

            # Sin strings, solo referencia a Paths
            file_handler = logging.FileHandler(Paths.LOG_FILE, encoding='utf-8')
            file_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.propagate = False
            
        return logger