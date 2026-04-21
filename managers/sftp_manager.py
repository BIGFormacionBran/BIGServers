import os
from dotenv import load_dotenv
from registries.server_registry import ServerRegistry
from utils.ssh_util import SSHUtil
from utils.paths_util import Paths
from utils.logger_util import Logger

log = Logger.get_logger("SFTP_MANAGER")

class SFTPManager:
    def __init__(self):
        # Cargar variables del .env
        load_dotenv(Paths.ROOT / ".env")
        
        self.ssh_client = None
        self.sftp_client = None
        self.current_session = None
        
        # Cargar inventario de servidores
        self.servers = ServerRegistry.SERVERS

    def connect(self, server_name):
        """Conexión persistente usando SSHUtil."""
        server = ServerRegistry.get_server(server_name)
        if not server:
            return False, "Servidor no encontrado en configuración."

        # Obtener pass del .env
        pass_key = f"SERVER_{server_name.upper()}_PASS"
        password = os.getenv(pass_key)

        if not password:
            return False, f"Falta contraseña en .env ({pass_key})"

        # Si ya estamos conectados al mismo, no hacemos nada
        if self.current_session == server_name and self.ssh_client:
            return True, "ALREADY_CONNECTED"

        self.disconnect()

        # Usar el Util para el vuelo
        client = SSHUtil.create_client(server['host'], server['user'], password, int(server.get('port', 22)), fingerprint=server.get('fingerprint'))
        
        if client:
            self.ssh_client = client
            self.sftp_client = SSHUtil.get_sftp(client)
            self.current_session = server_name
            return True, "CONNECTED"
        
        return False, "CONNECTION_FAILED"

    def list_dir(self, path):
        """Ejecución de comando sobre sesión caliente."""
        if not self.sftp_client:
            return []
        try:
            # listdir_attr nos da metadata (tamaño, tipo) en una sola petición
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