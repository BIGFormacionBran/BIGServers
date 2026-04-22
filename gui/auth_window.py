import tkinter as tk
from .views.auth_view import AuthView
from daos.user_dao import UserDAO

class AuthWindow:
    def __init__(self, success_callback):
        self.root = tk.Tk()
        self.root.title("BIGServers - Autenticación")
        self.root.geometry("400x550")
        
        self.on_success = success_callback
        # El controlador (self) se pasa a la vista
        self.view = AuthView(self.root, self)

    def login_action(self, email, password, remember):
        """Gestiona el intento de inicio de sesión."""
        if not email or not password:
            self.view.show_error("Por favor, rellena todos los campos.")
            return

        user = UserDAO.validate_login(email, password)
        if user:
            self.root.destroy()
            # Pasamos el usuario y la preferencia de guardado al AppManager
            self.on_success(user, remember)
        else:
            self.view.show_error("Credenciales incorrectas.")

    def register_action(self, nombre, email, password, key):
        """Gestiona el registro de nuevos usuarios."""
        if not all([nombre, email, password]):
            self.view.show_error("Nombre, email y clave son obligatorios.")
            return

        success, msg = UserDAO.register_with_key(nombre, email, password, key)
        if success:
            self.view.show_info("Registro exitoso. Ya puedes iniciar sesión.")
            self.view._build_login_ui()
        else:
            self.view.show_error(msg)

    def run(self):
        self.root.mainloop()