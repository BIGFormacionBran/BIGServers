import tkinter as tk
from gui.styles.ui_theme import UITheme

class ExplorerWidget(tk.Frame):
    def __init__(self, master, title, on_double_click_callback, **kwargs):
        super().__init__(master, bg=UITheme.BG_DARK, **kwargs)
        self.on_double_click = on_double_click_callback
        self.data = [] 
        self.selected_index = -1
        self.item_height = 24  # Un poco más de aire para legibilidad
        
        # Header simplificado
        header = tk.Frame(self, bg=UITheme.BG_DARK)
        header.pack(fill='x', padx=5, pady=4)
        tk.Label(header, text=title, bg=UITheme.BG_DARK, fg=UITheme.ACCENT, font=(UITheme.FONT_MONO[0], 10, "bold")).pack(side='left')
        
        self.path_var = tk.StringVar()
        tk.Entry(header, textvariable=self.path_var, bg="#333333", fg="#cccccc", 
                 borderwidth=0, font=(UITheme.FONT_MONO[0], 9), state='readonly').pack(side='left', fill='x', expand=True, padx=(10, 0))

        # Canvas con Scrollbar integrado
        self.canvas = tk.Canvas(self, bg=UITheme.BG_DARK, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", expand=True, fill="both")

        # Bindings optimizados
        self.canvas.bind("<Button-1>", self._handle_click)
        self.canvas.bind("<Double-Button-1>", self._handle_click)
        self.canvas.bind("<Configure>", lambda e: self._draw())
        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def refresh(self, current_path, data_list):
        self.path_var.set(current_path)
        self.data = [("..", "DIR", "")] + data_list
        self.selected_index = -1
        self._draw()

    def _draw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        self.canvas.config(scrollregion=(0, 0, w, len(self.data) * self.item_height))

        for i, (name, tipo, size) in enumerate(self.data):
            y = i * self.item_height
            if i == self.selected_index:
                self.canvas.create_rectangle(0, y, w, y + self.item_height, fill="#37373d", outline="")

            color = "#e2c08d" if tipo == "DIR" else UITheme.FG_TEXT
            icon = "📁" if tipo == "DIR" else "📄"
            
            self.canvas.create_text(5, y + 12, text=icon, fill=color, anchor="w", font=("Segoe UI Symbol", 10))
            self.canvas.create_text(25, y + 12, text=name, fill=color, anchor="w", font=UITheme.FONT_MONO)
            if size:
                self.canvas.create_text(w - 10, y + 12, text=size, fill="#858585", anchor="e", font=(UITheme.FONT_MONO[0], 8))

    def _handle_click(self, event):
        idx = int(self.canvas.canvasy(event.y) // self.item_height)
        if 0 <= idx < len(self.data):
            self.selected_index = idx
            if event.num == 1 and "Double" not in str(event.type):
                self._draw()
            else:
                name, tipo, _ = self.data[idx]
                self.on_double_click(name, tipo)