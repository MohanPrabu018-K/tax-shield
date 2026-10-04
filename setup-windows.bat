@echo off
REM Tax Shield - Windows setup (CMD)
REM Run from the project root:  setup-windows.bat
setlocal
cd /d "%~dp0"

echo ==^> Checking Python...
py --version || python --version

echo ==^> Checking Node...
node --version
npm --version

echo ==^> Backend: creating .venv...
if not exist "backend\.venv" py -m venv backend\.venv
call "backend\.venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
call deactivate

if not exist "backend\.env" (
  echo ==^> Creating backend\.env from .env.example
  copy "backend\.env.example" "backend\.env"
) else (
  echo ==^> backend\.env already exists, leaving it.
)

if not exist "backend\uploads" mkdir "backend\uploads"

echo ==^> Frontend: npm install...
cd /d "%~dp0frontend"
if exist ".next" rmdir /s /q ".next"
call npm install

cd /d "%~dp0"
echo.
echo Setup complete.
echo Backend : run-backend.bat  (http://localhost:8000/docs)
echo Frontend: open a second terminal -^> cd frontend ^& npm run dev  (http://localhost:3000)
echo MongoDB : install MongoDB 6+ for Windows or run: docker compose up -d mongodb
