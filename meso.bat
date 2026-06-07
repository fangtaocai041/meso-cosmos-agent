@echo off
setlocal
set "MESO_ROOT=%~dp0"
python "%MESO_ROOT%src\main.py" %*
endlocal
