import tkinter as tk
from tkinter import scrolledtext
from ..styles.ui_theme import UITheme

class ChatContainer(tk.Frame):
    ROLES = {
        "user": ("\n👤 TÚ: ", "#569cd6", ("Consolas", 10, "bold")),
        "bot": ("\n🤖 AGENTE: ", "#ce9178", ("Consolas", 10, "bold")),
        "system": ("\n⚙️ SISTEMA: ", "#858585", ("Consolas", 9, "italic"))
    }

    def __init__(self, master, **kwargs):
        super().__init__(master, bg=UITheme.BG_CHAT, **kwargs)
        self.display = scrolledtext.ScrolledText(
            self, bg=UITheme.BG_CHAT, fg=UITheme.FG_TEXT, font=UITheme.FONT_MONO,
            borderwidth=0, highlightthickness=0, padx=10, pady=10, state='disabled'
        )
        self.display.pack(expand=True, fill='both')
        for role, (_, color, font) in self.ROLES.items():
            self.display.tag_config(role, foreground=color, font=font)

    def add_message(self, role, text):
        prefix, _, _ = self.ROLES.get(role, self.ROLES["system"])
        self.display.configure(state='normal')
        self.display.insert(tk.END, prefix, role)
        self.display.insert(tk.END, f"{text}\n")
        self.display.see(tk.END)
        self.display.configure(state='disabled')