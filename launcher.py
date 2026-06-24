#!/usr/bin/env python
"""
Streamlit Cloud optimized launcher
This script should be referenced in streamlit_app.py as the startup handler
"""

import subprocess
import sys
import os
import time
from pathlib import Path

class AppLauncher:
    """Manages both Flask backend and Streamlit frontend"""
    
    def __init__(self):
        self.flask_process = None
        self.script_dir = Path(__file__).parent.absolute()
    
    def start_flask(self
        """Start Flask backend as daemon"""
        if self.flask_process is None:
            try:
                self.flask_process = subprocess.Popen(
                    [sys.executable, str(self.script_dir / "app.py")],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
                time.sleep(2)
                print("✓ Flask backend started (port 5000)")
            except Exception as e:
                print(f"✗ Failed to start Flask: {e}")
                return False
        return True
    
    def stop_flask(self):
        """Stop Flask backend"""
        if self.flask_process:
            try:
                self.flask_process.terminate()
                self.flask_process.wait(timeout=5)
            except:
                self.flask_process.kill()
            self.flask_process = None

if __name__ == "__main__":
    launcher = AppLauncher()
    launcher.start_flask()
