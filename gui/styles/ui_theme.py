class UITheme:
    BG_DARK = "#1e1e1e"
    BG_CHAT = "#252526"
    BG_INPUT = "#3c3c3c"
    FG_TEXT = "#d4d4d4"
    ACCENT = "#007acc"
    
    FONT_MONO = ("Consolas", 10)
    FONT_BOLD = ("Consolas", 10, "bold")

    # Atributos para Widgets
    CHAT_DISPLAY_ATTR = {
        "bg": BG_CHAT, "fg": FG_TEXT, "font": FONT_MONO,
        "borderwidth": 0, "padx": 10, "pady": 10, "insertbackground": "white"
    }
    
    CHAT_INPUT_ATTR = {
        "bg": BG_INPUT, "fg": "white", "font": FONT_MONO,
        "insertbackground": "white", "relief": "flat", "borderwidth": 5
    }
    
    # Estilos de botones
    BTN_BASE = {"relief": "flat", "cursor": "hand2", "font": ("Segoe UI", 9, "bold")}
    QUICK_BTN_ATTR = {**BTN_BASE, "bg": BG_INPUT, "fg": FG_TEXT, "activebackground": ACCENT}
    SEND_BTN_ATTR = {**BTN_BASE, "bg": ACCENT, "fg": "white", "activebackground": "#005a9e"}