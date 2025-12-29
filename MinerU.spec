# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Analysis phase - specify all files and dependencies
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.ini.example', '.'),
        ('mineru_icon.svg', '.'),
        ('src/ui/styles/*.qss', 'src/ui/styles'),
    ],
    hiddenimports=[
        # PySide6 core modules
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',

        # Application modules from src/
        'src',
        'src.ui',
        'src.ui.main_window',
        'src.ui.settings_dialog',
        'src.services',
        'src.services.api_client',
        'src.services.batch_service',
        'src.config',
        'src.config.config_manager',
        'src.config.constants',
        'src.models',
        'src.models.batch',
        'src.models.processing_options',
        'src.workers',
        'src.workers.upload_worker',
        'src.workers.polling_worker',
        'src.utils',
        'src.utils.logging_config',

        # Keyring backends for secure token storage
        'keyring.backends.SecretService',
        'keyring.backends.kwallet',
        'keyring.backends',

        # Other dependencies
        'requests',
    ],
    hookspath=[],
    hooksconfig={
        'cryptography': {
            # Skip problematic cryptography submodules
            'module_collection_mode': 'pyz+py'
        }
    },
    runtime_hooks=[],
    excludes=[
        # Exclude problematic modules that aren't needed
        'test',
        'tests',
        # Note: distutils removed - setuptools provides shim in Python 3.12+
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ phase - create a compressed archive of Python modules
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE phase - create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MinerU',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window (GUI application)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
