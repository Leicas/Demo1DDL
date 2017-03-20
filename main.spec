# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['D:\\owncloudisir\\workspace\\Demo1DDL'],
             binaries=[('D:\\Users\\antoine\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages\\glumpy', 'glumpy')],
             datas=[('*.png', '.' ),( 'ftdi1.dll', '.' ),( 'freetype.dll', '.' )],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='main',
          debug=False,
          strip=False,
          upx=True,
          console=True )