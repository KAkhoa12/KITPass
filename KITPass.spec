# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['K:\\Project\\KITPass\\src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('K:\\Project\\KITPass\\data', 'data')],
    hiddenimports=['pyperclip'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='KITPass',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
