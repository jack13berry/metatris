@echo off

del config\user.config
REM python setup.py build
REM python setup.py build_exe
python setup.py bdist_msi
