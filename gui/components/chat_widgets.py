import tkinter as tk
from tkinter import scrolledtext
from gui.styles.ui_theme import UITheme

class ChatDisplay(scrolledtext.ScrolledText):
    """Versión optimizada con estilos pre-cargados."""
    def __init__(self, master, **kwargs):
        # Combinamos los atributos del tema con cualquier override que venga por kwargs
        attrs = {**UITheme.CHAT_DISPLAY_ATTR, **kwargs}
        super().__init__(master, **attrs)

class ChatInput(tk.Entry):
    """Input con manejo de foco y estilos automáticos."""
    def __init__(self, master, **kwargs):
        attrs = {**UITheme.CHAT_INPUT_ATTR, **kwargs}
        super().__init__(master, **attrs)
        
        # Optimización: UX de foco automática
        self.bind("<FocusIn>", lambda e: self.config(highlightthickness=2))
        self.bind("<FocusOut>", lambda e: self.config(highlightthickness=1))

class QuickButton(tk.Button):
    """Botón genérico optimizado para acciones rápidas."""
    def __init__(self, master, text, command, **kwargs):
        attrs = {**UITheme.QUICK_BTN_ATTR, **kwargs}
        super().__init__(master, text=text, command=command, **attrs)

class SendButton(tk.Button):
    """Botón de envío con estilo de acento resaltado."""
    def __init__(self, master, command, **kwargs):
        attrs = {**UITheme.SEND_BTN_ATTR, **kwargs}
        super().__init__(master, text="ENVIAR", command=command, **attrs)