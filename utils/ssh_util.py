import paramiko
import time
from .logger_util import Logger

log = Logger.get_logger("SSH_UTIL")

class SSHUtil:
    @staticmethod
    def create_client(host, user, password=None, port=22, fingerprint=None):
        start = time.perf_counter()
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Simplificado para brevedad
            
            client.connect(hostname=host, port=int(port), username=user, 
                           password=password, timeout=15, compress=True)
            
            # OPTIMIZACIÓN: Aumenta la velocidad de transferencia de metadatos
            transport = client.get_transport()
            transport.window_size = 2147483647 
            transport.set_keepalive(30)
            
            log.info(f"🚀 SSH Conectado a {host} en {(time.perf_counter()-start)*1000:.2f}ms")
            return client
        except Exception as e:
            log.error(f"❌ Error SSH: {e}")
            return None