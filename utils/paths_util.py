from pathlib import Path
from functools import lru_cache

class Paths:
    ROOT = Path(__file__).parent.parent
    GUI = ROOT / "gui"
    LOGS = ROOT / "logs"
    DATA = ROOT / "data"
    
    LOG_FILE = LOGS / "system_debug.log"
    REMOTE_CACHE = DATA / "remote_cache.json"
    WINSCP_REG_KEY = r"Software\Martin Prikryl\WinSCP 2\Sessions"

    @classmethod
    @lru_cache(maxsize=1)
    def ensure_dirs(cls):
        """Crea las carpetas necesarias solo una vez."""
        for folder in [cls.LOGS, cls.DATA]:
            folder.mkdir(parents=True, exist_ok=True)
        return True

# Inicialización inmediata al importar
Paths.ensure_dirs()