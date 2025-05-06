# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['rtsports_scraper.py'],
    pathex=[],
    binaries=[],
    datas=[('/Users/ryanwallman/Desktop/CodingProjects/rtSportsScraper/chromedriver', 'chromedriver')],
    hiddenimports=['selenium', 'bs4', 'pandas', 'webdriver_manager'],
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
    name='rtsports_scraper',
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
app = BUNDLE(
    exe,
    name='rtsports_scraper.app',
    icon=None,
    bundle_identifier=None,
)
