#!/bin/bash
export PYTHONPATH=/app
rm -rf /app/.adk

echo "Starting ADK UI from project root (Official Mode)..."
# Point to project root so 'app' is discovered as an application
adk web . --host 0.0.0.0 --port 8003 > /app/adk_web.log 2>&1 &

echo "Starting API..."
python main.py
