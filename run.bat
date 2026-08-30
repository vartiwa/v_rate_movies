@echo off
echo ===================================================
echo Starting Fandango Rating Analytics Web Application...
echo ===================================================
start http://localhost:8000
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
