import paramiko
from .logger_util import Logger

log = Logger.get_logger("SSH_UTIL")

class SSHUtil:
    @staticmethod
    def create_client(host, user, pwd, port=22):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=host, port=port, username=user, password=pwd, timeout=10)
            
            # Optimización de transporte para SFTP rápido
            transport = client.get_transport()
            transport.window_size = 2147483647 
            transport.set_keepalive(20)
            
            return client
        except Exception as e:
            log.error(f"Fallo SSH: {e}")
            return None