from utils.ssh_util import SSHUtil
from daos.server_dao import ServerDAO # <-- CORREGIDO
from utils.logger_util import Logger

log = Logger.get_logger("SFTP_MANAGER")

class SFTPManager:
    def __init__(self):
        self.ssh = None
        self.sftp = None

    def connect(self, server_name):
        log.info(f"🌐 Iniciando conexión SFTP a: {server_name}")
        # Obtenemos los datos desde el DAO
        details = ServerDAO.get_details_by_name(server_name)
        
        if not details: 
            return False, "Servidor no encontrado en la base de datos"
        
        self.disconnect()
        
        # SSHUtil ya maneja los logs internos
        self.ssh = SSHUtil.create_client(
            host=details['host'], 
            user=details['user'], 
            password=details['password'], 
            port=details['port']
        )
        
        if self.ssh:
            try:
                self.sftp = self.ssh.open_sftp()
                log.info(f"✅ Canal SFTP abierto con éxito para {server_name}")
                return True, "OK"
            except Exception as e:
                log.error(f"❌ Error al abrir canal SFTP: {e}")
                return False, f"Fallo SFTP: {str(e)}"
        
        return False, "Error de conexión SSH"

    def list_dir(self, path):
        if not self.sftp: return []
        try: 
            return self.sftp.listdir_attr(path or ".")
        except Exception as e:
            log.error(f"Error listando directorio {path}: {e}")
            return []

    def disconnect(self):
        try:
            if self.sftp: self.sftp.close()
            if self.ssh: self.ssh.close()
            log.debug("🔌 SFTP desconectado")
        except: pass