#!/usr/bin/env python
"""
Combined run script for Smart Tourism Analytics Platform
Runs both Flask backend and Streamlit frontend
"""

import subprocess
import sys
import os
import time
import signal

def run_combined():
    """Start both Flask backend and Streamlit frontend"""
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("=" * 60)
    print("Smart Tourism Analytics Platform - Combined Launcher")
    print("=" * 60)
    
    # Start Flask backend in a subprocess
    print("\n[1] Starting Flask API backend on port 5000...")
    flask_process = subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Give Flask a moment to start
    time.sleep(2)
    
    # Check if Flask started successfully
    if flask_process.poll() is not None:
        print("[ERROR] Flask failed to start!")
        sys.exit(1)
    
    print("[✓] Flask API is running on http://localhost:5000")
    
    # Start Streamlit frontend
    print("\n[2] Starting Streamlit frontend...")
    print("=" * 60)
    
    try:
        streamlit_process = subprocess.run(
            [sys.executable, "-m", "streamlit", "run", "streamlit_app.py", 
             "--client.showErrorDetails=true"],
            cwd=script_dir
        )
    except KeyboardInterrupt:
        print("\n\n[INFO] Shutting down...")
    finally:
        # Cleanup: terminate Flask process
        print("\n[INFO] Stopping Flask backend...")
        flask_process.terminate()
        try:
            flask_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            flask_process.kill()
        print("[✓] All services stopped")

if __name__ == "__main__":
    run_combined()
