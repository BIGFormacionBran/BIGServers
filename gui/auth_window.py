import tkinter as tk
from tkinter import messagebox
from .views.auth_view import AuthView
from daos.user_dao import UserDAO
from utils.logger_util import Logger

log = Logger.get_logger("AUTH_WINDOW")

class AuthWindow:
    def __init__(self, success_callback):
        self.root = tk.Tk()
        self.root.title("BIGServers - Autenticación")
        self.root.geometry("400x550")
        self.on_success = success_callback
        self.view = AuthView(self.root, self)

    def login_action(self, email, password, remember):
        log.info(f"🔑 Intento de login para: {email} (Recordar: {remember})")
        if not email or not password:
            self.view.show_error("Email y contraseña obligatorios.")
            return

        user = UserDAO.validate_login(email, password)
        if user:
            log.info(f"✅ Login exitoso: {user['nombre']} [{user['rol']}]")
            self.root.destroy()
            self.on_success(user, remember)
        else:
            log.warning(f"❌ Login fallido para: {email}")
            self.view.show_error("Credenciales incorrectas.")

    def register_action(self, nombre, email, password, key, remember):
        log.info(f"📝 Intento de registro: {nombre} <{email}>")
        if not all([nombre, email, password]):
            log.warning("⚠️ Intento de registro con campos incompletos")
            self.view.show_error("Todos los campos marcados son obligatorios.")
            return

        success, msg = UserDAO.register_with_key(nombre, email, password, key)
        
        if success:
            log.info(f"✨ Usuario creado con éxito: {nombre}")
            # Si el registro es exitoso, validamos login automáticamente
            user = UserDAO.validate_login(email, password)
            if user:
                self.root.destroy()
                self.on_success(user, remember)
        else:
            log.error(f"❌ Error en registro: {msg}")
            self.view.show_error(msg)

    def run(self):
        self.root.mainloop()