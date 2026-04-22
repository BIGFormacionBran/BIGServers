import tkinter as tk
from gui.styles.ui_theme import UITheme

class AuthView(tk.Frame):
    def __init__(self, master, success_callback=None, **kwargs):
        # Master será la MainWindow. El AppManager pasa success_callback por kwargs en show_view
        super().__init__(master, bg=UITheme.BG_DARK)
        self.master = master
        # En el modelo de ventana única, el controller es el app_manager (master.app)
        self.controller = master.app 
        self.success_callback = success_callback
        
        self.pack(expand=True, fill="both")
        
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
                       activebackground=UITheme.BG_DARK, cursor="hand2").pack(pady=5)

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

        tk.Checkbutton(self, text="Recordar tras registro", variable=self.remember_var,
                       bg=UITheme.BG_DARK, fg="white", selectcolor=UITheme.BG_INPUT,
                       activebackground=UITheme.BG_DARK).pack(pady=2)

        tk.Checkbutton(self, text="Tengo una clave de registro (Rol)", variable=self.has_key_var,
                       command=self._toggle_key_field, bg=UITheme.BG_DARK, fg="white", 
                       selectcolor=UITheme.BG_INPUT).pack(pady=5)

        self.key_container = tk.Frame(self, bg=UITheme.BG_DARK)
        self.reg_key = self._create_input("Key de Acceso:", container=self.key_container, is_password=True)

        tk.Button(self, text="REGISTRARSE", command=self._on_register, **UITheme.SEND_BTN_ATTR, width=20).pack(pady=15)
        tk.Button(self, text="Volver al Login", command=self._build_login_ui,
                  bg=UITheme.BG_DARK, fg="#858585", borderwidth=0, cursor="hand2").pack()

    def _on_login(self):
        # Usamos los métodos de ayuda del controlador (AuthWindow o AppManager)
        email = self.email_ent.get()
        password = self.pass_ent.get()
        remember = self.remember_var.get()
        
        from daos.user_dao import UserDAO
        user = UserDAO.validate_login(email, password)
        if user and self.success_callback:
            self.success_callback(user, remember)
        else:
            self.show_error("Credenciales incorrectas.")

    def _on_register(self):
        from daos.user_dao import UserDAO
        nombre = self.reg_name.get()
        email = self.reg_email.get()
        password = self.reg_pass.get()
        key = self.reg_key.get() if self.has_key_var.get() else None
        remember = self.remember_var.get()

        success, msg = UserDAO.register_with_key(nombre, email, password, key)
        if success:
            user = UserDAO.validate_login(email, password)
            if user and self.success_callback:
                self.success_callback(user, remember)
        else:
            self.show_error(msg)

    def _create_input(self, label_text, container=None, is_password=False):
        parent = container if container else self
        frame = tk.Frame(parent, bg=UITheme.BG_DARK)
        frame.pack(fill="x", padx=40, pady=5)
        tk.Label(frame, text=label_text, bg=UITheme.BG_DARK, fg="#cccccc", font=("Segoe UI", 9)).pack(anchor="w")
        entry_frame = tk.Frame(frame, bg=UITheme.BG_INPUT)
        entry_frame.pack(fill="x")
        entry = tk.Entry(entry_frame, bg=UITheme.BG_INPUT, fg="white", borderwidth=5, relief="flat", insertbackground="white")
        if is_password: entry.config(show="*")
        entry.pack(side="left", expand=True, fill="x")
        if is_password:
            btn = tk.Button(entry_frame, text="👁", bg=UITheme.BG_INPUT, fg="#858585", borderwidth=0, command=lambda: self._toggle_pass(entry))
            btn.pack(side="right", padx=5)
        return entry

    def _toggle_pass(self, entry):
        entry.config(show="" if entry.cget("show") == "*" else "*")

    def _toggle_key_field(self):
        if self.has_key_var.get():
            self.key_container.pack(fill="x")
        else:
            self.key_container.pack_forget()

    def _clear_frame(self):
        for widget in self.winfo_children(): widget.destroy()

    def show_error(self, msg):
        tk.messagebox.showerror("Error", msg)