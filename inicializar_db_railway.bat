@echo off
title 🚀 Inicializar Base de Datos en Railway

echo ============================
echo 🔗 Iniciando conexión con PostgreSQL en Railway...
echo ============================

REM Activar entorno virtual
call .\venv\Scripts\activate.bat

REM Ejecutar script de creación de base de datos
echo 🛠️ Ejecutando crear_db_railway.py...
py crear_db_railway.py

echo.
echo ✅ Proceso finalizado.
pause
