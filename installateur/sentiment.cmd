@echo off
setlocal
set "PYTHONUTF8=1"
"%~dp0python\python.exe" -m sentiment_app %*
exit /b %errorlevel%
