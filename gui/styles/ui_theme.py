class UITheme:
    # --- COLORES ---
    BG_DARK = "#1e1e1e"
    BG_CHAT = "#252526"
    BG_INPUT = "#3c3c3c"
    FG_TEXT = "#d4d4d4"
    ACCENT = "#007acc"
    
    # --- CONFIGURACIÓN DE WIDGETS (ATRIBUTOS) ---
    
    # Pantalla de chat
    CHAT_DISPLAY_ATTR = {
        "bg": BG_CHAT, 
        "fg": FG_TEXT, 
        "font": ("Consolas", 11),
        "borderwidth": 0, 
        "padx": 10, 
        "pady": 10
    }
    
    # Campo de texto (Input)
    CHAT_INPUT_ATTR = {
        "bg": BG_INPUT, 
        "fg": "white", 
        "insertbackground": "white",
        "borderwidth": 0, 
        "highlightthickness": 1,
        "highlightcolor": ACCENT
    }
    
    # Botones rápidos (Listar, Conectar, Salir)
    QUICK_BTN_ATTR = {
        "bg": BG_INPUT, 
        "fg": FG_TEXT, 
        "relief": "flat", 
        "cursor": "hand2",
        "font": ("Segoe UI", 9, "bold"),
        "activebackground": ACCENT,
        "activeforeground": "white"
    }
    
    # Botón de enviar
    SEND_BTN_ATTR = {
        "bg": ACCENT, 
        "fg": "white", 
        "relief": "flat", 
        "cursor": "hand2",
        "font": ("Segoe UI", 9, "bold"),
        "activebackground": "#005a9e"
    }

    # --- LAYOUT HELPERS ---
    # Usamos diccionarios para no repetir padx/pady en el código de la vista
    LAYOUT_FILL = {"expand": True, "fill": "both"}
    COMMON_PADS = {"padx": 10, "pady": 5}