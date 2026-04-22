import threading
import time
from .sftp_manager import SFTPManager
from utils.logger_util import Logger
from utils.db_util import DBUtil

log = Logger.get_logger("APP_MANAGER")

class AppManager:
    def __init__(self):
        from gui.chat_window import ChatWindow
        self.sftp = SFTPManager()
        self.gui = ChatWindow(on_submit_callback=self.handle_input)
        self._sync_lock = threading.Lock()

    def start(self):
        # Carga inicial de servidores sin bloquear el hilo principal (GUI)
        threading.Thread(target=self._load_initial_data, daemon=True).start()
        log.info("🖥️ Interfaz de usuario lanzada")
        self.gui.run()

    def _load_initial_data(self):
        start = time.perf_counter()
        servers = DBUtil.get_server_list()
        log.info(f"📂 Lista de servidores cargada en {(time.perf_counter()-start)*1000:.2f}ms")
        self.gui.root.after(0, lambda: self.gui.view.update_servers(servers))

    def handle_input(self, text):
        if not text: return
        # Procesar comandos en hilos separados para mantener la GUI fluida
        threading.Thread(target=self._execute_command, args=(text,), daemon=True).start()

    def _execute_command(self, text):
        parts = text.split()
        cmd = parts[0].lower()
        
        if cmd == "/connect" and len(parts) > 1:
            server = parts[1]
            self.gui.write_message("system", f"Conectando a {server}...")
            success, msg = self.sftp.connect(server)
            if success:
                self.gui.root.after(0, self.gui.view.show_file_explorer)
                log.info(f"✅ Conexión establecida con {server}")
            else:
                self.gui.write_message("system", f"Error: {msg}")