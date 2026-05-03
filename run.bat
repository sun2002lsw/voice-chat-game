@echo off
cd /d "%~dp0"

call tts\run.bat
if errorlevel 1 (
    echo TTS failed.
    pause
    exit /b 1
)

start "voice-chat-game backend" cmd /k "%~dp0backend\run.bat"
start "voice-chat-game frontend" cmd /k "%~dp0frontend\run.bat"
