@echo off
title Plataforma SSMA - Gestao Integrada
echo ========================================
echo   Plataforma SSMA - Inicializando...
echo ========================================
echo.
cd /d %~dp0

REM Verifica se o ambiente virtual existe
if not exist "venv\" (
    echo [1/3] Criando ambiente virtual...
    python -m venv venv
)

echo [2/3] Ativando ambiente e instalando dependencias...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

echo [3/3] Iniciando Plataforma SSMA...
echo.
start "" http://localhost:8501
streamlit run app.py --server.port 8501

pause
