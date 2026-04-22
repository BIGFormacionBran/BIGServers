from utils.ssh_util import SSHUtil
from daos.server_dao import ServerDAO
from utils.logger_util import Logger

log = Logger.get_logger("SFTP_MANAGER")

class SFTPManager:
    def __init__(self):
        self.ssh = None
        self.sftp = None

    def connect(self, server_name):
        log.info(f"🌐 Iniciando conexión SFTP a: {server_name}")
        details = ServerDAO.get_details_by_name(server_name)
        
        if not details: 
            return False, "Servidor no encontrado en la base de datos"
        
        self.disconnect()
        
        try:
            # Aseguramos que el puerto sea entero para Paramiko
            puerto = int(details.get('port', 22))
            
            self.ssh = SSHUtil.create_client(
                host=details['host'], 
                user=details['user'], 
                password=details['password'], 
                port=puerto
            )
            
            if self.ssh:
                self.sftp = self.ssh.open_sftp()
                log.info(f"✅ Canal SFTP abierto con éxito para {server_name}")
                return True, "OK"
            else:
                return False, "Error en SSHUtil: No se pudo crear el cliente"
                
        except Exception as e:
            log.error(f"❌ Error crítico en conexión SFTP: {e}", exc_info=True)
            return False, f"Error: {str(e)}"

    def list_dir(self, path):
        if not self.sftp: return []
        try: 
            # listdir_attr es más lento pero da info de iconos/permisos
            return self.sftp.listdir_attr(path or ".")
        except Exception as e:
            log.error(f"Error listando directorio {path}: {e}")
            return []

    def disconnect(self):
        """Cierre seguro de canales y cliente."""
        try:
            if self.sftp:
                self.sftp.close()
                self.sftp = None
            if self.ssh:
                self.ssh.close()
                self.ssh = None
            log.debug("🔌 SFTP y SSH desconectados")
        except Exception as e:
            log.debug(f"Aviso en desconexión: {e}")