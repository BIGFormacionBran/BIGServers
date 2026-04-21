# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Definir la ruta base para asegurar que encuentre los archivos
base_path = os.getcwd()

a = Analysis(
    ['main.py'],
    pathex=[base_path],
    binaries=[],
    datas=[
        ('.env', '.'),           # Archivo de configuración (DATABASE_URL, etc)
        # Si tienes una carpeta de assets o iconos, añádela aquí:
        # ('gui/assets', 'gui/assets'), 
    ],
    hiddenimports=[
        'psycopg2',
        'cryptography.fernet',
        'cryptography.hazmat.backends.openssl',
        'paramiko',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BIGServers',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Falso para que sea una aplicación de ventana pura (GUI)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.ico' if os.path.exists('logo.ico') else None,
)