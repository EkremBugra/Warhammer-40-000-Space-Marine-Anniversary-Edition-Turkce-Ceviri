@echo off
setlocal
cd /d "%~dp0"

REM Drag & drop .pc file onto this BAT
py 01_unpack.py "%~1"

pause
