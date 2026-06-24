import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS
from database.schema import init_db
from database.seed_data import seed_database
from api.recommend_routes import recommend_bp
from api.chat_routes import chat_bp
from api.travel_routes import travel_bp

app = Flask(__name__)
app.config.from_object("config")
CORS(app)

app.register_blueprint(recommend_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(travel_bp)

@app.route("/")
def index():
    return {"status": "Smart Tourism Analytics Platform API", "version": "1.0.0"}

@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)

@app.route("/api/health")
def health():
    return {"status": "healthy", "message": "All systems operational"}

if __name__ == "__main__":
    is_streamlit = any("streamlit" in m.lower() for m in sys.modules) or "STREAMLIT_SCRIPT" in os.environ
    is_production = os.environ.get("FLASK_DEBUG", "1") == "0"
    if is_streamlit and not is_production:
        print("[Hint] Run 'streamlit run streamlit_app.py' for the frontend, and 'python app.py' for the Flask API.")
    else:
        debug = not is_production
        init_db()
        seed_database()
        print(f"[Flask] Starting API on http://127.0.0.1:5000 {'(production)' if is_production else '(debug)'}")
        app.run(host="0.0.0.0", port=5000, debug=debug)
