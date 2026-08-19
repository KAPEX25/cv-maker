# -*- mode: python ; coding: utf-8 -*-
"""macOS paket spec'i — CV-Olusturucu.app + .dmg üretir.

Kullanım (MAC üzerinde, proje klasöründe):
    pyinstaller CV-Olusturucu-mac.spec --noconfirm
"""
import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT, BUNDLE


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('fonts', 'fonts'),
        ('logos', 'logos'),
    ],
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='CV-Olusturucu',
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

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CV',
)

app = BUNDLE(
    coll,
    name='CV-Olusturucu.app',
    icon=os.path.join('logos', 'app.icns'),
    bundle_identifier='com.cvolusturucu.app',
    info_plist={
        'CFBundleName': 'CV Oluşturucu',
        'CFBundleDisplayName': 'CV Oluşturucu',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
    },
)