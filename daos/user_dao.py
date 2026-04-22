import os
import bcrypt
from utils.db_util import DBUtil
from cryptography.fernet import Fernet

class UserDAO:
    # La key debe estar en el .env
    _key = os.getenv("ENCRYPTION_KEY")
    _cipher = Fernet(_key.encode()) if _key else None

    @classmethod
    def validate_login(cls, email, password):
        sql = """
            SELECT u.id, u.nombre, u.password_hash, r.nombre 
            FROM USUARIO u 
            JOIN ROL r ON u.rol_id = r.id 
            WHERE u.email = %s
        """
        res = DBUtil.execute_query(sql, (email,))
        if res:
            uid, name, pw_hash, role_name = res[0]
            # Verificación de hash con bcrypt
            if bcrypt.checkpw(password.encode(), pw_hash.encode()):
                return {"id": uid, "nombre": name, "rol": role_name}
        return None

    @classmethod
    def register_with_key(cls, nombre, email, password, plain_key):
        """Valida la clave de rol e inserta el usuario."""
        if not cls._cipher:
            return False, "Error interno: Llave de encriptación no configurada."

        # 1. Buscar el rol correspondiente a la key proporcionada
        roles = DBUtil.execute_query("SELECT id, registration_key FROM ROL WHERE registration_key IS NOT NULL")
        target_role_id = None
        
        if plain_key:
            for r_id, enc_key in roles:
                try:
                    decrypted_key = cls._cipher.decrypt(enc_key.encode()).decode()
                    if decrypted_key == plain_key:
                        target_role_id = r_id
                        break
                except:
                    continue
        
        # Si no hay key o no es válida, podríamos asignar un rol por defecto o denegar
        if not target_role_id:
            return False, "La clave de registro no es válida."

        # 2. Hashear password y guardar
        try:
            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            sql = "INSERT INTO USUARIO (nombre, email, password_hash, rol_id) VALUES (%s, %s, %s, %s)"
            DBUtil.execute_query(sql, (nombre, email, pw_hash, target_role_id), fetch=False)
            return True, "OK"
        except Exception as e:
            return False, f"Error al crear usuario: {str(e)}"