@echo off
echo 🚀 Iniciando aplicación con preguntas actualizadas...
echo.

REM Primero crear la nueva base de datos
echo 📝 Creando base de datos nueva...
call .\venv\Scripts\activate.bat
.\venv\Scripts\python.exe crear_db_nueva.py

echo.
echo 🌐 Iniciando servidor...
echo.
echo 👉 Abre tu navegador en: http://127.0.0.1:5000
echo 👉 Presiona Ctrl+C para detener
echo.
.\venv\Scripts\python.exe run_local.py

pause
