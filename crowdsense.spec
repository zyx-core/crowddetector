# Optimized PyInstaller spec - reduces size from 2.3GB to ~300MB
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Exclude unnecessary packages to reduce size
excludes = [
    'tensorflow',           # Not needed (failed conversion)
    'tensorboard',
    'keras',
    'matplotlib',
    'pandas',
    'scipy',
    'jupyter',
    'notebook',
    'IPython',
    'pytest',
    'sphinx',
    'PIL.ImageQt',         # Qt not needed
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',
    'tkinter',
]

a = Analysis(
    ['desktop_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('web', 'web'),
        ('best.pt', '.'),
        ('config.yaml', '.'),
    ],
    hiddenimports=[
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
        'ultralytics',
        'cv2',
        'numpy',
        'torch',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,  # Exclude unnecessary packages
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove CUDA libraries if not needed (CPU-only mode)
# Uncomment these lines to reduce size further (CPU-only, ~200MB)
# a.binaries = [x for x in a.binaries if not x[0].startswith('torch/lib/cuda')]
# a.binaries = [x for x in a.binaries if not x[0].startswith('nvidia')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CrowdSense',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,              # Compress with UPX
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
