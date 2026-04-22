from utils.db_util import DBUtil
from utils.security_util import SecurityUtil

class ServerDAO:
    @classmethod
    def get_server_names(cls):
        """Obtiene solo los nombres de los servidores."""
        sql = "SELECT nombre FROM SERVIDOR ORDER BY nombre ASC"
        res = DBUtil.execute_query(sql)
        return [r[0] for r in res] if res else []

    @classmethod
    def get_details_by_name(cls, name):
        """Obtiene toda la info de conexión y desencripta la contraseña."""
        sql = "SELECT host, usuario_ssh, password_ssh, puerto, fingerprint FROM SERVIDOR WHERE nombre = %s"
        res = DBUtil.execute_query(sql, (name,))
        
        if res:
            h, u, p_encrypted, prt, f = res[0]
            # Desencriptamos la contraseña usando el Util centralizado
            p_decrypted = SecurityUtil.decrypt(p_encrypted)
            
            return {
                "host": h, 
                "user": u, 
                "password": p_decrypted, 
                "port": prt, 
                "fingerprint": f
            }
        return None