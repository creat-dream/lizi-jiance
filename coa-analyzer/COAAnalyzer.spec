# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# 添加数据文件
added_files = [
    ('config', 'config'),
    ('data', 'data'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PyQt6.sip',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'fitz',
        'fitz.fitz',
        'pandas',
        'pandas.core',
        'pandas.core.dtypes',
        'pandas.core.algorithms',
        'pandas.core.arrays',
        'pandas.core.indexes',
        'pandas.core.indexes.base',
        'pandas.core.frame',
        'pandas.core.series',
        'pandas.io',
        'pandas.io.excel',
        'pandas.io.formats',
        'pyqtgraph',
        'pyqtgraph.graphicsItems',
        'pyqtgraph.exporters',
        'requests',
        'requests.packages',
        'requests.packages.urllib3',
        'json',
        'os',
        'sys',
        'datetime',
        'typing',
        'glob',
        'shutil',
        'csv',
        'openpyxl',
        'openpyxl.cell',
        'openpyxl.worksheet',
        'openpyxl.workbook',
        'numpy',
        'numpy.core',
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
    name='COA试验报告分析系统',
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
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
