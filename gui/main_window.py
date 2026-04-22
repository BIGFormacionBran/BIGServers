import tkinter as tk
import ctypes
import os
from utils.paths_util import Paths
from utils.logger_util import Logger

log = Logger.get_logger("GUI")

class MainWindow(tk.Tk):
    def __init__(self, app_manager):
        super().__init__()
        
        self._setup_windows_appid()
        
        self.app = app_manager
        self.title("BIGServers - SFTP AI Agent")
        
        # Centrar ventana
        width, height = 1000, 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self._set_app_icon()
        self.current_view = None

    def _setup_windows_appid(self):
        try:
            myappid = 'com.bigservers.sftpagent.v1' 
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            log.debug("🆔 Windows AppUserModelID configurado correctamente.")
        except Exception as e:
            log.warning(f"⚠️ No se pudo configurar el ID de aplicación: {e}")

    def _set_app_icon(self):
        try:
            icon_path = str(Paths.APP_ICON)
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
                # Forzar icono en la barra de tareas para algunos entornos de ejecución
                img = tk.PhotoImage(file=icon_path.replace(".ico", ".png")) if os.path.exists(icon_path.replace(".ico", ".png")) else None
                if img: self.iconphoto(True, img)
                log.info("🎨 Icono visual aplicado a la ventana.")
        except Exception as e:
            log.warning(f"⚠️ Error al cargar el archivo .ico: {e}")

    def show_view(self, view_class, **kwargs):
        if self.current_view:
            self.current_view.destroy()
        
        # Pasamos self como master y el resto de kwargs (como success_callback)
        self.current_view = view_class(self, **kwargs)
        self.current_view.pack(fill="both", expand=True)