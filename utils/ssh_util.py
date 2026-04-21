import paramiko
import base64
import hashlib
import time
from .logger_util import Logger

log = Logger.get_logger("SSH_UTIL")

class WinSCPFingerprintPolicy(paramiko.MissingHostKeyPolicy):
    def __init__(self, fingerprint_str):
        self.expected_hash = fingerprint_str.split()[-1].strip()

    def missing_host_key(self, client, hostname, key):
        key_blob = key.asbytes()
        sha256_fp = base64.b64encode(hashlib.sha256(key_blob).digest()).decode('ascii').rstrip('=')
        if self.expected_hash == sha256_fp:
            return
        raise paramiko.SSHException(f"Huella no coincide: {sha256_fp}")

class SSHUtil:
    @staticmethod
    def create_client(host, user, password=None, port=22, fingerprint=None):
        start = time.perf_counter()
        try:
            client = paramiko.SSHClient()
            if fingerprint:
                client.set_missing_host_key_policy(WinSCPFingerprintPolicy(fingerprint))
            else:
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            client.connect(
                hostname=host, port=int(port), username=user, password=password,
                timeout=15, compress=True, look_for_keys=False, allow_agent=False
            )
            
            trans = client.get_transport()
            trans.window_size = 2147483647
            trans.set_keepalive(30)
            
            log.info(f"SSH conectado a {host} en {(time.perf_counter()-start)*1000:.2f}ms")
            return client
        except Exception as e:
            log.error(f"Fallo SSH a {host}: {e}")
            return None