@echo off
title Waseel Claim Creator & Automated Batch Extractor
cd /d "%~dp0"
echo ======================================================================
echo          WASEEL NPHIES CLAIM CREATOR & AUTOMATED EXTRACTOR
echo                Saudi German Hospital - Jeddah
echo ======================================================================
echo.
echo Checking for claim JSON files in this folder...
echo.
python create_and_extract_waseel.py
echo.
echo ======================================================================
echo Process finished. Check summary above.
echo ======================================================================
pause
