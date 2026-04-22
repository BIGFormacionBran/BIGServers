import threading
import time
from .sftp_manager import SFTPManager
from utils.logger_util import Logger
from utils.json_util import JsonUtil
from utils.paths_util import Paths
from daos.server_dao import ServerDAO 
from daos.user_dao import UserDAO

log = Logger.get_logger("APP_MANAGER")

class AppManager:
    def __init__(self):
        from gui.main_window import MainWindow
        # Creamos la ventana única que contendrá todo
        self.root = MainWindow(self)
        self.sftp = SFTPManager()
        self.user_data = None

    def start(self):
        """Punto de entrada: decide qué vista cargar en la ventana principal."""
        config = JsonUtil.load(Paths.USER_CONFIG)
        
        if config and config.get("session_token"):
            log.info("🔄 Validando token de sesión...")
            user = UserDAO.validate_session(config["session_token"])
            if user:
                self.user_data = user
                log.info(f"✅ Sesión recuperada: {user['nombre']}")
                self.show_main_chat()
                self.root.mainloop()
                return
        
        self.show_login()
        self.root.mainloop()

    def show_login(self):
        """Carga la vista de Login en la ventana actual."""
        from gui.auth_window import AuthView
        self.root.show_view(AuthView, success_callback=self._on_auth_success)

    def show_main_chat(self):
        """Carga la vista de Chat en la ventana actual."""
        from gui.views.chat_view import ChatView
        self.root.show_view(ChatView, on_submit_callback=self.handle_input)
        # Carga de datos en segundo plano
        threading.Thread(target=self._load_initial_data, daemon=True).start()

    def _on_auth_success(self, user, remember):
        """Callback tras login exitoso."""
        self.user_data = user
        if remember:
            token = UserDAO.generate_session_token(user['id'])
            JsonUtil.save(Paths.USER_CONFIG, {"session_token": token})
        self.show_main_chat()

    def _load_initial_data(self):
        """Carga la lista de servidores para la UI."""
        try:
            servers = ServerDAO.get_server_names() 
            # Actualizamos la vista actual si es el chat
            if hasattr(self.root.current_view, 'update_servers'):
                self.root.after(0, lambda: self.root.current_view.update_servers(servers))
        except Exception as e:
            log.error(f"❌ Error cargando servidores: {e}")

    def handle_input(self, text):
        """Maneja el input del chat sin bloquear la UI."""
        if not text: return
        threading.Thread(target=self._execute_command, args=(text,), daemon=True).start()

    def _execute_command(self, text):
        """Lógica de comandos SFTP."""
        parts = text.split()
        if not parts: return
        cmd = parts[0].lower()
        
        if cmd == "/connect" and len(parts) > 1:
            server_name = parts[1]
            self.root.current_view.write_message("system", f"Conectando a {server_name}...")
            
            success, msg = self.sftp.connect(server_name)
            
            if success:
                self.root.after(0, self.root.current_view.show_file_explorer)
                log.info(f"✅ Conectado a {server_name}")
            else:
                self.root.current_view.write_message("system", f"Error: {msg}")