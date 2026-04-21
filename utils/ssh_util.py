import paramiko
import base64
import binascii
from utils.logger_util import Logger

log = Logger.get_logger("SSH_UTIL")

class SSHUtil:
    @staticmethod
    def create_client(host, user, password=None, port=22, fingerprint=None):
        try:
            log.debug(f"🛠 Intentando crear cliente SSH para {user}@{host}...") # [cite: 3, 5]
            client = paramiko.SSHClient()
            
            if fingerprint:
                # El fingerprint de WinSCP es: "ssh-ed25519 255 base64..."
                # 1. Separamos por espacios
                parts = fingerprint.strip().split()
                key_type = parts[0]
                
                # 2. El hash real SIEMPRE es la parte más larga y suele estar al final.
                # Al usar parts[-1], evitamos que el "255" interfiera.
                raw_b64 = parts[-1].strip() 
                
                # 3. Forzamos el padding correcto para Base64 si falta (evita el error 'Incorrect padding')
                missing_padding = len(raw_b64) % 4
                if missing_padding:
                    raw_b64 += '=' * (4 - missing_padding)
                
                # 4. Decodificación robusta
                key_binary = base64.b64decode(raw_b64)
                
                if "ed25519" in key_type.lower():
                    key = paramiko.Ed25519Key(data=key_binary)
                elif "rsa" in key_type.lower():
                    key = paramiko.RSAKey(data=key_binary)
                else:
                    # Fallback para otros tipos de llave
                    key = paramiko.PKey(data=key_binary)
                
                client.get_host_keys().add(host, key_type, key)
                client.set_missing_host_key_policy(paramiko.RejectPolicy())
            else:
                # Mantenemos la política automática para Experto, Dedicado y Retodigital
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_params = {
                "hostname": host,
                "port": int(port),
                "username": user,
                "password": password,
                "timeout": 15,
                "compress": True,
                "look_for_keys": False,
                "allow_agent": False
            }
            
            client.connect(**connect_params)
            
            transport = client.get_transport()
            if transport:
                transport.window_size = 2147483647
                transport.set_keepalive(30)
            
            log.info(f"🚀 Túnel SSH establecido con {host}") # 
            return client
        except Exception as e:
            log.error(f"❌ Error crítico en SSHUtil: {e}") # 
            return None

    @staticmethod
    def get_sftp(ssh_client):
        if ssh_client:
            return ssh_client.open_sftp()
        return None