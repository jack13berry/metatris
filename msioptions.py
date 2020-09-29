
msi_options = {
  'install_icon': 'media/game-changer.ico',
  'data': {
    'Shortcut': [
      (
        #Shortcut                      Directory        Name            Component
        'DesktopShortcut',            'DesktopFolder', 'Game Changer', 'TARGETDIR',

        #Target                        Arguments        Description   Hotkey
        '[TARGETDIR]game-changer.exe', None,            None,         None,

        #Icon   IconIndex    ShowCmd     WkDir
        None,   None,         None,       'TARGETDIR'
      ),

      (
        #Shortcut                      Directory        Name            Component
        'StartupShortcut',            'StartupFolder', 'Game Changer', 'TARGETDIR',

        #Target                        Arguments    Description   Hotkey
        '[TARGETDIR]game-changer.exe', None,        None,         None,

        #Icon   IconIndex    ShowCmd     WkDir
        None,   None,         None,       'TARGETDIR'
      )

    ]
  },
}
