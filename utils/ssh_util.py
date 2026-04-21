import paramiko
import base64
import hashlib
from utils.logger_util import Logger

log = Logger.get_logger("SSH_UTIL")

# 1. Creamos una política personalizada para validar el Fingerprint de WinSCP
class WinSCPFingerprintPolicy(paramiko.MissingHostKeyPolicy):
    def __init__(self, fingerprint_str):
        # Extraemos solo el hash final del string de WinSCP (ignora "ssh-ed25519" y "255")
        self.expected_hash = fingerprint_str.split()[-1].strip()

    def missing_host_key(self, client, hostname, key):
        # Paramiko obtiene la llave pública real del servidor en este paso
        key_blob = key.asbytes()
        
        # Calculamos el SHA-256 en el mismo formato que usa WinSCP (Base64 sin padding)
        sha256_fp = base64.b64encode(hashlib.sha256(key_blob).digest()).decode('ascii').rstrip('=')
        
        # Calculamos también el MD5 por si en el futuro pones un fingerprint en formato hexadecimal
        md5_fp = hashlib.md5(key_blob).hexdigest()
        md5_fp = ':'.join(md5_fp[i:i+2] for i in range(0, len(md5_fp), 2))
        
        # Si la huella del servidor coincide con la tuya, autorizamos la conexión
        if self.expected_hash == sha256_fp or self.expected_hash == md5_fp:
            client.get_host_keys().add(hostname, key.get_name(), key)
        else:
            log.error(f"⚠️ Fingerprint mismatch en {hostname}! Esperado: {self.expected_hash}, Servidor: {sha256_fp}")
            raise paramiko.SSHException("El Fingerprint del servidor no coincide con el configurado.")

class SSHUtil:
    @staticmethod
    def create_client(host, user, password=None, port=22, fingerprint=None):
        try:
            log.debug(f"🛠 Intentando crear cliente SSH para {user}@{host}...") # [cite: 3, 5, 7, 9]
            client = paramiko.SSHClient()
            
            # 2. Aplicamos la política correcta dependiendo de si hay fingerprint o no
            if fingerprint:
                client.set_missing_host_key_policy(WinSCPFingerprintPolicy(fingerprint))
            else:
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
            
            log.info(f"🚀 Túnel SSH establecido con {host}") # [cite: 4, 8, 10]
            return client
        except Exception as e:
            log.error(f"❌ Error crítico en SSHUtil: {e}") # 
            return None

    @staticmethod
    def get_sftp(ssh_client):
        if ssh_client:
            return ssh_client.open_sftp()
        return None