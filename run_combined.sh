#!/bin/bash
# Combined run script for Smart Tourism Analytics Platform
# Runs both Flask backend and Streamlit frontend

echo "=========================================="
echo "Smart Tourism Analytics Platform Launcher"
echo "=========================================="
echo ""
echo "[1] Starting Flask API backend on port 5000..."
python app.py &
FLASK_PID=$!

sleep 2

echo "[✓] Flask API is running (PID: $FLASK_PID)"
echo ""
echo "[2] Starting Streamlit frontend..."
echo "=========================================="
echo ""

# Run Streamlit in the foreground
python -m streamlit run streamlit_app.py --client.showErrorDetails=true

# Cleanup on exit
echo ""
echo "[INFO] Shutting down services..."
kill $FLASK_PID 2>/dev/null
echo "[✓] All services stopped"
