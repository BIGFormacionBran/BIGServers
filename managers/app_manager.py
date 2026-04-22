import threading
import os
from managers.sftp_manager import SFTPManager
from utils.logger_util import Logger
from utils.json_util import JsonUtil
from utils.paths_util import Paths
from daos.server_dao import ServerDAO 
from daos.user_dao import UserDAO

log = Logger.get_logger("APP_MANAGER")

class AppManager:
    def __init__(self):
        from gui.main_window import MainWindow
        self.root = MainWindow(self)
        self.sftp = SFTPManager()
        self.user_data = None

    def start(self):
        config = JsonUtil.load(Paths.USER_CONFIG)
        if config and config.get("session_token"):
            log.info("🔄 Validando token de sesión persistente...")
            user = UserDAO.validate_session(config["session_token"])
            if user:
                self.user_data = user
                self.show_main_chat()
                self.root.mainloop()
                return
        
        self.show_login()
        self.root.mainloop()

    def show_login(self):
        from gui.views.auth_view import AuthView
        self.root.show_view(AuthView, success_callback=self._on_auth_success)

    def show_main_chat(self):
        from gui.views.chat_view import ChatView
        self.root.show_view(ChatView, on_submit_callback=self.handle_input)
        
        # --- SALUDO INICIAL ---
        name = self.user_data.get('nombre', 'Usuario')
        role = self.user_data.get('rol', 'USER')
        msg = f"¡Hola {name}! Has iniciado sesión como [{role}]. ¿En qué puedo ayudarte hoy?"
        self.root.after(100, lambda: self.root.current_view.write_message("system", msg))

        threading.Thread(target=self._load_initial_data, daemon=True).start()

    def _on_auth_success(self, user, remember):
        self.user_data = user
        if remember:
            token = UserDAO.generate_session_token(user['id'])
            JsonUtil.save(Paths.USER_CONFIG, {"session_token": token})
        self.show_main_chat()

    def _load_initial_data(self):
        try:
            servers = ServerDAO.get_server_names() 
            if hasattr(self.root.current_view, 'update_servers'):
                self.root.after(0, lambda: self.root.current_view.update_servers(servers))
        except Exception as e:
            log.error(f"❌ Error cargando servidores iniciales: {e}")

    def handle_input(self, text):
        if not text or not text.strip(): return
        threading.Thread(target=self._execute_command, args=(text.strip(),), daemon=True).start()

    def _execute_command(self, text):
        parts = text.split()
        cmd = parts[0].lower()
        role = self.user_data.get('rol', '').upper()
        
        if cmd == "/connect" and len(parts) > 1:
            server_name = parts[1]
            self.root.after(0, lambda: self.root.current_view.write_message("system", f"Intentando conectar a {server_name}..."))
            
            if role == "DEVELOPER":
                self.root.after(0, lambda: self.root.current_view.write_message("system", "ℹ️ Modo Developer: Acceso de lectura/escritura permitido. Gestión de credenciales bloqueada."))

            success, msg = self.sftp.connect(server_name)
            if success:
                self.root.after(0, lambda: self.root.current_view.write_message("system", f"✅ Conectado a {server_name} con éxito."))
                # 1. Mostramos los paneles de archivos
                self.root.after(0, self.root.current_view.show_file_explorer)
                # 2. Refrescamos el contenido de los paneles
                self._refresh_explorers()
            else:
                self.root.after(0, lambda: self.root.current_view.write_message("system", f"❌ Error: {msg}"))
        
        elif cmd == "/list":
             self.root.after(0, lambda: self.root.current_view.write_message("system", "Refrescando lista de archivos..."))
             self._refresh_explorers()
        else:
            self.root.after(0, lambda: self.root.current_view.write_message("agent", f"Entiendo que quieres hacer: '{text}'. Por ahora solo proceso comandos SFTP."))

    def _refresh_explorers(self):
        """Obtiene la estructura de archivos local y remota y actualiza la GUI."""
        try:
            # --- PROCESAR REMOTO ---
            remote_data = []
            try:
                # Obtenemos lista de objetos SFTPAttributes de paramiko
                raw_remote_files = self.sftp.list_dir(".")
                for f in raw_remote_files:
                    # Determinamos si es directorio por el modo (longname suele empezar con 'd')
                    is_dir = "d" in f.longname[0]
                    tipo = "DIR" if is_dir else "FILE"
                    size = f"{f.st_size / 1024:.1f} KB" if not is_dir else ""
                    remote_data.append((f.filename, tipo, size))
            except Exception as e:
                log.error(f"Error listando remoto: {e}")
                self.root.after(0, lambda: self.root.current_view.write_message("system", "⚠️ Error al leer archivos remotos."))

            # --- PROCESAR LOCAL ---
            local_data = []
            local_path = os.getcwd()
            try:
                for item in os.listdir(local_path):
                    full_p = os.path.join(local_path, item)
                    is_dir = os.path.isdir(full_p)
                    tipo = "DIR" if is_dir else "FILE"
                    size = f"{os.path.getsize(full_p) / 1024:.1f} KB" if not is_dir else ""
                    local_data.append((item, tipo, size))
            except Exception as e:
                log.error(f"Error listando local: {e}")

            # --- ENVIAR A LA GUI ---
            view = self.root.current_view
            if hasattr(view, 'remote_exp') and hasattr(view, 'local_exp'):
                self.root.after(0, lambda: view.remote_exp.refresh("/", remote_data))
                self.root.after(0, lambda: view.local_exp.refresh(local_path, local_data))

        except Exception as e:
            log.error(f"Fallo crítico en _refresh_explorers: {e}")