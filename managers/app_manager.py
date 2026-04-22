import threading
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
        # Inicializamos la ventana única de la aplicación
        self.root = MainWindow(self)
        self.sftp = SFTPManager()
        self.user_data = None

    def start(self):
        """
        Punto de entrada principal. 
        Verifica sesión existente o lanza el flujo de login.
        """
        config = JsonUtil.load(Paths.USER_CONFIG)
        
        if config and config.get("session_token"):
            log.info("🔄 Validando token de sesión persistente...")
            # Asumimos que UserDAO tiene validate_session para tokens
            user = UserDAO.validate_session(config["session_token"])
            if user:
                self.user_data = user
                log.info(f"✅ Sesión recuperada: {user['nombre']}")
                self.show_main_chat()
                self.root.mainloop()
                return
        
        # Si no hay sesión, al login
        log.info("🔑 No se detectó sesión activa. Iniciando Login.")
        self.show_login()
        self.root.mainloop()

    def show_login(self):
        """Carga la vista de AuthView en el contenedor principal."""
        from gui.views.auth_view import AuthView
        # Pasamos el callback para que AuthView sepa qué hacer al tener éxito
        self.root.show_view(AuthView, success_callback=self._on_auth_success)

    def show_main_chat(self):
        """Carga la interfaz del Chat y el Explorador."""
        from gui.views.chat_view import ChatView
        self.root.show_view(ChatView, on_submit_callback=self.handle_input)
        
        # Carga de datos (servidores) en segundo plano para no congelar la UI
        threading.Thread(target=self._load_initial_data, daemon=True).start()

    def _on_auth_success(self, user, remember):
        """
        Manejador de éxito de autenticación.
        Guarda el token si 'recordar' está activo y cambia de vista.
        """
        self.user_data = user
        if remember:
            # Asumimos que UserDAO genera tokens únicos para la sesión
            token = UserDAO.generate_session_token(user['id'])
            JsonUtil.save(Paths.USER_CONFIG, {"session_token": token})
            log.debug("💾 Token de sesión guardado localmente.")
        
        self.show_main_chat()

    def _load_initial_data(self):
        """Obtiene los nombres de servidores y actualiza el combobox del chat."""
        try:
            servers = ServerDAO.get_server_names() 
            # Verificamos si la vista actual es la de chat y tiene el método de actualización
            if hasattr(self.root.current_view, 'update_servers'):
                # Usamos after(0, ...) para ejecutar la actualización en el hilo de Tkinter
                self.root.after(0, lambda: self.root.current_view.update_servers(servers))
                log.info(f"📊 {len(servers)} servidores cargados en la interfaz.")
        except Exception as e:
            log.error(f"❌ Error cargando servidores iniciales: {e}")

    def handle_input(self, text):
        """Recibe el texto del chat y lo procesa en un hilo separado."""
        if not text or not text.strip():
            return
        
        threading.Thread(target=self._execute_command, args=(text.strip(),), daemon=True).start()

    def _execute_command(self, text):
        """Lógica interna para interpretar comandos (/connect, etc)."""
        parts = text.split()
        cmd = parts[0].lower()
        
        if cmd == "/connect" and len(parts) > 1:
            server_name = parts[1]
            # Escribir en el chat (vía hilo principal)
            self.root.after(0, lambda: self.root.current_view.write_message("system", f"Conectando a {server_name}..."))
            
            success, msg = self.sftp.connect(server_name)
            
            if success:
                log.info(f"✅ Conexión exitosa a {server_name}")
                # Al conectar, mostramos el explorador de archivos
                self.root.after(0, self.root.current_view.show_file_explorer)
            else:
                log.warning(f"❌ Fallo de conexión: {msg}")
                self.root.after(0, lambda: self.root.current_view.write_message("system", f"Error: {msg}"))
        else:
            # Aquí podrías añadir lógica para hablar con la IA si no es un comando SFTP
            log.debug(f"Comando no reconocido o mensaje de chat: {text}")