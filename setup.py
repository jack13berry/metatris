import sys
sys.path.insert(0, r'.\extlib')

from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {
  'includes': [
    'attr',
    'constantly',
    'incremental',
    'twisted',
    'zope',
    'simulator',
    'zoid'
  ]
} # 'packages': [], 'excludes': []}

#base = 'Console'
base = 'Win32GUI'

executables = [
  Executable(
    'main.py',
    base=base,
    targetName = 'game-changer'
  )
]

setup(
  name='Game Changer',
  version = '1.0',
  description = '',
  options = {'build_exe': build_options},
  executables = executables
)
