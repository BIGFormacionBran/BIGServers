class UITheme:
    # --- COLORES ---
    BG_DARK = "#1e1e1e"
    BG_CHAT = "#252526"
    BG_INPUT = "#3c3c3c"
    FG_TEXT = "#d4d4d4"
    ACCENT = "#007acc"
    
    # --- CONFIGURACIÓN BASE ---
    FONT_MONO = ("Consolas", 10)
    FONT_UI = ("Segoe UI", 9)

    # Atributos comunes para evitar repetición
    _BASE_BTN = {
        "relief": "flat",
        "cursor": "hand2",
        "font": (FONT_UI[0], 9, "bold"),
        "activeforeground": "white"
    }

    QUICK_BTN_ATTR = {**_BASE_BTN, "bg": BG_INPUT, "fg": FG_TEXT, "activebackground": ACCENT}
    SEND_BTN_ATTR = {**_BASE_BTN, "bg": ACCENT, "fg": "white", "activebackground": "#005a9e"}
    
    CHAT_INPUT_ATTR = {
        "bg": BG_INPUT, "fg": "white", "insertbackground": "white",
        "borderwidth": 0, "highlightthickness": 1, "highlightcolor": ACCENT,
        "font": FONT_MONO
    }

    # Helpers de Layout
    LAYOUT_FILL = {"expand": True, "fill": "both"}