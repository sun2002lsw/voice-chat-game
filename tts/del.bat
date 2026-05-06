@echo off
cd /d "%~dp0.."
powershell -Command "Get-ChildItem '.scenario' -Recurse -Filter '*.wav' | Remove-Item -Force"
echo Done.
pause
