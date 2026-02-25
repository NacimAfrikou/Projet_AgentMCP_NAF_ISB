@echo off
REM ============================================================
REM  run_all.bat – Lance TOUT le programme NAF_ISB
REM  1. Extraction batch (ligne de commande)
REM  2. Interface web Streamlit
REM ============================================================

cd /d "%~dp0"
echo.
echo ============================================================
echo         NAF_ISB - Programme Complet
echo ============================================================
echo.
echo Choisissez une option :
echo.
echo [1] Extraction batch (ligne de commande - data/input)
echo [2] Interface web Streamlit (navigateur)
echo [3] Les DEUX (extraction puis interface)
echo [4] Quitter
echo.
set /p choice="Votre choix (1-4) : "

if "%choice%"=="1" goto batch
if "%choice%"=="2" goto streamlit
if "%choice%"=="3" goto both
if "%choice%"=="4" goto end

echo.
echo Choix invalide. Veuillez entrer 1, 2, 3 ou 4.
echo.
pause
goto end

:batch
echo.
echo === Lancement de l'extraction batch ===
echo.
python -m code_source.main
echo.
pause
goto end

:streamlit
echo.
echo === Lancement de l'interface Streamlit ===
echo.
echo L'application va s'ouvrir dans votre navigateur...
echo.
python -m streamlit run app.py
goto end

:both
echo.
echo === Lancement de l'extraction batch ===
echo.
python -m code_source.main
echo.
echo === Extraction terminee ! ===
echo.
echo === Lancement de l'interface Streamlit ===
echo.
echo L'application va s'ouvrir dans votre navigateur...
echo.
python -m streamlit run app.py
goto end

:end
