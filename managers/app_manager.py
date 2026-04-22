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
        self.sftp = SFTPManager()
        self.user_data = None
        self.gui = None

    def start(self):
        config = JsonUtil.load(Paths.USER_CONFIG)
        if config and config.get("session_token"):
            log.info("🔄 Validando token de sesión...")
            user = UserDAO.validate_session(config["session_token"])
            if user:
                self.user_data = user
                log.info(f"✅ Sesión recuperada: {user['nombre']}")
                self._launch_main_gui()
                return
        
        self._launch_auth_gui()

    def _launch_auth_gui(self):
        from gui.auth_window import AuthWindow
        self.auth = AuthWindow(success_callback=self._on_auth_success)
        self.auth.run()

    def _on_auth_success(self, user, remember):
        self.user_data = user
        if remember:
            token = UserDAO.generate_session_token(user['id'])
            JsonUtil.save(Paths.USER_CONFIG, {"session_token": token})
        self._launch_main_gui()

    def _launch_main_gui(self):
        from gui.chat_window import ChatWindow
        self.gui = ChatWindow(on_submit_callback=self.handle_input)
        threading.Thread(target=self._load_initial_data, daemon=True).start()
        self.gui.run()

    def _load_initial_data(self):
        try:
            servers = ServerDAO.get_server_names() 
            if self.gui and self.gui.root:
                self.gui.root.after(0, lambda: self.gui.view.update_servers(servers))
        except Exception as e:
            log.error(f"❌ Error cargando servidores: {e}")

    def handle_input(self, text):
        if not text: return
        threading.Thread(target=self._execute_command, args=(text,), daemon=True).start()

    def _execute_command(self, text):
        parts = text.split()
        if not parts: return
        cmd = parts[0].lower()
        if cmd == "/connect" and len(parts) > 1:
            server_name = parts[1]
            self.gui.write_message("system", f"Conectando a {server_name}...")
            success, msg = self.sftp.connect(server_name)
            if success:
                self.gui.root.after(0, self.gui.view.show_file_explorer)
                log.info(f"✅ Conectado a {server_name}")
            else:
                self.gui.write_message("system", f"Error: {msg}")