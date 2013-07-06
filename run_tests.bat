
:: Running the unit tests requires the following python modules to be installed:
::
:: nose
:: mox   (python 3 version from https://github.com/e0ne/pymox/tree/python3)
:: coverage

@echo off
setlocal

set BLENDER_SCRIPTS_PATH=D:\bin\blender-2.68-RC1-windows64\2.67\scripts

set PATH=src;%BLENDER_SCRIPTS_PATH%\startup;%BLENDER_SCRIPTS_PATH%\modules;%PATH%
set PYTHONPATH=%PYTHONPATH%;%PATH%
set LUXBLEND_NO_REGISTER=1

:: %PY3_64% -m nose --with-coverage --cover-package=luxrender --cover-erase tests

%PY3_64% -m nose tests

