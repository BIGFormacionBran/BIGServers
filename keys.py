import os
from cryptography.fernet import Fernet
from utils.db_util import DBUtil

def run_db_update():
    # GitHub Actions le pasará esto al sistema
    key = os.getenv("ENCRYPTION_KEY")
    
    if not key:
        print("❌ Error: No hay ENCRYPTION_KEY")
        return

    cipher = Fernet(key.encode())
    
    # Datos a encriptar
    keys_to_set = {
        "admin": "ADMIN_BIGSERVERS_2026",
        "developer": "DEVELOPER_BIGSERVERS_2026"
    }

    for role, plain_text in keys_to_set.items():
        encrypted = cipher.encrypt(plain_text.encode()).decode()
        # Usamos tu método _execute de db_util.py
        sql = "UPDATE ROL SET registration_key = %s WHERE nombre = %s"
        DBUtil._execute(sql, (encrypted, role))
        print(f"✅ Rol '{role}' actualizado.")

if __name__ == "__main__":
    run_db_update()