import os
import time
from dotenv import load_dotenv
from utils.ssh_util import SSHUtil
from utils.db_util import DBUtil
from utils.paths_util import Paths
from utils.logger_util import Logger

log = Logger.get_logger("SFTP_MANAGER")

class SFTPManager:
    def __init__(self):
        load_dotenv(Paths.ENV_FILE)
        self.ssh_client = None
        self.sftp_client = None
        self.current_session = None

    def connect(self, server_name):
        log.info(f"Intentando conectar a {server_name}")
        t0 = time.time()
        server = DBUtil.get_server_details(server_name)
        
        if not server:
            log.error(f"Servidor {server_name} no encontrado en DB")
            return False, "Servidor no encontrado."

        if self.current_session == server_name and self.ssh_client:
            return True, "ALREADY_CONNECTED"

        self.disconnect()

        log.info(f"Estableciendo túnel SSH para {server['host']}...")
        client = SSHUtil.create_client(
            server['host'], 
            server['user'], 
            server['password'], 
            int(server.get('port', 22)), 
            fingerprint=server.get('fingerprint')
        )
        
        if client:
            self.ssh_client = client
            self.sftp_client = SSHUtil.get_sftp(client)
            self.current_session = server_name
            log.info(f"Conexión completa en {time.time()-t0:.4f}s")
            return True, "CONNECTED"
        
        log.error("Fallo al crear cliente SSH")
        return False, "CONNECTION_FAILED"

    def list_dir(self, path):
        if not self.sftp_client: return []
        t0 = time.time()
        try:
            res = self.sftp_client.listdir_attr(path if path else ".")
            log.info(f"ListDir remoto '{path}' en {time.time()-t0:.4f}s")
            return res
        except Exception as e:
            log.error(f"Error list_dir remoto: {e}")
            return []

    def disconnect(self):
        if self.current_session:
            log.info(f"Desconectando sesión: {self.current_session}")
        try:
            if self.sftp_client: self.sftp_client.close()
            if self.ssh_client: self.ssh_client.close()
        except Exception as e:
            log.error(f"Error al desconectar: {e}")
        self.ssh_client = None
        self.sftp_client = None
        self.current_session = None