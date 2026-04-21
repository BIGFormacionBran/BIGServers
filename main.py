#!/usr/bin/env python3
from managers.app_manager import AppManager
from utils.logger_util import Logger

log = Logger.get_logger("MAIN")

def main():
    try:
        log.info("--- Iniciando Aplicación ---")
        
        # El AppManager orquestará el inicio de la GUI y la lógica SFTP
        app = AppManager()
        app.start()
        
    except Exception as e:
        log.error(f"Error crítico: {e}", exc_info=True)
    finally:
        log.info("--- Aplicación Cerrada ---")

if __name__ == "__main__":
    main()