@echo off
echo ===========================================
echo  SkyLink Airlines - Installing dependencies
echo ===========================================
python -m venv venv
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Installation complete. Run "run.bat" to start the application.
pause
