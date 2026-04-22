import os
from cryptography.fernet import Fernet
from utils.db_util import DBUtil # Esto funciona si el PYTHONPATH incluye la raíz

def run_db_update():
    key = os.getenv("ENCRYPTION_KEY")
    
    if not key:
        print("❌ Error: No hay ENCRYPTION_KEY configurada en los Secrets de GitHub")
        return

    try:
        cipher = Fernet(key.encode())
        
        keys_to_set = {
            "admin": "ADMIN_BIGSERVERS_2026",
            "developer": "DEVELOPER_BIGSERVERS_2026"
        }

        for role, plain_text in keys_to_set.items():
            encrypted = cipher.encrypt(plain_text.encode()).decode()
            
            # CORRECCIÓN: El método correcto es execute_query y fetch=False para UPDATES
            sql = "UPDATE ROL SET registration_key = %s WHERE nombre = %s"
            DBUtil.execute_query(sql, (encrypted, role), fetch=False)
            print(f"✅ Rol '{role}' actualizado correctamente.")
            
    except Exception as e:
        print(f"❌ Error durante la actualización: {e}")

if __name__ == "__main__":
    run_db_update()