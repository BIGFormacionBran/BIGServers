import tkinter as tk
from gui.styles.ui_theme import UITheme

class CanvasButton(tk.Canvas):
    """Botón optimizado dibujado en Canvas para evitar la carga de widgets del sistema."""
    def __init__(self, master, text, command, width=100, height=30, bg_color=UITheme.ACCENT, **kwargs):
        super().__init__(master, width=width, height=height, bg=master["bg"], highlightthickness=0, bd=0, cursor="hand2")
        self.command = command
        self.bg_color = bg_color
        self.text = text
        
        self.rect = self.create_rectangle(0, 0, width, height, fill=bg_color, outline="")
        self.label = self.create_text(width//2, height//2, text=text, fill="white", font=("Segoe UI", 9, "bold"))
        
        self.bind("<Button-1>", lambda e: self.command())
        self.bind("<Enter>", lambda e: self.itemconfig(self.rect, fill="#005a9e"))
        self.bind("<Leave>", lambda e: self.itemconfig(self.rect, fill=bg_color))

class ChatInput(tk.Entry):
    def __init__(self, master, **kwargs):
        attrs = {**UITheme.CHAT_INPUT_ATTR, **kwargs}
        super().__init__(master, **attrs)
        self.config(highlightbackground=UITheme.BG_INPUT, highlightcolor=UITheme.ACCENT)

class QuickButton(CanvasButton):
    def __init__(self, master, text, command, **kwargs):
        super().__init__(master, text, command, width=80, height=25, bg_color=UITheme.BG_INPUT)

class SendButton(CanvasButton):
    def __init__(self, master, command, **kwargs):
        super().__init__(master, "ENVIAR", command, width=80, height=35, bg_color=UITheme.ACCENT)