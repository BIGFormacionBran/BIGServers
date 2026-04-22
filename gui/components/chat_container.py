import tkinter as tk
from gui.styles.ui_theme import UITheme

class ChatContainer(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=UITheme.BG_CHAT, **kwargs)
        
        self.canvas = tk.Canvas(self, bg=UITheme.BG_CHAT, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", expand=True, fill="both")
        
        self.messages = []
        self.padding = 15
        
        self.canvas.bind("<Configure>", lambda e: self._redraw())
        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def add_message(self, role, text):
        color = "#569cd6" if role == "user" else "#ce9178"
        if role == "system": color = "#858585"
        prefix = "👤 TÚ: " if role == "user" else "🤖 AGENTE: "
        if role == "system": prefix = "⚙️ SISTEMA: "
        
        self.messages.append({"prefix": prefix, "text": text, "color": color})
        self._redraw()
        self.canvas.yview_moveto(1.0)

    def _redraw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() - 30
        y = self.padding
        
        for msg in self.messages:
            # Prefijo
            self.canvas.create_text(self.padding, y, text=msg["prefix"], fill=msg["color"], 
                                    anchor="nw", font=("Consolas", 10, "bold"))
            y += 20
            # Texto con wrap (ajuste de línea automático)
            t_id = self.canvas.create_text(self.padding, y, text=msg["text"], fill=UITheme.FG_TEXT, 
                                          anchor="nw", font=UITheme.FONT_MONO, width=w)
            bbox = self.canvas.bbox(t_id)
            y = bbox[3] + 15 # Espaciado entre mensajes

        self.canvas.config(scrollregion=(0, 0, w, y))