from pathlib import Path
from functools import lru_cache
import sys

class Paths:
    # BASE_DIR es donde reside el ejecutable (o el script main.py)
    if getattr(sys, 'frozen', False):
        BASE_DIR = Path(sys.executable).parent
    else:
        BASE_DIR = Path(__file__).parent.parent

    # ROOT solo para recursos estáticos del código si fuera necesario
    ROOT = Path(__file__).parent.parent
    
    GUI = ROOT / "gui"
    LOGS = BASE_DIR / "logs"
    DATA = BASE_DIR / "data"
    
    LOG_FILE = LOGS / "system_debug.log"
    REMOTE_CACHE = DATA / "remote_cache.json"
    VERSION_JSON = DATA / "version.json"
    # El .env sí puede ir dentro del EXE para proteger las contraseñas base
    ENV_FILE = Path(sys._MEIPASS) / ".env" if getattr(sys, 'frozen', False) else ROOT / ".env"
    
    WINSCP_REG_KEY = r"Software\Martin Prikryl\WinSCP 2\Sessions"

    @classmethod
    @lru_cache(maxsize=1)
    def ensure_dirs(cls):
        for folder in [cls.LOGS, cls.DATA]:
            folder.mkdir(parents=True, exist_ok=True)
        return True

Paths.ensure_dirs()