@echo off
:: Drag a .txt or .md file onto this batch file to summarize it.
:: "%~dp0" is the folder this batch file is sitting in.

echo straining...
echo ---------------------------------------------------

python -m strainer "%~1"

echo.
echo ---------------------------------------------------
echo Done.
pause
