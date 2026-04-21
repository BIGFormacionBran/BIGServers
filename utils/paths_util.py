import sys
from pathlib import Path
from functools import lru_cache

class Paths:
    IS_FROZEN = getattr(sys, 'frozen', False)
    BASE_DIR = Path(sys.executable).parent if IS_FROZEN else Path(__file__).parent.parent
    
    # Directorios base
    LOGS = BASE_DIR / "logs"
    DATA = BASE_DIR / "data"
    
    # Archivos específicos
    LOG_FILE = LOGS / "system_debug.log"
    REMOTE_CACHE = DATA / "remote_cache.json"
    ENV_FILE = (Path(sys._MEIPASS) / ".env") if IS_FROZEN and hasattr(sys, '_MEIPASS') else BASE_DIR / ".env"

    @classmethod
    @lru_cache(maxsize=1)
    def ensure_dirs(cls):
        """Crea las carpetas necesarias una sola vez."""
        for p in [cls.LOGS, cls.DATA]:
            p.mkdir(parents=True, exist_ok=True)
        return True

Paths.ensure_dirs()