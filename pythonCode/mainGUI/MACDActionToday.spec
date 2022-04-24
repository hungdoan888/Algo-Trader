# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['paths=C:\\Users\\hungd\\Desktop\\MACD\\MACD\\pythonCode\\MACDActionToday', '--paths=C:\\Users\\hungd\\Desktop\\MACD\\MACD\\pythonCode\\MACDBacktester', '--paths=C:\\Users\\hungd\\Desktop\\MACD\\MACD\\pythonCode\\MACDResearch', '--paths=C:\\Users\\hungd\\Desktop\\MACD\\MACD\\pythonCode\\MACDTDAmeritrade', '--paths=C:\\Users\\hungd\\Desktop\\MACD\\MACD\\pythonCode\\mainGUI', '--paths=C:\\Users\\hungd\\Desktop\\MACD\\MACD\\pythonCode\\simulateReturns', '--paths=C:\\Users\\hungd\\Desktop\\MACD\\MACD\\pythonCode\\TDAmeritrade', 'main.py'],
             pathex=['C:/Users/hungd/Desktop/MACD/MACD/pythonCode/commonScripts'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='MACDActionToday',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='MACDActionToday')
