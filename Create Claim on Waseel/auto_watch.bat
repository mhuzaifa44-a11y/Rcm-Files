@echo off
title Waseel Claim Auto-Watcher (Live Folder Monitor)
cd /d "%~dp0"
echo ======================================================================
echo             WASEEL NPHIES AUTO-WATCHER (LIVE MONITOR)
echo ======================================================================
echo.
echo Whenever you copy or paste any JSON files into this folder,
echo the system will automatically detect them and extract to Waseel!
echo.
python create_and_extract_waseel.py --watch
pause
