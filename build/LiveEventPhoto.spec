# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Live Event Photography Mac App
"""

import os
from pathlib import Path

block_cipher = None

# Get the project directory
project_dir = os.path.dirname(os.path.abspath(SPEC))

# Data files to include
datas = [
    (os.path.join(project_dir, 'templates'), 'templates'),
    (os.path.join(project_dir, 'assets'), 'assets'),
    (os.path.join(project_dir, 'index.html'), '.'),
    (os.path.join(project_dir, 'server.py'), '.'),
]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.lifespan.off',
    'PIL._tkinter_finder',
    'multipart',
    'python_multipart',
]

a = Analysis(
    ['mac_app.py'],
    pathex=[project_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='LiveEventPhoto',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LiveEventPhoto',
)

app = BUNDLE(
    coll,
    name='Live Event Photo.app',
    icon=None,  # Will add icon later if available
    bundle_identifier='com.liveevent.photo',
    info_plist={
        'CFBundleName': 'Live Event Photo',
        'CFBundleDisplayName': 'Live Event Photo',
        'CFBundleVersion': '2.3.0',
        'CFBundleShortVersionString': '2.3',
        'LSUIElement': True,  # Hide from dock (menu bar app)
        'NSHighResolutionCapable': True,
    },
)
