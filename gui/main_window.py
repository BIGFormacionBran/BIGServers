import tkinter as tk
import ctypes
import os
from utils.paths_util import Paths
from utils.logger_util import Logger

log = Logger.get_logger("GUI")

class MainWindow(tk.Tk):
    def __init__(self, app_manager):
        super().__init__()
        
        # --- AQUÍ ES DONDE DEBE IR ---
        self._setup_windows_appid()
        # -----------------------------
        
        self.app = app_manager
        self.title("BIGServers - SFTP AI Agent")
        self.geometry("1000x700")
        
        self._set_app_icon()
        self.current_view = None

    def _setup_windows_appid(self):
        """
        Informa a Windows que este proceso tiene un ID único.
        Esto permite que el icono de la barra de tareas sea el logo.ico 
        y no el de python.exe.
        """
        try:
            # Puedes poner el nombre que quieras, mientras sea único
            myappid = 'com.bigservers.sftpagent.v1' 
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            log.debug("🆔 Windows AppUserModelID configurado correctamente.")
        except Exception as e:
            log.warning(f"⚠️ No se pudo configurar el ID de aplicación para Windows: {e}")

    def _set_app_icon(self):
        """Aplica el icono visual a la ventana."""
        try:
            icon_path = str(Paths.APP_ICON)
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
                log.info("🎨 Icono visual aplicado a la ventana.")
        except Exception as e:
            log.warning(f"⚠️ Error al cargar el archivo .ico: {e}")

    def show_view(self, view_class, **kwargs):
        """Limpia el contenido actual y carga una nueva vista (Frame)."""
        if self.current_view:
            self.current_view.destroy()
        
        # Instanciamos la nueva vista pasando 'self' como master (MainWindow)
        self.current_view = view_class(self, **kwargs)
        self.current_view.pack(fill="both", expand=True)