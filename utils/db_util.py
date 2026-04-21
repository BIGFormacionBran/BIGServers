import os
import psycopg2
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from utils.paths_util import Paths
from utils.logger_util import Logger

log = Logger.get_logger("DB_UTIL")

# Cargamos las variables desde el .env (que Paths localiza automáticamente)
load_dotenv(Paths.ENV_FILE)

class DBUtil:
    # Leemos de las variables de entorno inyectadas por el Secret de GitHub
    DATABASE_URL = os.getenv("DATABASE_URL")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
    
    # Inicializamos el suite de cifrado solo si la clave existe
    cipher_suite = None
    if ENCRYPTION_KEY:
        try:
            cipher_suite = Fernet(ENCRYPTION_KEY.encode())
        except Exception as e:
            log.error(f"Error al inicializar la clave de cifrado: {e}")

    @classmethod
    def get_server_list(cls):
        """Obtiene solo los nombres para el Combobox"""
        if not cls.DATABASE_URL:
            log.error("DATABASE_URL no configurada.")
            return []
            
        try:
            conn = psycopg2.connect(cls.DATABASE_URL)
            cur = conn.cursor()
            cur.execute("SELECT nombre FROM SERVIDOR ORDER BY nombre ASC;")
            servers = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            return servers
        except Exception as e:
            log.error(f"Error al listar servidores de DB: {e}")
            return []

    @classmethod
    def get_server_details(cls, name):
        """Obtiene todos los datos y DESCIFRA la contraseña"""
        if not cls.DATABASE_URL or not cls.cipher_suite:
            log.error("Configuración de DB o Cifrado incompleta.")
            return None

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
                # Descifrar la contraseña usando la clave del Secret
                encrypted_pass = row[2]
                decrypted_pass = cls.cipher_suite.decrypt(encrypted_pass.encode()).decode()
                
                return {
                    "host": row[0],
                    "user": row[1],
                    "password": decrypted_pass,
                    "port": row[3],
                    "fingerprint": row[4],
                    "type": row[5]
                }
        except Exception as e:
            log.error(f"Error al obtener detalles del servidor {name}: {e}")
            
        return None