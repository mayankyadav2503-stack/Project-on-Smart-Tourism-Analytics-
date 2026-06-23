# Smart Tourism Analytics Platform - Deployment Guide

## Local Deployment (Development)

### Option 1: Using Python Combined Runner (Recommended for local testing)
```bash
python run_combined.py
```
This runs both Flask backend (port 5000) and Streamlit frontend (port 8501) simultaneously.

### Option 2: Using Shell Script (Linux/Mac)
```bash
chmod +x run_combined.sh
./run_combined.sh
```

### Option 3: Using Batch Script (Windows)
```cmd
run_combined.bat
```

### Option 4: Manual - Run Separately in Different Terminals

**Terminal 1 - Flask Backend:**
```bash
python app.py
```
Backend runs on `http://localhost:5000`

**Terminal 2 - Streamlit Frontend:**
```bash
streamlit run streamlit_app.py
```
Frontend runs on `http://localhost:8501`

---

## Streamlit Cloud Deployment

### Prerequisites
- Streamlit Cloud account (https://streamlit.io/cloud)
- GitHub repository with your code

### Setup Steps

1. **Create `requirements.txt`** (Already created in your project)
   - Ensure all dependencies are listed

2. **Create Procfile** (Already created)
   - Defines how services run on Streamlit Cloud

3. **Create `.streamlit/config.toml`** (Already created)
   - Configures Streamlit behavior for cloud

4. **Connect to Streamlit Cloud:**
   - Push your code to GitHub
   - Go to https://share.streamlit.io/
   - Click "New App"
   - Select your repository and main file: `streamlit_app.py`
   - Deploy

### Important Notes for Streamlit Cloud

- **Port Configuration**: Streamlit Cloud handles port assignment automatically
- **Backend Access**: Update `streamlit_app.py` to use the correct API endpoint:
  ```python
  # For cloud deployment, use environment-aware endpoints
  import os
  API_URL = os.getenv("API_URL", "http://localhost:5000")
  ```

- **Environment Variables**: Set via Streamlit Cloud dashboard under App settings

- **One-Click Deploy Issue**: Streamlit Cloud currently focuses on single Python apps. For dual processes:
  - Use the Procfile approach (if supported)
  - Or embed Flask backend initialization in Streamlit app using `launcher.py`

### Advanced: Multi-Process on Streamlit Cloud

If Streamlit Cloud doesn't support multiple processes via Procfile, embed backend startup in your Streamlit app:

```python
# Add to streamlit_app.py
import streamlit as st
from launcher import AppLauncher

# Initialize backend on first run
if "backend_started" not in st.session_state:
    launcher = AppLauncher()
    launcher.start_flask()
    st.session_state.backend_started = True

# Rest of your Streamlit code...
```

---

## Files Created

| File | Purpose |
|------|---------|
| `run_combined.py` | Python launcher (cross-platform) |
| `run_combined.sh` | Shell script (Linux/Mac) |
| `run_combined.bat` | Batch script (Windows) |
| `.streamlit/config.toml` | Streamlit configuration |
| `Procfile` | Deployment process definition |
| `launcher.py` | Backend startup helper |

---

## Troubleshooting

**Flask not starting:**
- Check if port 5000 is already in use: `lsof -i :5000` (Linux/Mac)
- Kill existing process and retry

**Streamlit connection issues:**
- Verify Flask is running on `http://localhost:5000`
- Check API endpoint URLs in `streamlit_app.py`
- Review network/firewall settings

**Streamlit Cloud deployment fails:**
- Ensure `requirements.txt` has all dependencies
- Check GitHub repository structure
- Review Streamlit Cloud deployment logs

---

## Environment Variables (Streamlit Cloud)

Set these in Streamlit Cloud Dashboard > Settings > Secrets:

```toml
# secrets.toml
FLASK_ENV = "production"
API_URL = "https://your-backend-url.com"
```

Access in code:
```python
import streamlit as st
api_url = st.secrets.get("API_URL", "http://localhost:5000")
```
