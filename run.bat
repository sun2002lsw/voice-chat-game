@echo off
cd /d "%~dp0"

start "voice-chat-game backend" cmd /k "%~dp0backend\run.bat"
start "voice-chat-game frontend" cmd /k "%~dp0frontend\run.bat"
