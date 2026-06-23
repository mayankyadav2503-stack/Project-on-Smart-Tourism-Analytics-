import streamlit as st
import requests

API = "http://127.0.0.1:5000/api"

def show_home():
    st.markdown("<h1 style='text-align:center'>🌍 Smart Tourism Analytics Platform</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#888;font-size:1.1em'>AI-Powered Travel Discovery & Planning System</p>", unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    try:
        trends = requests.get(f"{API}/trends", timeout=5).json()
        cat_dist = trends.get("category_distribution", [])
        hs = trends.get("hotel_stats", {})
        top = trends.get("top_destinations", [])
    except:
        cat_dist, hs, top = [], {}, []
    with k1: st.markdown(f"<div class='metric-card'><span style='font-size:2rem'>🗺</span><br><span style='font-size:1.5rem;color:#fff'>{len(cat_dist) or 15}</span><br><span style='color:#888'>Destinations</span></div>", unsafe_allow_html=True)
    with k2: st.markdown(f"<div class='metric-card'><span style='font-size:2rem'>🏨</span><br><span style='font-size:1.5rem;color:#fff'>${hs.get('avg_hotel_price',0):.0f}</span><br><span style='color:#888'>Avg Hotel</span></div>", unsafe_allow_html=True)
    with k3: st.markdown(f"<div class='metric-card'><span style='font-size:2rem'>📊</span><br><span style='font-size:1.5rem;color:#fff'>{len(cat_dist)}</span><br><span style='color:#888'>Categories</span></div>", unsafe_allow_html=True)
    with k4: st.markdown(f"<div class='metric-card'><span style='font-size:2rem'>✈️</span><br><span style='font-size:1.5rem;color:#fff'>{sum(d.get('bookings',0) for d in top) if top else 'N/A'}</span><br><span style='color:#888'>Bookings</span></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["🔥 Popular Destinations", "🌤 Live Weather", "🗺 Explore"])

    with t1:
        popular = []
        try:
            r = requests.get(f"{API}/recommendations/popular?limit=9", timeout=5)
            popular = r.json()
        except:
            pass
        if popular:
            cols = st.columns(3)
            for i, item in enumerate(popular):
                d = item["destination"]
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class='card'>
                        <h4 style='margin:0 0 4px 0'>{d['name']}</h4>
                        <p style='margin:2px 0;color:#888'>📍 {d['city']}, {d['country']}</p>
                        <p style='margin:2px 0'>⭐ {d['avg_rating']}/5 · 💬 {d['review_count']} reviews</p>
                        <p style='margin:2px 0'>🏷 {d['category'].title()} · 🔥 Score: <b>{item['score']:.1f}</b></p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"View {d['name']}", key=f"home_dest_{d['id']}", width='stretch'):
                        st.session_state["selected_dest"] = d["id"]
                        st.session_state.page = "map"
                        st.rerun()
        else:
            st.info("Loading destinations...")

    with t2:
        city = st.text_input("Enter city for weather", "Paris", key="home_weather_city")
        if city:
            try:
                w = requests.get(f"{API}/weather", params={"city": city}, timeout=5).json()
                if w.get("temperature"):
                    c1, c2 = st.columns([1,2])
                    with c1:
                        icon_map = {"01d":"☀️","02d":"⛅","03d":"☁️","04d":"☁️","09d":"🌧","10d":"🌦","11d":"⛈","13d":"❄️","50d":"🌫"}
                        st.markdown(f"<div style='font-size:4em;text-align:center'>{icon_map.get(w.get('icon',''),'🌤')}</div>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"<h3>{w['city']}, {w.get('country','')}</h3>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:#ccc'><b>{w['temperature']}°C</b> (feels like {w['feels_like']}°C)<br>☁ {w['description'].title()} · 💧 {w['humidity']}% · 💨 {w['wind_speed']} m/s</p>", unsafe_allow_html=True)
            except:
                st.info("Weather data unavailable")

    with t3:
        c1, c2 = st.columns([3,1])
        with c2:
            search_q = st.text_input("Search destinations", placeholder="e.g., Paris, Tokyo...")
            selected_cat = st.selectbox("Filter by category", ["All","landmark","museum","beach","nature","temple","shopping","park","island"])
        with c1:
            dests = []
            try:
                if search_q:
                    dests = requests.get(f"{API}/search", params={"q": search_q}, timeout=5).json()
                else:
                    dests = requests.get(f"{API}/destinations", timeout=5).json()
            except:
                pass
            if selected_cat != "All":
                dests = [d for d in dests if d.get("category") == selected_cat]
            if dests:
                for d in dests[:6]:
                    st.markdown(f"""
                    <div class='card' style='padding:10px 16px;display:flex;justify-content:space-between;align-items:center'>
                        <span><b>{d['name']}</b> — {d['city']}, {d['country']}</span>
                        <span>⭐ {d['avg_rating']} · {d['category'].title()}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No destinations found")
