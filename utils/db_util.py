import os
import psycopg2
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from .paths_util import Paths
from .logger_util import Logger

log = Logger.get_logger("DB_UTIL")
load_dotenv(Paths.ENV_FILE)

class DBUtil:
    DATABASE_URL = os.getenv("DATABASE_URL")
    _cipher = None

    if key := os.getenv("ENCRYPTION_KEY"):
        try: _cipher = Fernet(key.encode())
        except: log.error("Llave de cifrado inválida")

    @classmethod
    def _query(cls, sql, params=None, fetch=True):
        if not cls.DATABASE_URL: return None
        try:
            with psycopg2.connect(cls.DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    return cur.fetchall() if fetch else True
        except Exception as e:
            log.error(f"Error DB: {e}")
            return None

    @classmethod
    def get_server_list(cls):
        rows = cls._query("SELECT nombre FROM SERVIDOR ORDER BY nombre ASC;")
        return [r[0] for r in rows] if rows else []

    @classmethod
    def get_server_details(cls, name):
        sql = """SELECT s.host, s.usuario_ssh, s.password_ssh, s.puerto, s.fingerprint, t.nombre
                 FROM SERVIDOR s JOIN TIPO_CONEXION t ON s.tipo_id = t.id WHERE s.nombre = %s;"""
        row = cls._query(sql, (name,))
        if not row or not cls._cipher: return None
        r = row[0]
        return {
            "host": r[0], "user": r[1],
            "password": cls._cipher.decrypt(r[2].encode()).decode(),
            "port": r[3], "fingerprint": r[4], "type": r[5]
        }