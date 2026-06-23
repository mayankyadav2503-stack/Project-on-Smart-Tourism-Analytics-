import streamlit as st

st.set_page_config(page_title="STAP", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    * { color: #e0e0e0 !important; }
    .stApp { background: #0a0a0a !important; }
    .main > div { padding: 0 1.5rem; }
    h1, h2, h3, h4 { color: #ffffff !important; }
    p, li, span, label, .stMarkdown { color: #cccccc !important; }
    .stButton>button {
        background: #1a1a2e !important; color: #e0e0e0 !important;
        border: 1px solid #333 !important; border-radius: 8px !important;
    }
    .stButton>button:hover { background: #16213e !important; border-color: #0f3460 !important; }
    .stTextInput>div>div>input, .stSelectbox>div>div, .stDateInput>div>div {
        background: #1a1a2e !important; color: #e0e0e0 !important;
        border: 1px solid #333 !important; border-radius: 8px !important;
    }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.8rem !important; }
    div[data-testid="stMetricLabel"] { color: #999 !important; }
    section[data-testid="stSidebar"] { background: #111 !important; border-right: 1px solid #222 !important; }
    section[data-testid="stSidebar"] .stButton>button {
        background: transparent !important; border: none !important;
        text-align: left !important; padding: 8px 16px !important;
        border-radius: 0 !important; width: 100% !important;
    }
    section[data-testid="stSidebar"] .stButton>button:hover { background: #1a1a2e !important; }
    .stTabs [data-baseweb="tab-list"] { background: #111 !important; border-bottom: 1px solid #333 !important; }
    .stTabs [data-baseweb="tab"] { color: #999 !important; }
    .stTabs [aria-selected="true"] { color: #fff !important; background: #1a1a2e !important; }
    div[data-testid="stExpander"] { background: #111 !important; border: 1px solid #222 !important; border-radius: 8px !important; }
    .stAlert { background: #1a1a2e !important; border: 1px solid #333 !important; color: #ccc !important; }
    .stDataFrame { background: #111 !important; }
    .st-eb { background: #1a1a2e !important; }
    hr { border-color: #333 !important; }
    .card {
        background: #111 !important; border: 1px solid #222 !important;
        border-radius: 12px; padding: 20px; margin: 10px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: #111; border: 1px solid #222; border-radius: 10px;
        padding: 16px; text-align: center;
    }
    div[role="alert"] { background: #1a1a2e !important; border: 1px solid #0f3460 !important; }
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

PAGES = {
    "dashboard": "📊 Dashboard",
    "recommendations": "🎯 Discover",
    "itinerary": "📋 Planner",
    "map": "🗺 Map",
    "chatbot": "🤖 Assistant",
}

with st.sidebar:
    st.markdown("<h2 style='text-align:center;color:#fff !important'>🌍 STAP</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#333'>", unsafe_allow_html=True)
    for key, label in PAGES.items():
        active = "1px solid #0f3460" if st.session_state.page == key else "transparent"
        if st.button(label, key=f"nav_{key}", width='stretch'):
            st.session_state.page = key
            st.rerun()
    st.markdown("<hr style='border-color:#333'>", unsafe_allow_html=True)
    st.caption("© 2026 STAP")

page = st.session_state.page

if page == "dashboard":
    from frontend.dashboard import show_dashboard
    show_dashboard()
elif page == "recommendations":
    from frontend.recommendations import show_recommendations
    show_recommendations()
elif page == "itinerary":
    from frontend.itinerary import show_itinerary
    show_itinerary()
elif page == "map":
    from frontend.map_view import show_map
    show_map()
elif page == "chatbot":
    from frontend.chatbot import show_chatbot
    show_chatbot()
