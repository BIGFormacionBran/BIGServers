import os
import time
import threading
import stat
from .sftp_manager import SFTPManager
from utils.logger_util import Logger
from utils.json_util import JsonUtil
from utils.paths_util import Paths
from utils.db_util import DBUtil

log = Logger.get_logger("APP_MANAGER")

class AppManager:
    def __init__(self):
        log.info("Iniciando AppManager...")
        from gui.chat_window import ChatWindow
        self.sftp = SFTPManager()
        self.gui = ChatWindow(on_submit_callback=self.handle_input)
        
        self.current_remote_path = ""
        self._sync_lock = threading.Lock()
        self.remote_cache = JsonUtil.load(Paths.REMOTE_CACHE) or {}

    def start(self):
        # Carga asíncrona inicial de servidores
        threading.Thread(target=self._initial_load, daemon=True).start()
        self.gui.run()

    def _initial_load(self):
        start = time.perf_counter()
        servers = DBUtil.get_server_list()
        log.info(f"Lista de servidores cargada en {(time.perf_counter()-start)*1000:.2f}ms")
        self.gui.root.after(0, lambda: self.gui.view.update_servers(servers))

    def handle_input(self, text):
        # Evitamos bloquear la GUI lanzando cada comando en un hilo
        threading.Thread(target=self._process_command, args=(text,), daemon=True).start()

    def _process_command(self, text):
        parts = text.split()
        if not parts: return
        cmd = parts[0].lower()

        if cmd == "/connect" and len(parts) > 1:
            self._connect_to_server(parts[1])
        elif cmd == "/ls_remote":
            self._sync_remote(self.current_remote_path)

    def _connect_to_server(self, server_name):
        self.gui.write_message("system", f"Conectando a {server_name}...")
        success, status = self.sftp.connect(server_name)
        
        if success:
            self.gui.write_message("bot", f"Conexión exitosa a {server_name}.")
            self.gui.root.after(0, self.gui.view.show_file_explorer)
            self._sync_remote("")
        else:
            self.gui.write_message("system", f"Fallo: {status}")

    def _sync_remote(self, path):
        if not self.sftp.sftp_client: return
        
        def task():
            with self._sync_lock:
                start = time.perf_counter()
                log.info(f"Sincronizando {path}...")
                items = self.sftp.list_dir(path)
                
                new_data = []
                for item in items:
                    if item.filename in [".", ".."]: continue
                    is_dir = stat.S_ISDIR(item.st_mode)
                    size = "" if is_dir else f"{item.st_size // 1024}KB"
                    new_data.append((item.filename, "DIR" if is_dir else "FILE", size))

                new_data.sort(key=lambda x: (x[1] != "DIR", x[0].lower()))
                self.remote_cache[path] = new_data
                JsonUtil.save(Paths.REMOTE_CACHE, self.remote_cache)
                
                log.info(f"Sincronización remota finalizada en {(time.perf_counter()-start)*1000:.2f}ms")
                self.gui.root.after(0, lambda: self.gui.view.remote_exp.refresh(path, new_data))

        threading.Thread(target=task, daemon=True).start()