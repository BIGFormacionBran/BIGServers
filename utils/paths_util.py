import sys
from pathlib import Path

class Paths:
    IS_FROZEN = getattr(sys, 'frozen', False)
    # Directorio raíz del proyecto o del ejecutable
    BASE_DIR = Path(sys.executable).parent if IS_FROZEN else Path(__file__).parent.parent
    
    DATA = BASE_DIR / "data"
    LOGS = BASE_DIR / "logs"
    
    LOG_FILE = LOGS / "app.log"
    REMOTE_CACHE = DATA / "cache.json"
    ENV_FILE = BASE_DIR / ".env"

    @classmethod
    def init(cls):
        """Crea la estructura de carpetas necesaria."""
        for p in [cls.DATA, cls.LOGS]:
            p.mkdir(parents=True, exist_ok=True)

Paths.init()