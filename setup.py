import sys
sys.path.insert(0, r'.\extlib')

from cx_Freeze import setup, Executable
from msioptions import msi_options

exe_options = {
  'includes': [
    'attr',
    'constantly',
    'incremental',
    'twisted',
    'zope',
    'simulator',
    'zoid'
  ],
  'include_files': [
    'boards',
    'configs',
    'controllers',
    'media'
  ]
}

#base = 'Console'
base = 'Win32GUI'

executables = [
  Executable(
    'main.py',
    base=base,
    targetName = 'game-changer',
    shortcutName = 'Game Changer',
    shortcutDir = 'StartupFolder',
    icon = 'media/game-changer.ico'
  )
]

setup(
  name='Game Changer',
  version = '1.0',
  description = '',
  options = {'build_exe': exe_options, 'bdist_msi':msi_options},
  executables = executables
)
