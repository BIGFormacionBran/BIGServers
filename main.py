#!/usr/bin/env python3
from managers.app_manager import AppManager
from utils.logger_util import Logger

def main():
    log = Logger.get_logger("MAIN")
    try:
        log.info("Iniciando Sistema...")
        app = AppManager()
        app.start()
    except Exception as e:
        log.error(f"Error fatal: {e}", exc_info=True)

if __name__ == "__main__":
    main()