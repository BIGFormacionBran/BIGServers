import json
from pathlib import Path
from utils.logger_util import Logger

log = Logger.get_logger("JSON_UTIL")

class JsonUtil:
    @staticmethod
    def save(path: Path, data):
        """Escribe contenido en el path del JSON especificado."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            log.error(f"Fallo al guardar JSON en {path}: {e}")
            return False

    @staticmethod
    def load(path: Path):
        """Lee el JSON del path especificado y devuelve su contenido."""
        if not path.exists():
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log.error(f"Fallo al leer JSON en {path}: {e}")
            return None