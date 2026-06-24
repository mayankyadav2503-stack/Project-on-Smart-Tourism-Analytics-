"""
Render startup — runs Flask backend (thread) + Streamlit frontend (subprocess)
in a single container so both fit on Render's free tier.
"""
import os, sys, threading, subprocess, time

FLASK_PORT = 5000

def start_flask():
    os.environ["FLASK_DEBUG"] = "0"
    from database.schema import init_db
    from database.seed_data import seed_database
    init_db()
    seed_database()

    from app import app
    print(f"[startup] Flask running on internal port {FLASK_PORT}")
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    # Boot Flask in a daemon thread
    t = threading.Thread(target=start_flask, daemon=True)
    t.start()
    time.sleep(3)  # give Flask a moment to start

    # Launch Streamlit on Render's assigned port
    port = os.environ.get("PORT", "8501")
    print(f"[startup] Launching Streamlit on port {port}")
    sys.exit(subprocess.call([
        sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
        "--server.port", port,
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
    ]))
