import tkinter as tk

class ExplorerWidget(tk.Frame):
    def __init__(self, master, title, on_double_click_callback, **kwargs):
        super().__init__(master, bg="#1e1e1e", **kwargs)
        self.on_double_click = on_double_click_callback
        self.data = []  # Lista de (name, tipo, size)
        self.selected_index = -1
        self.item_height = 22
        
        # --- HEADER ---
        header = tk.Frame(self, bg="#1e1e1e")
        header.pack(fill='x', padx=5, pady=2)
        tk.Label(header, text=title, bg="#1e1e1e", fg="#007acc", font=("Consolas", 10, "bold")).pack(side='left')
        
        self.path_var = tk.StringVar()
        self.path_entry = tk.Entry(header, textvariable=self.path_var, bg="#333333", fg="#cccccc", 
                                  insertbackground="white", borderwidth=0, font=("Consolas", 9), state='readonly')
        self.path_entry.pack(side='left', fill='x', expand=True, padx=(10, 0))

        # --- CANVAS EXPLORER ---
        self.container = tk.Frame(self, bg="#1e1e1e")
        self.container.pack(expand=True, fill='both', padx=5, pady=5)

        self.canvas = tk.Canvas(self.container, bg="#1e1e1e", highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", expand=True, fill="both")

        # Eventos
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        self.canvas.bind("<Configure>", lambda e: self._draw())
        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def refresh(self, current_path, data_list):
        self.path_var.set(current_path)
        # Añadimos la opción de volver atrás si no estamos en raíz
        self.data = [("..", "DIR", "")] + data_list
        self.selected_index = -1
        self._draw()

    def _draw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        
        total_height = len(self.data) * self.item_height
        self.canvas.config(scrollregion=(0, 0, w, total_height))

        for i, (name, tipo, size) in enumerate(self.data):
            y1 = i * self.item_height
            y2 = y1 + self.item_height
            
            # Fondo de selección
            if i == self.selected_index:
                self.canvas.create_rectangle(0, y1, w, y2, fill="#37373d", outline="")

            # Icono simple (Cuadrado para DIR, Círculo para FILE)
            color = "#e2c08d" if tipo == "DIR" else "#d4d4d4"
            icon_char = "📁" if tipo == "DIR" else "📄"
            
            # Texto Nombre
            self.canvas.create_text(5, y1 + 11, text=icon_char, fill=color, anchor="w", font=("Segoe UI Symbol", 10))
            self.canvas.create_text(25, y1 + 11, text=name, fill=color, anchor="w", font=("Consolas", 10))
            
            # Texto Tamaño (si existe)
            if size:
                self.canvas.create_text(w - 10, y1 + 11, text=size, fill="#858585", anchor="e", font=("Consolas", 9))

    def _on_click(self, event):
        canvas_y = self.canvas.canvasy(event.y)
        index = int(canvas_y // self.item_height)
        if 0 <= index < len(self.data):
            self.selected_index = index
            self._draw()

    def _on_double_click(self, event):
        canvas_y = self.canvas.canvasy(event.y)
        index = int(canvas_y // self.item_height)
        if 0 <= index < len(self.data):
            name, tipo, _ = self.data[index]
            self.on_double_click(name, tipo)