import os
import psycopg2
from psycopg2.extras import RealDictCursor
from utils.logger_util import Logger

log = Logger.get_logger("DB_UTIL")

class DBUtil:
    @staticmethod
    def _get_connection():
        conn_str = os.getenv("DATABASE_URL")
        if not conn_str:
            log.error("Falta DATABASE_URL en el entorno.")
            return None
        return psycopg2.connect(conn_str)

    @classmethod
    def get_server_details(cls, server_name):
        conn = cls._get_connection()
        if not conn: return None
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT s.*, t.nombre as tipo 
                    FROM SERVIDOR s 
                    JOIN TIPO_CONEXION t ON s.tipo_id = t.id 
                    WHERE LOWER(s.nombre) = LOWER(%s)
                """, (server_name,))
                return cur.fetchone()
        finally:
            conn.close()