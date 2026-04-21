import os
import time
import threading
import stat
from .sftp_manager import SFTPManager
from utils.logger_util import Logger
from utils.json_util import JsonUtil
from utils.paths_util import Paths

log = Logger.get_logger("APP_MANAGER")

class AppManager:
    def __init__(self):
        from gui.chat_window import ChatWindow
        self.sftp = SFTPManager()
        # Inicializamos la GUI
        self.gui = ChatWindow(on_submit_callback=self.handle_input)
        
        # Rutas y Estados
        self.current_local_path = r"C:\Users\SERGIO\Desktop\Bran"
        if not os.path.exists(self.current_local_path):
            self.current_local_path = os.getcwd()
            
        self.current_remote_path = ""
        self.cache_file = Paths.REMOTE_CACHE
        
        # Lock para operaciones críticas de red
        self._sync_lock = threading.Lock()
        
        # Carga de caché
        self.remote_cache = {}
        if self.cache_file.exists():
            try:
                self.remote_cache = JsonUtil.load(self.cache_file) or {}
            except Exception:
                self.remote_cache = {}

        # Actualizar servidores en el combo
        self._refresh_gui_servers()

    def _write_log(self, role, text):
        """
        USA EL MÉTODO CORRECTO: write_message (definido en tu chat_window.py)
        """
        try:
            # Según tu chat_window.py, el método es write_message
            self.gui.write_message(role, text)
        except Exception as e:
            log.error(f"Error fatal al escribir en UI: {e}")

    def _refresh_gui_servers(self):
        server_names = [s["name"] for s in self.sftp.servers]
        # Nos aseguramos de que esto corra en el hilo de la UI
        self.gui.root.after(0, lambda: self.gui.view.update_servers(server_names))

    def handle_input(self, text):
        if not text: return
        msg = text.strip()
        
        if msg.startswith("/connect"):
            server_name = msg.split(" ", 1)[1] if " " in msg else ""
            self._do_connect(server_name)
        elif msg.startswith("/cd_remote"):
            target = msg.split(" ", 1)[1] if " " in msg else ""
            self._change_remote_dir(target)
        elif msg.startswith("/cd_local"):
            target = msg.split(" ", 1)[1] if " " in msg else ""
            self._change_local_dir(target)
        else:
            self._write_log("user", msg)

    def _do_connect(self, name):
        if not name:
            self._write_log("bot", "⚠️ Especifica un servidor.")
            return

        self._write_log("bot", f"🚀 Conectando a {name}...")
        
        def run_connect():
            success, msg = self.sftp.connect(name)
            if success:
                self.current_remote_path = "/"
                self.gui.root.after(0, self._after_connect_success)
            else:
                self.gui.root.after(0, lambda: self._write_log("bot", f"❌ Error: {msg}"))
        
        threading.Thread(target=run_connect, daemon=True).start()

    def _after_connect_success(self):
        # Primero activamos la vista de explorador
        self.gui.view.show_file_explorer()
        # Luego refrescamos datos
        self._refresh_local_view()
        self._refresh_remote_view()
        self._write_log("bot", "✨ Sistema listo.")

    def _refresh_local_view(self):
        try:
            data = []
            with os.scandir(self.current_local_path) as it:
                for entry in it:
                    if entry.name.startswith(".") and entry.name != ".env": continue
                    is_dir = entry.is_dir()
                    size = f"{entry.stat().st_size // 1024}KB" if not is_dir else ""
                    data.append((entry.name, "DIR" if is_dir else "FILE", size))
            
            data.sort(key=lambda x: (x[1] != "DIR", x[0].lower()))
            self.gui.view.local_exp.refresh(self.current_local_path, data)
        except Exception as e:
            log.error(f"Error local: {e}")

    def _refresh_remote_view(self):
        path = self.current_remote_path
        # Mostrar caché si existe
        if path in self.remote_cache:
            self.gui.view.remote_exp.refresh(path, self.remote_cache[path])
        # Actualizar en segundo plano
        threading.Thread(target=self._worker_sync_remote, args=(path,), daemon=True).start()

    def _worker_sync_remote(self, path_to_sync):
        if not self.sftp.sftp_client or self._sync_lock.locked(): return
        with self._sync_lock:
            try:
                items = self.sftp.list_dir(path_to_sync)
                new_data = []
                for item in items:
                    if item.filename in [".", ".."]: continue
                    is_dir = stat.S_ISDIR(item.st_mode)
                    size = "" if is_dir else f"{item.st_size // 1024}KB"
                    new_data.append((item.filename, "DIR" if is_dir else "FILE", size))

                new_data.sort(key=lambda x: (x[1] != "DIR", x[0].lower()))
                self.remote_cache[path_to_sync] = new_data
                JsonUtil.save(self.cache_file, self.remote_cache)

                if self.current_remote_path == path_to_sync:
                    self.gui.root.after(0, lambda: self.gui.view.remote_exp.refresh(path_to_sync, new_data))
            except Exception as e:
                log.error(f"Error sync: {e}")

    def start(self): 
        self.gui.run()