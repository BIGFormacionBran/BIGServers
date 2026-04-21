import tkinter as tk
from ..components.explorer_widget import ExplorerWidget
from ..components.chat_container import ChatContainer
from ..components.chat_widgets import ChatInput, QuickButton, SendButton
from ..styles.ui_theme import UITheme

class ChatView:
    def __init__(self, root, on_submit_callback):
        self.root = root
        self.on_submit = on_submit_callback
        self.server_var = tk.StringVar()
        self.main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=UITheme.BG_DARK, sashwidth=4)
        self.main_pane.pack(expand=True, fill='both')

        self.chat_side = tk.Frame(self.main_pane, bg=UITheme.BG_CHAT)
        self.chat_container = ChatContainer(self.chat_side)
        self.chat_container.pack(expand=True, fill='both')
        self._build_input_area(self.chat_side)
        self.main_pane.add(self.chat_side)

        self.explorer_side = tk.Frame(self.main_pane, bg=UITheme.BG_DARK)
        self.local_exp = None
        self.remote_exp = None

    def _build_input_area(self, container):
        ctrl_panel = tk.Frame(container, bg=UITheme.BG_CHAT)
        ctrl_panel.pack(fill='x', side='bottom', padx=10, pady=10)
        btn_bar = tk.Frame(ctrl_panel, bg=UITheme.BG_CHAT)
        btn_bar.pack(fill='x', pady=(0, 5))
        QuickButton(btn_bar, "📁 LISTAR", lambda: self.on_submit("/list"), **UITheme.QUICK_BTN_ATTR).pack(side='left', padx=2)
        from tkinter import ttk
        self.selector = ttk.Combobox(btn_bar, textvariable=self.server_var, state="readonly")
        self.selector.pack(side='left', padx=5, expand=True, fill='x')
        QuickButton(btn_bar, "⚡ CONECTAR", self._on_connect_click, **UITheme.QUICK_BTN_ATTR).pack(side='left', padx=2)

        input_row = tk.Frame(ctrl_panel, bg=UITheme.BG_CHAT)
        input_row.pack(fill='x')
        self.entry = ChatInput(input_row, **UITheme.CHAT_INPUT_ATTR)
        self.entry.pack(side='left', expand=True, fill='x', ipady=8)
        self.entry.bind("<Return>", lambda e: self._on_send())
        SendButton(input_row, self._on_send, **UITheme.SEND_BTN_ATTR).pack(side='right', padx=(5, 0))

    def show_file_explorer(self):
        if self.local_exp: return
        self.main_pane.forget(self.chat_side)
        self.main_pane.add(self.explorer_side, width=500)
        self.main_pane.add(self.chat_side)
        v_pane = tk.PanedWindow(self.explorer_side, orient=tk.VERTICAL, bg=UITheme.BG_DARK, sashwidth=2)
        v_pane.pack(expand=True, fill='both')
        
        self.local_exp = ExplorerWidget(v_pane, "💻 LOCAL", lambda n, t: self.on_submit(f"/cd_local {n}"))
        self.remote_exp = ExplorerWidget(v_pane, "🌐 REMOTO", lambda n, t: self.on_submit(f"/cd_remote {n}"))
        v_pane.add(self.local_exp)
        v_pane.add(self.remote_exp)

    def render_message(self, role, text): self.chat_container.add_message(role, text)
    def update_servers(self, names):
        self.selector['values'] = names
        if names: self.selector.current(0)
    def _on_connect_click(self):
        sel = self.server_var.get()
        if sel: self.on_submit(f"/connect {sel}")
    def _on_send(self):
        val = self.entry.get().strip()
        if val:
            self.entry.delete(0, tk.END)
            self.on_submit(val)