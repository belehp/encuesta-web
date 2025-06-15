@echo off
echo 🚀 Iniciando aplicación de encuestas...
echo.

REM Activar entorno virtual
echo 📦 Activando entorno virtual...
call .\venv\Scripts\activate.bat

REM Verificar que Flask esté instalado
echo 🔍 Verificando instalación...
.\venv\Scripts\python.exe -c "import flask; print('✅ Flask instalado correctamente')" 2>nul
if errorlevel 1 (
    echo ❌ Flask no encontrado, instalando...
    .\venv\Scripts\pip.exe install Flask
)

REM Ejecutar aplicación
echo 🌐 Iniciando servidor...
echo.
echo 👉 Abre tu navegador en: http://127.0.0.1:5000
echo 👉 Presiona Ctrl+C para detener
echo.
.\venv\Scripts\python.exe run_local.py

pause
