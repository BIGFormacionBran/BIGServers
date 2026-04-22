import tkinter as tk
from ..styles.ui_theme import UITheme

class AuthView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=UITheme.BG_DARK)
        self.master = master
        self.controller = controller
        self.pack(expand=True, fill="both")
        
        # Variables de control
        self.remember_var = tk.BooleanVar(value=False)
        self.has_key_var = tk.BooleanVar(value=False)
        
        self._build_login_ui()

    def _build_login_ui(self):
        self._clear_frame()
        tk.Label(self, text="INICIAR SESIÓN", bg=UITheme.BG_DARK, fg=UITheme.ACCENT, 
                 font=("Segoe UI", 16, "bold")).pack(pady=20)

        self.email_ent = self._create_input("Email:")
        self.pass_ent = self._create_input("Contraseña:", is_password=True)

        tk.Checkbutton(self, text="Recordar usuario", variable=self.remember_var,
                       bg=UITheme.BG_DARK, fg="white", selectcolor=UITheme.BG_INPUT,
                       activebackground=UITheme.BG_DARK).pack(pady=5)

        tk.Button(self, text="INGRESAR", command=self._on_login, **UITheme.SEND_BTN_ATTR, width=20).pack(pady=10)
        
        tk.Button(self, text="¿No tienes cuenta? Regístrate", command=self._build_register_ui,
                  bg=UITheme.BG_DARK, fg="#858585", borderwidth=0, cursor="hand2").pack()

    def _build_register_ui(self):
        self._clear_frame()
        tk.Label(self, text="CREAR CUENTA", bg=UITheme.BG_DARK, fg=UITheme.ACCENT, 
                 font=("Segoe UI", 14, "bold")).pack(pady=15)

        self.reg_name = self._create_input("Nombre:")
        self.reg_email = self._create_input("Email:")
        self.reg_pass = self._create_input("Contraseña:", is_password=True)

        # Checkbox para Key de Rol
        tk.Checkbutton(self, text="Tengo una clave de registro (Rol)", variable=self.has_key_var,
                       command=self._toggle_key_field, bg=UITheme.BG_DARK, fg="white", 
                       selectcolor=UITheme.BG_INPUT).pack(pady=5)

        # Contenedor para la key (oculto por defecto)
        self.key_container = tk.Frame(self, bg=UITheme.BG_DARK)
        self.reg_key = self._create_input("Key de Acceso:", container=self.key_container, is_password=True)

        tk.Button(self, text="REGISTRARSE", command=self._on_register, **UITheme.SEND_BTN_ATTR, width=20).pack(pady=15)
        tk.Button(self, text="Volver al Login", command=self._build_login_ui,
                  bg=UITheme.BG_DARK, fg="#858585", borderwidth=0).pack()

    def _create_input(self, label_text, container=None, is_password=False):
        parent = container if container else self
        frame = tk.Frame(parent, bg=UITheme.BG_DARK)
        frame.pack(fill="x", padx=40, pady=5)

        tk.Label(frame, text=label_text, bg=UITheme.BG_DARK, fg="#cccccc", font=("Segoe UI", 9)).pack(anchor="w")
        
        entry_frame = tk.Frame(frame, bg=UITheme.BG_INPUT)
        entry_frame.pack(fill="x")

        entry = tk.Entry(entry_frame, bg=UITheme.BG_INPUT, fg="white", borderwidth=5, relief="flat",
                         insertbackground="white", font=UITheme.FONT_MONO)
        if is_password: entry.config(show="*")
        entry.pack(side="left", expand=True, fill="x")

        if is_password:
            btn = tk.Button(entry_frame, text="👁", bg=UITheme.BG_INPUT, fg="#858585", 
                            borderwidth=0, cursor="hand2", command=lambda: self._toggle_pass(entry))
            btn.pack(side="right", padx=5)

        return entry

    def _toggle_pass(self, entry):
        entry.config(show="" if entry.cget("show") == "*" else "*")

    def _toggle_key_field(self):
        if self.has_key_var.get():
            self.key_container.pack(fill="x", before=self.key_container.master.children.get('!button'))
        else:
            self.key_container.pack_forget()

    def _clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _on_login(self):
        self.controller.login_action(self.email_ent.get(), self.pass_ent.get(), self.remember_var.get())

    def _on_register(self):
        key = self.reg_key.get() if self.has_key_var.get() else None
        # Aquí llamarías a la lógica de registro del controller
        pass