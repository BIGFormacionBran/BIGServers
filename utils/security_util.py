import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from utils.paths_util import Paths

load_dotenv(Paths.ENV_FILE)

class SecurityUtil:
    _key = os.getenv("ENCRYPTION_KEY")
    _cipher = Fernet(_key.encode()) if _key else None

    @classmethod
    def encrypt(cls, plain_text):
        if not cls._cipher or not plain_text:
            return plain_text
        return cls._cipher.encrypt(plain_text.encode()).decode()

    @classmethod
    def decrypt(cls, encrypted_text):
        if not cls._cipher or not encrypted_text:
            return encrypted_text
        try:
            return cls._cipher.decrypt(encrypted_text.encode()).decode()
        except Exception:
            return None