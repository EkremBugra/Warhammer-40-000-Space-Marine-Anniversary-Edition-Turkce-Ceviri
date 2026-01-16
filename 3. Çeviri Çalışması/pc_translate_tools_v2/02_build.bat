@echo off
setlocal
cd /d "%~dp0"

REM Put original ucs.pc in this folder.
REM Drag & drop ucs_translate_TR.tsv onto this BAT.
py 02_build_pc.py "ucs.pc" "%~1" "ucs_tr.pc"

pause
