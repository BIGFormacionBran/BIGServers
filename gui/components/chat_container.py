import tkinter as tk
from tkinter import scrolledtext
from ..styles.ui_theme import UITheme

class ChatContainer(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=UITheme.BG_CHAT, **kwargs)
        
        # ScrolledText muestra el scroll automáticamente solo si es necesario
        self.display = scrolledtext.ScrolledText(
            self, 
            bg=UITheme.BG_CHAT,
            fg=UITheme.FG_TEXT,
            font=("Consolas", 11),
            borderwidth=0,
            highlightthickness=0,
            padx=10,
            pady=10,
            undo=True,
            state='disabled'
        )
        self.display.pack(expand=True, fill='both')
        self._setup_tags()

    def _setup_tags(self):
        self.display.tag_config("user", foreground="#569cd6", font=("Consolas", 10, "bold"))
        self.display.tag_config("bot", foreground="#ce9178", font=("Consolas", 10, "bold"))
        self.display.tag_config("system", foreground="#858585", font=("Consolas", 9, "italic"))

    def add_message(self, role, text):
        self.display.configure(state='normal')
        prefix = "\n👤 TÚ: " if role == "user" else "\n🤖 AGENTE: " if role == "bot" else "\n⚙️ SISTEMA: "
        tag = role if role in ["user", "bot"] else "system"
        self.display.insert(tk.END, prefix, tag)
        self.display.insert(tk.END, f"{text}\n")
        self.display.see(tk.END)
        self.display.configure(state='disabled')