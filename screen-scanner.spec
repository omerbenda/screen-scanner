# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, copy_metadata

# Collect all torchvision C++ binaries, metadata, and hidden imports
tv_datas, tv_binaries, tv_hiddenimports = collect_all('torchvision')

datas = [('models', 'models')]
datas += copy_metadata('screen-scanner')
datas += copy_metadata('ultralytics')
datas += tv_datas

a = Analysis(
    ['src/screen_scanner/main.py'],
    pathex=['src/screen_scanner'],
    binaries=[*tv_binaries],
    datas=datas,
    hiddenimports=[*tv_hiddenimports],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='screen-scanner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
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
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='screen-scanner',
)
