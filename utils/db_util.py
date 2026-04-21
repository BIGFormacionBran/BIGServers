import os
import time
import psycopg2
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from utils.paths_util import Paths
from utils.logger_util import Logger

log = Logger.get_logger("DB_UTIL")
load_dotenv(Paths.ENV_FILE)

class DBUtil:
    DATABASE_URL = os.getenv("DATABASE_URL")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
    
    cipher_suite = None
    if ENCRYPTION_KEY:
        try:
            cipher_suite = Fernet(ENCRYPTION_KEY.encode())
        except Exception as e:
            log.error(f"Error inicializando cipher_suite: {e}")

    @classmethod
    def get_server_list(cls):
        log.info("DB: Solicitando lista de servidores")
        if not cls.DATABASE_URL:
            log.error("DATABASE_URL no definida")
            return []
            
        t0 = time.time()
        try:
            conn = psycopg2.connect(cls.DATABASE_URL)
            cur = conn.cursor()
            cur.execute("SELECT nombre FROM SERVIDOR ORDER BY nombre ASC;")
            servers = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            log.info(f"DB: Lista obtenida en {time.time()-t0:.4f}s")
            return servers
        except Exception as e:
            log.error(f"Error DB (get_server_list): {e}")
            return []

    @classmethod
    def get_server_details(cls, name):
        log.info(f"DB: Solicitando detalles de {name}")
        if not cls.DATABASE_URL or not cls.cipher_suite:
            log.error("Configuración de DB o cifrado incompleta")
            return None

        t0 = time.time()
        try:
            conn = psycopg2.connect(cls.DATABASE_URL)
            cur = conn.cursor()
            cur.execute("""
                SELECT s.host, s.usuario_ssh, s.password_ssh, s.puerto, s.fingerprint, t.nombre
                FROM SERVIDOR s
                JOIN TIPO_CONEXION t ON s.tipo_id = t.id
                WHERE s.nombre = %s;
            """, (name,))
            row = cur.fetchone()
            cur.close()
            conn.close()

            if row:
                decrypted_pass = cls.cipher_suite.decrypt(row[2].encode()).decode()
                log.info(f"DB: Detalles de {name} obtenidos y descifrados en {time.time()-t0:.4f}s")
                return {
                    "host": row[0],
                    "user": row[1],
                    "password": decrypted_pass,
                    "port": row[3],
                    "fingerprint": row[4],
                    "type": row[5]
                }
            log.warning(f"DB: Servidor {name} no encontrado")
        except Exception as e:
            log.error(f"Error DB (get_server_details): {e}")
            
        return None