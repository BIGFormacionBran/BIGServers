import tkinter as tk
from .views.chat_view import ChatView

class ChatWindow:
    def __init__(self, on_submit_callback):
        self.root = tk.Tk()
        self.root.title("SFTP AI Agent")
        self.root.geometry("850x650")
        
        # Iniciamos la vista (Skeleton + Styles)
        self.view = ChatView(self.root, on_submit_callback)

    def write_message(self, role, text):
        self.view.render_message(role, text)

    def run(self):
        self.root.mainloop()