import os
import psycopg2
from dotenv import load_dotenv
from utils.paths_util import Paths

load_dotenv(Paths.ENV_FILE)

class DBUtil:
    DATABASE_URL = os.getenv("DATABASE_URL")

    @classmethod
    def get_connection(cls):
        return psycopg2.connect(cls.DATABASE_URL)

    @classmethod
    def execute_query(cls, query, params=None, fetch=True):
        """Método genérico optimizado para ejecutar y cerrar."""
        with cls.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall()
                conn.commit()
                return None