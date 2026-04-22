import tkinter as tk
import ctypes
import time
from .views.chat_view import ChatView
from utils.paths_util import Paths
from utils.logger_util import Logger

log = Logger.get_logger("GUI")

class ChatWindow:
    def __init__(self, on_submit_callback):
        t0 = time.perf_counter()
        self.root = tk.Tk()
        self.root.title("BIGServers - SFTP AI Agent")
        self.root.geometry("1000x700")
        
        # Seteamos el ID interno para que Windows respete nuestro icono
        self._set_taskbar_icon()
        
        # Carga de la vista
        self.view = ChatView(self.root, on_submit_callback)
        
        log.info(f"✅ GUI inicializada en {(time.perf_counter()-t0)*1000:.2f}ms")

    def _set_taskbar_icon(self):
        """Fuerza a Windows a mostrar el logo en la barra de tareas."""
        try:
            # Identificador único de aplicación
            appid = 'com.bigservers.sftpagent.v1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
            
            icon_file = str(Paths.DATA / "logo.ico")
            if os.path.exists(icon_file):
                self.root.iconbitmap(icon_file)
                log.info("🎨 Icono aplicado con éxito.")
        except Exception as e:
            log.warning(f"⚠️ No se pudo setear el icono: {e}")

    def write_message(self, role, text):
        self.view.render_message(role, text)

    def run(self):
        self.root.mainloop()