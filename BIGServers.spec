# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None
base_path = os.getcwd()

# Asegurar que el icono existe antes de compilar
icon_path = os.path.join(base_path, 'data', 'logo.ico')
if not os.path.exists(icon_path):
    icon_path = os.path.join(base_path, 'logo.ico')

a = Analysis(
    ['main.py'],
    pathex=[base_path],
    binaries=[],
    datas=[
        ('.env', '.'),
        (icon_path, 'data') if os.path.exists(icon_path) else (icon_path, '.'),
    ],
    hiddenimports=[
        'psycopg2',
        'cryptography.fernet',
        'paramiko',
        'tkinter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'notebook', 'test'], # Excluimos basura para reducir peso
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
    console=False, # GUI pura
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    icon=icon_path if os.path.exists(icon_path) else None,
)