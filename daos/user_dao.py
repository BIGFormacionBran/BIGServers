import bcrypt
import uuid
from utils.db_util import DBUtil
from utils.security_util import SecurityUtil
from utils.logger_util import Logger

log = Logger.get_logger("USER_DAO")

class UserDAO:

    @classmethod
    def validate_login(cls, email, password):
        log.info(f"🔑 Intentando validar login para: {email}")
        try:
            sql = """
                SELECT u.id, u.nombre, u.password_hash, r.nombre 
                FROM USUARIO u 
                JOIN ROL r ON u.rol_id = r.id 
                WHERE u.email = %s
            """
            res = DBUtil.execute_query(sql, (email,))
            if res:
                uid, name, pw_hash, role_name = res[0]
                if bcrypt.checkpw(password.encode(), pw_hash.encode()):
                    log.info(f"✅ Login exitoso para: {name}")
                    return {"id": uid, "nombre": name, "rol": role_name}
            
            log.warning(f"🚫 Credenciales inválidas para: {email}")
            return None
        except Exception as e:
            log.error(f"💥 Error en validate_login: {e}", exc_info=True)
            return None

    @classmethod
    def generate_session_token(cls, user_id):
        """Genera un token único, lo guarda en DB y lo devuelve encriptado para el JSON."""
        raw_token = str(uuid.uuid4())
        try:
            sql = "UPDATE USUARIO SET session_token = %s WHERE id = %s"
            DBUtil.execute_query(sql, (raw_token, user_id), fetch=False)
            # Encriptamos el token antes de mandarlo al archivo local
            return SecurityUtil.encrypt(raw_token)
        except Exception as e:
            log.error(f"Error generando session_token: {e}")
            return None

    @classmethod
    def validate_session(cls, encrypted_token):
        """Valida el token del JSON local (previa desencriptación) contra la DB."""
        if not encrypted_token: return None
        try:
            raw_token = SecurityUtil.decrypt(encrypted_token)
            if not raw_token: return None

            sql = """
                SELECT u.id, u.nombre, r.nombre 
                FROM USUARIO u 
                JOIN ROL r ON u.rol_id = r.id 
                WHERE u.session_token = %s
            """
            res = DBUtil.execute_query(sql, (raw_token,))
            if res:
                uid, name, role = res[0]
                return {"id": uid, "nombre": name, "rol": role}
        except Exception as e:
            log.error(f"Token de sesión inválido o expirado: {e}")
        return None

    @classmethod
    def register_with_key(cls, nombre, email, password, plain_key):
        log.info(f"📝 Registro para: {email}")
        try:
            # Obtenemos roles que tengan key de registro
            roles = DBUtil.execute_query("SELECT id, nombre, registration_key FROM ROL WHERE registration_key IS NOT NULL")
            target_role_id = None
            
            if plain_key:
                for r_id, r_nombre, enc_key in roles:
                    # Usamos el Util para comparar la key plana con la de la DB
                    if SecurityUtil.decrypt(enc_key) == plain_key:
                        target_role_id = r_id
                        break
            
            if not target_role_id: 
                return False, "Clave de registro inválida."

            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            sql = "INSERT INTO USUARIO (nombre, email, password_hash, rol_id) VALUES (%s, %s, %s, %s)"
            DBUtil.execute_query(sql, (nombre, email, pw_hash, target_role_id), fetch=False)
            return True, "OK"
        except Exception as e:
            if "unique" in str(e).lower(): return False, "El email ya existe."
            return False, f"Error: {str(e)}"