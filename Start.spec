# -*- mode: python -*-

block_cipher = None


a = Analysis(['Start.py'],
             pathex=['/Users/Malte/SNARE/v0.3'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

a.datas += [ ('EditorUI/Marker.png', '/Users/Malte/SNARE/v0.3/EditorUI/Marker.png', 'DATA')]
a.datas += [ ('EditorUI/Lock.png', '/Users/Malte/SNARE/v0.3/EditorUI/Lock.png', 'DATA')]
a.datas += [ ('EditorUI/Unlock.png', '/Users/Malte/SNARE/v0.3/EditorUI/Unlock.png', 'DATA')]
a.datas += [ ('AnalyzeTools/NominalData.csv', '/Users/Malte/SNARE/v0.3/AnalyzeTools/NominalData.csv', 'DATA')]
a.datas += [ ('icon.icns', '/Users/Malte/SNARE/v0.3/icon.icns', 'DATA')]
a.datas += [ ('icon.ico', '/Users/Malte/SNARE/v0.3/icon.ico', 'DATA')]

# a.datas += [ ('EditorUI/Marker.png', 'C:\\PythonExperiments\\SNARE\\v0.3\\EditorUI\\Marker.png', 'DATA')]
# a.datas += [ ('EditorUI/Lock.png', 'C:\\PythonExperiments\\SNARE\\v0.3\\EditorUI\\Lock.png', 'DATA')]
# a.datas += [ ('EditorUI/Unlock.png', 'C:\\PythonExperiments\\SNARE\\v0.3\\EditorUI\\Unlock.png', 'DATA')]
# a.datas += [ ('AnalyzeTools/NominalData.csv', ''C:\\PythonExperiments\\SNARE\\v0.3\\AnalyzeTools\\NominalData.csv', 'DATA')]
# a.datas += [ ('icon.icns', 'C:\\PythonExperiments\\SNARE\\v0.3\\icon.icns', 'DATA')]
# a.datas += [ ('icon.ico', 'C:\\PythonExperiments\\SNARE\\v0.3\\icon.ico', 'DATA')]

             
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='SNARE',
          icon='icon.ico',
          debug=False,
          strip=False,
          upx=True,
          console=False )
          
app = BUNDLE(exe,
             name='SNARE.app',
             icon='icon.icns',
             version='0.3',
             debug=True,
             strip=False,
             upx=True,
             console=True,
             bundle_identifier=None)
