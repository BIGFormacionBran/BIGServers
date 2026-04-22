import os
import bcrypt
from utils.db_util import DBUtil
from cryptography.fernet import Fernet
from utils.logger_util import Logger

# Configuramos el logger para trazabilidad total
log = Logger.get_logger("USER_DAO")

class UserDAO:
    # La key debe estar en el .env y cargarse correctamente
    _key = os.getenv("ENCRYPTION_KEY")
    _cipher = Fernet(_key.encode()) if _key else None

    @classmethod
    def validate_login(cls, email, password):
        """Valida las credenciales del usuario."""
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
                # Verificación de hash con bcrypt
                if bcrypt.checkpw(password.encode(), pw_hash.encode()):
                    log.info(f"✅ Login exitoso para usuario: {name} (Rol: {role_name})")
                    return {"id": uid, "nombre": name, "rol": role_name}
                else:
                    log.warning(f"⚠️ Contraseña incorrecta para el email: {email}")
            else:
                log.warning(f"🚫 No se encontró ningún usuario con el email: {email}")
                
            return None
        except Exception as e:
            log.error(f"💥 Error crítico en validate_login: {e}", exc_info=True)
            return None

    @classmethod
    def register_with_key(cls, nombre, email, password, plain_key):
        """Valida la clave de rol e inserta el usuario con trazabilidad de errores."""
        log.info(f"📝 Iniciando proceso de registro para: {email}")
        
        if not cls._cipher:
            log.critical("‼️ Error de configuración: ENCRYPTION_KEY no encontrada o no válida en el .env")
            return False, "Error interno: Llave de encriptación no configurada."

        # 1. Buscar el rol correspondiente a la key proporcionada
        log.debug("🔍 Buscando roles disponibles en la base de datos...")
        try:
            roles = DBUtil.execute_query("SELECT id, nombre, registration_key FROM ROL WHERE registration_key IS NOT NULL")
            target_role_id = None
            
            if plain_key:
                log.debug(f"Verificando clave proporcionada contra {len(roles)} roles...")
                for r_id, r_nombre, enc_key in roles:
                    try:
                        decrypted_key = cls._cipher.decrypt(enc_key.encode()).decode()
                        if decrypted_key == plain_key:
                            target_role_id = r_id
                            log.info(f"🎯 Clave válida detectada para el Rol: {r_nombre} (ID: {r_id})")
                            break
                    except Exception:
                        # Si falla la desencriptación de uno, seguimos con el siguiente
                        continue
            
            if not target_role_id:
                log.warning(f"🚫 La clave de registro '{plain_key}' no coincide con ningún rol activo.")
                return False, "La clave de registro no es válida."

            # 2. Hashear password y guardar
            log.debug("🔐 Generando hash de seguridad para la contraseña...")
            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            
            sql = "INSERT INTO USUARIO (nombre, email, password_hash, rol_id) VALUES (%s, %s, %s, %s)"
            log.debug(f"💾 Insertando usuario {nombre} en la base de datos...")
            
            DBUtil.execute_query(sql, (nombre, email, pw_hash, target_role_id), fetch=False)
            
            log.info(f"✨ Usuario {nombre} ({email}) registrado exitosamente.")
            return True, "OK"

        except Exception as e:
            error_msg = str(e)
            if "duplicate key" in error_msg.lower() or "unique constraint" in error_msg.lower():
                log.warning(f"⚠️ Intento de registro duplicado para el email: {email}")
                return False, "Este correo electrónico ya está registrado."
            
            log.error(f"💥 Fallo inesperado en register_with_key: {error_msg}", exc_info=True)
            return False, f"Error al crear usuario: {error_msg}"