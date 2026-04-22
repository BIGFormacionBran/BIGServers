import tkinter as tk
import ctypes
import time
import os  # <-- CORREGIDO: Importación necesaria para os.path
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
        
        # Primero configuramos los iconos
        self._set_app_icons()
        
        self.view = ChatView(self.root, on_submit_callback)
        log.info(f"✅ GUI inicializada en {(time.perf_counter()-t0)*1000:.2f}ms")

    def _set_app_icons(self):
        """Configura el icono en la ventana y en la barra de tareas de Windows."""
        try:
            icon_path = str(Paths.APP_ICON)
            
            if os.path.exists(icon_path):
                # 1. Icono de la ventana (Esquina superior izquierda)
                self.root.iconbitmap(icon_path)
                
                # 2. Icono de la Barra de Tareas (Windows)
                # Esto le dice a Windows que no agrupe el script como 'python.exe' sino como nuestra app
                appid = 'bigservers.sftp.aiagent.v1'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
                
                log.info("🎨 Iconos de ventana y barra de tareas aplicados.")
            else:
                log.warning(f"⚠️ No se encontró el icono en: {icon_path}")
        except Exception as e:
            log.warning(f"⚠️ Error al setear iconos: {e}")

    def write_message(self, role, text):
        self.view.render_message(role, text)

    def run(self):
        self.root.mainloop()