import threading
import stat
from .sftp_manager import SFTPManager
from utils.json_util import JsonUtil
from utils.paths_util import Paths
from utils.db_util import DBUtil

class AppManager:
    def __init__(self):
        from gui.chat_window import ChatWindow
        self.sftp = SFTPManager()
        self.gui = ChatWindow(on_submit_callback=self.handle_input)
        self.remote_cache = JsonUtil.load(Paths.REMOTE_CACHE) or {}

    def start(self):
        # Carga inicial de DB en hilo separado
        threading.Thread(target=self._init_db, daemon=True).start()
        self.gui.run()

    def _init_db(self):
        servers = DBUtil.get_server_list()
        self.gui.root.after(0, lambda: self.gui.view.update_servers(servers))

    def handle_input(self, text):
        parts = text.split()
        if not parts: return
        cmd = parts[0].lower()

        if cmd == "/connect" and len(parts) > 1:
            threading.Thread(target=self._connect_task, args=(parts[1],), daemon=True).start()

    def _connect_task(self, server):
        self.gui.write_message("system", f"Conectando a {server}...")
        success, res = self.sftp.connect(server)
        if success:
            self.gui.write_message("bot", f"Conectado a {server}")
            self.gui.root.after(0, self.gui.view.show_file_explorer)
        else:
            self.gui.write_message("system", f"Error: {res}")