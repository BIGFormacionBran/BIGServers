import os
from dotenv import load_dotenv
from utils.ssh_util import SSHUtil
from utils.db_util import DBUtil
from utils.paths_util import Paths
from utils.logger_util import Logger

log = Logger.get_logger("SFTP_MANAGER")

class SFTPManager:
    def __init__(self):
        # Cargamos el .env (que ahora tendrá la DATABASE_URL)
        load_dotenv(Paths.ENV_FILE)
        
        self.ssh_client = None
        self.sftp_client = None
        self.current_session = None

    def connect(self, server_name):
        """Conexión usando datos de la base de datos."""
        # Obtenemos los datos (incluida la pass) de la DB
        server = DBUtil.get_server_details(server_name)
        
        if not server:
            return False, "Servidor no encontrado en la base de datos."

        # Si ya estamos conectados al mismo, no hacemos nada
        if self.current_session == server_name and self.ssh_client:
            return True, "ALREADY_CONNECTED"

        self.disconnect()

        # Usamos los datos de la DB. Las keys coinciden con las columnas SQL
        client = SSHUtil.create_client(
            server['host'], 
            server['usuario_ssh'], 
            server['password_ssh'], 
            int(server.get('puerto', 22)), 
            fingerprint=server.get('fingerprint')
        )
        
        if client:
            self.ssh_client = client
            self.sftp_client = SSHUtil.get_sftp(client)
            self.current_session = server_name
            return True, "CONNECTED"
        
        return False, "CONNECTION_FAILED"

    def list_dir(self, path):
        if not self.sftp_client:
            return []
        try:
            return self.sftp_client.listdir_attr(path if path else ".")
        except Exception as e:
            log.error(f"Error en list_dir: {e}")
            return []

    def disconnect(self):
        try:
            if self.sftp_client: self.sftp_client.close()
            if self.ssh_client: self.ssh_client.close()
        except: pass
        self.ssh_client = None
        self.sftp_client = None
        self.current_session = None