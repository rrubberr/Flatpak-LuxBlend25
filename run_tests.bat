
:: Running the unit tests requires the following python modules to be installed:
::
:: nose
:: mox   (python 3 version from https://github.com/e0ne/pymox/tree/python3)
:: coverage

@echo off
setlocal

set BLENDER_SCRIPTS_PATH=D:\bin\blender-2.68-RC1-windows64\2.67\scripts

set BLENDER_MODS=%BLENDER_SCRIPTS_PATH%\startup;%BLENDER_SCRIPTS_PATH%\modules;%BLENDER_SCRIPTS_PATH%\addons\modules

set PATH=src;%BLENDER_MODS%;%PATH%
set PYTHONPATH=%BLENDER_MODS%;%PYTHONPATH%

%PY3_64% -m nose --with-coverage --cover-package=luxrender --cover-erase tests
:: %PY3_64% -m nose --cover-package=luxrender --cover-erase tests
