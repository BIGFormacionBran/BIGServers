import os
import time
import psycopg2
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from .paths_util import Paths
from .logger_util import Logger

log = Logger.get_logger("DB_UTIL")
load_dotenv(Paths.ENV_FILE)

class DBUtil:
    DATABASE_URL = os.getenv("DATABASE_URL")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
    _cipher = None

    if ENCRYPTION_KEY:
        try: _cipher = Fernet(ENCRYPTION_KEY.encode())
        except Exception as e: log.error(f"Error Fernet: {e}")

    @classmethod
    def _execute(cls, query, params=None):
        start = time.perf_counter()
        if not cls.DATABASE_URL: return None
        try:
            with psycopg2.connect(cls.DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    res = cur.fetchall()
                    log.info(f"⏱️ Query OK: {(time.perf_counter()-start)*1000:.2f}ms")
                    return res
        except Exception as e:
            log.error(f"❌ Error SQL: {e}")
            return None

    @classmethod
    def get_server_list(cls):
        rows = cls._execute("SELECT nombre FROM SERVIDOR ORDER BY nombre ASC;")
        return [r[0] for r in rows] if rows else []

    @classmethod
    def get_server_details(cls, name):
        sql = """SELECT s.host, s.usuario_ssh, s.password_ssh, s.puerto, s.fingerprint, t.nombre
                 FROM SERVIDOR s JOIN TIPO_CONEXION t ON s.tipo_id = t.id WHERE s.nombre = %s;"""
        rows = cls._execute(sql, (name,))
        if not rows or not cls._cipher: return None
        r = rows[0]
        return {
            "host": r[0], "user": r[1],
            "password": cls._cipher.decrypt(r[2].encode()).decode(),
            "port": r[3], "fingerprint": r[4], "type": r[5]
        }