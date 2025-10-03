@echo off
REM Запуск бекенду у новому вікні на всіх інтерфейсах
start "Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM Затримка, щоб бекенд встиг стартувати (5 секунд)
timeout /t 5 /nobreak >nul

REM Запуск фронтенду у новому вікні
start "Frontend" cmd /k "cd /d %~dp0frontend && npm start"

REM Відкрити браузер (опційно)
REM start http://localhost:3000

exit