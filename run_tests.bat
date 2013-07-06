
:: Running the unit tests requires the following python modules to be installed:
::
:: nose
:: mox   (python 3 version from https://github.com/e0ne/pymox/tree/python3)
:: coverage

@echo off

%PY3_64% -m nose --with-coverage --cover-package=luxrender tests 
