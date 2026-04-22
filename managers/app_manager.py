import threading
import time
from .sftp_manager import SFTPManager
from utils.logger_util import Logger
from utils.json_util import JsonUtil
from utils.paths_util import Paths
# Importamos el DAO, no el UTIL directamente para cumplir con tu lógica
from daos.server_dao import ServerDAO 

log = Logger.get_logger("APP_MANAGER")

class AppManager:
    def __init__(self):
        self.sftp = SFTPManager()
        self.user_data = None
        self._sync_lock = threading.Lock()
        self.gui = None
        self.auth = None

    def start(self):
        """Punto de entrada: decide si va al login o al chat directamente."""
        config = JsonUtil.load(Paths.USER_CONFIG)
        
        if config and config.get("remember_me") and config.get("user"):
            log.info(f"🔄 Sesión recuperada: {config['user']['nombre']}")
            self.user_data = config["user"]
            self._launch_main_gui()
        else:
            self._launch_auth_gui()

    def _launch_auth_gui(self):
        """Lanza la ventana de login."""
        from gui.auth_window import AuthWindow
        self.auth = AuthWindow(success_callback=self._on_auth_success)
        log.info("🔐 Ventana de autenticación iniciada")
        self.auth.run()

    def _on_auth_success(self, user, remember):
        """Callback ejecutado por AuthWindow al loguear con éxito."""
        self.user_data = user
        if remember:
            # Persistimos la sesión en el JSON configurado en Paths
            JsonUtil.save(Paths.USER_CONFIG, {
                "remember_me": True, 
                "user": user
            })
        self._launch_main_gui()

    def _launch_main_gui(self):
        """Lanza la interfaz de chat principal."""
        from gui.chat_window import ChatWindow
        self.gui = ChatWindow(on_submit_callback=self.handle_input)
        
        # Carga inicial de servidores en segundo plano para no congelar la GUI
        threading.Thread(target=self._load_initial_data, daemon=True).start()
        
        log.info("🖥️ Interfaz principal lanzada")
        self.gui.run()

    def _load_initial_data(self):
        """Carga los servidores desde la DB usando el DAO."""
        start = time.perf_counter()
        try:
            # Usamos el DAO especializado para obtener la lista de nombres
            servers = ServerDAO.get_server_names() 
            log.info(f"📂 {len(servers)} servidores cargados en {(time.perf_counter()-start)*1000:.2f}ms")
            
            # Actualizamos la GUI en el hilo principal de Tkinter
            if self.gui and self.gui.root:
                self.gui.root.after(0, lambda: self.gui.view.update_servers(servers))
        except Exception as e:
            log.error(f"❌ Error cargando servidores iniciales: {e}")

    def handle_input(self, text):
        """Maneja el input del chat."""
        if not text: return
        # Ejecutamos en hilo separado para que la UI no se bloquee durante el comando
        threading.Thread(target=self._execute_command, args=(text,), daemon=True).start()

    def _execute_command(self, text):
        """Lógica de procesamiento de comandos."""
        parts = text.split()
        if not parts: return
        
        cmd = parts[0].lower()
        
        if cmd == "/connect" and len(parts) > 1:
            server_name = parts[1]
            self.gui.write_message("system", f"Conectando a {server_name}...")
            
            # El SFTPManager se encarga de buscar los detalles mediante ServerDAO internamente
            success, msg = self.sftp.connect(server_name)
            
            if success:
                self.gui.root.after(0, self.gui.view.show_file_explorer)
                log.info(f"✅ Conexión establecida con {server_name}")
            else:
                self.gui.write_message("system", f"Error: {msg}")
                log.error(f"❌ Fallo de conexión: {msg}")