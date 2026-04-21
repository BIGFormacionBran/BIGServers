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
        t0 = time.time()
        log.info("Iniciando AppManager...")
        from gui.chat_window import ChatWindow
        self.sftp = SFTPManager()
        self.gui = ChatWindow(on_submit_callback=self.handle_input)
        
        self.current_local_path = r"C:\Users\SERGIO\Desktop\Bran"
        if not os.path.exists(self.current_local_path):
            self.current_local_path = os.getcwd()
            
        self.current_remote_path = ""
        self.cache_file = Paths.REMOTE_CACHE
        self._sync_lock = threading.Lock()
        
        self.remote_cache = {}
        if self.cache_file.exists():
            try:
                self.remote_cache = JsonUtil.load(self.cache_file) or {}
                log.info(f"Caché cargada: {len(self.remote_cache)} entradas.")
            except Exception as e:
                log.error(f"Error cargando caché: {e}")

        self._refresh_gui_servers()
        log.info(f"AppManager inicializado en {time.time() - t0:.4f}s")

    def _write_log(self, role, text):
        try:
            log.info(f"Escribiendo en UI ({role}): {text[:50]}...")
            self.gui.write_message(role, text)
        except Exception as e:
            log.error(f"Error escribiendo en UI: {e}")

    def _refresh_gui_servers(self):
        t0 = time.time()
        try:
            server_names = DBUtil.get_server_list()
            log.info(f"Servidores obtenidos de DB: {server_names} ({time.time()-t0:.4f}s)")
            self.gui.root.after(0, lambda: self.gui.view.update_servers(server_names))
        except Exception as e:
            log.error(f"Error refrescando servidores: {e}")
            self._write_log("system", "❌ Error al conectar con Neon DB")

    def handle_input(self, text):
        if not text: return
        msg = text.strip()
        log.info(f"Procesando entrada: {msg}")
        
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

        log.info(f"Iniciando hilo de conexión a {name}")
        self._write_log("bot", f"🚀 Conectando a {name}...")
        
        def run_connect():
            t_start = time.time()
            success, result_msg = self.sftp.connect(name)
            if success:
                log.info(f"Conectado a {name} en {time.time()-t_start:.4f}s")
                self.current_remote_path = "." 
                self.gui.root.after(0, self._after_connect_success)
            else:
                log.error(f"Fallo al conectar a {name}: {result_msg}")
                self.gui.root.after(0, lambda: self._write_log("bot", f"❌ Error: {result_msg}"))
        
        threading.Thread(target=run_connect, daemon=True).start()

    def _after_connect_success(self):
        self.gui.view.show_file_explorer()
        self._refresh_local_view()
        self._refresh_remote_view()
        self._write_log("bot", "✨ Conexión establecida.")

    def _change_local_dir(self, target):
        log.info(f"Cambiando directorio local a: {target}")
        try:
            new_path = os.path.abspath(os.path.join(self.current_local_path, target))
            if os.path.isdir(new_path):
                self.current_local_path = new_path
                self._refresh_local_view()
            else:
                log.warning(f"Ruta local no válida: {new_path}")
                self._write_log("system", "Ruta local inválida.")
        except Exception as e:
            log.error(f"Error CD Local: {e}")

    def _change_remote_dir(self, target):
        if not self.sftp.sftp_client: return
        log.info(f"Cambiando directorio remoto a: {target}")
        if target == "..":
            parts = self.current_remote_path.rstrip('/').split('/')
            if len(parts) > 1: parts.pop()
            self.current_remote_path = "/".join(parts) or "/"
        else:
            self.current_remote_path = f"{self.current_remote_path.rstrip('/')}/{target}"
        self._refresh_remote_view()

    def _refresh_local_view(self):
        t0 = time.time()
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
            log.info(f"Vista local refrescada ({time.time()-t0:.4f}s)")
        except Exception as e:
            log.error(f"Error local: {e}")

    def _refresh_remote_view(self):
        path = self.current_remote_path
        if path in self.remote_cache:
            self.gui.view.remote_exp.refresh(path, self.remote_cache[path])
        threading.Thread(target=self._worker_sync_remote, args=(path,), daemon=True).start()

    def _worker_sync_remote(self, path_to_sync):
        if not self.sftp.sftp_client or self._sync_lock.locked(): return
        with self._sync_lock:
            try:
                t0 = time.time()
                log.info(f"Sincronizando directorio remoto: {path_to_sync}")
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
                log.info(f"Sync remoto finalizado en {time.time()-t0:.4f}s")
            except Exception as e:
                log.error(f"Error sync remoto: {e}")

    def start(self): 
        log.info("Lanzando aplicación.")
        self.gui.run()