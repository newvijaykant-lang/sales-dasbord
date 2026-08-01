@echo off
cd /d "%~dp0"
title Pulse Sales Analytics
where py >nul 2>nul
if %errorlevel%==0 (
    py -m streamlit run app.py
) else (
    python -m streamlit run app.py
)
pause
