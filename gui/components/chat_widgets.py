import tkinter as tk
from tkinter import scrolledtext

class ChatDisplay(scrolledtext.ScrolledText):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

class ChatInput(tk.Entry):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

class QuickButton(tk.Button):
    def __init__(self, master, text, command, **kwargs):
        super().__init__(master, text=text, command=command, **kwargs)

class SendButton(tk.Button):
    def __init__(self, master, command, **kwargs):
        super().__init__(master, text="ENVIAR", command=command, **kwargs)