import logging
from utils.paths_util import Paths

class Logger:
    @staticmethod
    def get_logger(name):
        logger = logging.getLogger(name)
        if not logger.handlers:
            logger.setLevel(logging.DEBUG)
            # Formato con milisegundos y alineación
            formatter = logging.Formatter('%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-12s | %(message)s', 
                                          datefmt='%H:%M:%S')

            file_handler = logging.FileHandler(Paths.LOG_FILE, encoding='utf-8')
            file_handler.setFormatter(formatter)
            
            # También mandamos a consola para debugging rápido si lanzas el script
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console)
            logger.propagate = False
        return logger