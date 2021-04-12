
msi_options = {
  'install_icon': 'media/metatris.ico',
  'upgrade_code': "{36173754-973f-4ae0-8005-d9ad447a9711}",
  'data': {
    'Shortcut': [
      (
        #Shortcut            Directory          Name            Component
        'DesktopShortcut',  'DesktopFolder',   'Metatris',      'TARGETDIR',

        #Target                      Arguments    Description   Hotkey
        '[TARGETDIR]metatris.exe',   None,        None,         None,

        #Icon   IconIndex    ShowCmd   WkDir
        None,   None,        None,     'TARGETDIR'
      ),

      (
        #Shortcut            Directory            Name        Component
        'StartMenu',        'ProgramMenuFolder', 'MetaTris',  'TARGETDIR',

        #Target                      Arguments    Description   Hotkey
        '[TARGETDIR]metatris.exe',   None,        None,         None,

        #Icon   IconIndex    ShowCmd   WkDir
        None,   None,        None,     'TARGETDIR'
      )

    ]
  },
}
