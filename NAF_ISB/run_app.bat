@echo off
REM ============================================================
REM  run_app.bat – Lance l'interface web Streamlit
REM  Double-cliquez sur ce fichier pour ouvrir l'application.
REM ============================================================

cd /d "%~dp0"
echo.
echo === NAF_ISB – Lancement de l'interface web ===
echo.
echo L'application va s'ouvrir dans votre navigateur...
echo.

streamlit run app.py

pause
