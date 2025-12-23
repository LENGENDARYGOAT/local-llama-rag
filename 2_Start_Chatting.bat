@echo off
cd /d "%~dp0"
echo Starting Web Interface...
python -m streamlit run app.py
pause