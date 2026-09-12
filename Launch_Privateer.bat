@echo off
cd /d "%~dp0"
python -m privateer
if errorlevel 1 pause
