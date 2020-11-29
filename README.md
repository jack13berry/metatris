# MetaTetris Frontend

This repository contains the source code of the game and environment setup for
creation of Windows installers for both 32bit and 64bit platforms.

## Dependencies

Make sure you have Python3.8 installed as default Python interpreter on your
system. Python dependency is only for the process of creating the installer.
The installer created will have a completely contained version of Python
with all the necessary dependencies for the game to work, so end users will not
need to have anything other than the installer itself.

## Creating the Installer

1. Once the repository is downloaded, open a cmd window, cd into the folder
where this README.md file is.
2. Call `install.bat`. This will install the Python libraries needed.
3. Call `build.bat`. This will create a `dist` folder where you will find the
installer for the game.

The installer created will be 64bit or 32bit reflecting your own Windows.
Cross-compiling does not work with the current version of Python libraries that
are used for building the installer, so to build a 32bit installer, you need to
be on a 32bit Windows machine and the same for 64bit.
