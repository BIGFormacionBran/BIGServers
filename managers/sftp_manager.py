from utils.ssh_util import SSHUtil
from utils.db_util import DBUtil

class SFTPManager:
    def __init__(self):
        self.ssh = None
        self.sftp = None

    def connect(self, server_name):
        details = DBUtil.get_server_details(server_name)
        if not details: return False, "Servidor no encontrado"
        
        self.disconnect()
        self.ssh = SSHUtil.create_client(details['host'], details['user'], details['password'], details['port'])
        
        if self.ssh:
            self.sftp = self.ssh.open_sftp()
            return True, "OK"
        return False, "Error de conexión"

    def list_dir(self, path):
        if not self.sftp: return []
        try: return self.sftp.listdir_attr(path or ".")
        except: return []

    def disconnect(self):
        if self.sftp: self.sftp.close()
        if self.ssh: self.ssh.close()