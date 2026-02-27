@echo off
echo ============================================================
echo NAF_ISB - Extracteur de Documents - Interface Streamlit
echo ============================================================
echo.

REM Activer l'environnement virtuel si nécessaire
if exist "..\..\..\.venv\Scripts\activate.bat" (
    call "..\..\..\.venv\Scripts\activate.bat"
)

echo Demarrage de l'interface Streamlit...
echo.
echo L'interface s'ouvrira automatiquement dans votre navigateur
echo sur : http://localhost:8501
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo ============================================================
echo.

streamlit run interface\app.py

pause
