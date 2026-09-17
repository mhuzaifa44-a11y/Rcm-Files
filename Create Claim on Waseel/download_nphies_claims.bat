@echo off
title NPHIES Bulk Claim Request Downloader
cd /d "%~dp0"
echo ========================================================
echo       NPHIES BULK CLAIM REQUEST DOWNLOADER
echo ========================================================
echo.
python "%~dp0nphies_bulk_downloader.py"
echo.
echo Process completed. Press any key to exit.
pause >nul
