#!/usr/bin/env bash
set -e

echo "==================================================="
echo "Starting Fandango Rating Analytics Web Application..."
echo "==================================================="

# Automatically open browser
if which xdg-open > /dev/null; then
  xdg-open http://localhost:8000 &
elif which open > /dev/null; then
  open http://localhost:8000 &
fi

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
