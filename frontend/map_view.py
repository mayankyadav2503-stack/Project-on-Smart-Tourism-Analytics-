import streamlit as st
import folium
from streamlit_folium import st_folium
import requests

API = "http://127.0.0.1:5000/api"

def show_map():
    st.markdown("<h1>🗺 Interactive Destination Map</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888'>Explore destinations, hotels, restaurants, and activities on the map.</p>", unsafe_allow_html=True)

    destinations = []
    try:
        r = requests.get(f"{API}/map/destinations", timeout=5)
        destinations = r.json()
    except:
        st.error("Could not load map data")

    c1, c2 = st.columns([3,1])
    with c2:
        st.markdown("<h3>Filters</h3>", unsafe_allow_html=True)
        all_cats = list(set(d.get("category","general") for d in destinations))
        selected_cats = []
        for cat in sorted(all_cats):
            if st.checkbox(cat.title(), value=True):
                selected_cats.append(cat)
        st.markdown("<p style='color:#888'>📍 Destination · ⭐ Rating</p>", unsafe_allow_html=True)

    filtered = [d for d in destinations if d.get("category") in selected_cats]

    with c1:
        if filtered:
            m = folium.Map(location=[20,0], zoom_start=2,
                           tiles="CartoDB dark_matter")
            for d in filtered:
                if d.get("latitude") and d.get("longitude"):
                    lat, lng = d["latitude"], d["longitude"]
                    popup_text = f"""
                    <div style='font-family:sans-serif;min-width:180px'>
                        <b style='font-size:1.1em'>{d['name']}</b><br>
                        {d['city']}, {d['country']}<br>
                        ⭐ {d['avg_rating']}/5 · 📂 {d['category'].title()}<br>
                        🔥 Popularity: {d['popularity_score']:.0f}
                    </div>
                    """
                    color = "blue" if d["avg_rating"] >= 4.0 else "orange" if d["avg_rating"] >= 3.0 else "red"
                    folium.Marker(
                        [lat, lng],
                        popup=folium.Popup(popup_text, max_width=300),
                        tooltip=d["name"],
                        icon=folium.Icon(color=color),
                    ).add_to(m)
            st_data = st_folium(m, width=800, height=500, returned_objects=[])
        else:
            st.warning("No destinations match the selected filters")

    if "selected_dest" in st.session_state and st.session_state["selected_dest"]:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3>📍 Destination Details</h3>", unsafe_allow_html=True)
        try:
            r = requests.get(f"{API}/destinations/{st.session_state['selected_dest']}", timeout=5)
            if r.status_code == 200:
                dest = r.json()
                k1, k2, k3 = st.columns(3)
                with k1: st.markdown(f"<div class='metric-card'><span style='font-size:1.2rem;color:#fff'>⭐ {dest['avg_rating']}/5</span><br><span style='color:#888'>Rating</span></div>", unsafe_allow_html=True)
                with k2: st.markdown(f"<div class='metric-card'><span style='font-size:1.2rem;color:#fff'>💬 {dest['review_count']}</span><br><span style='color:#888'>Reviews</span></div>", unsafe_allow_html=True)
                with k3: st.markdown(f"<div class='metric-card'><span style='font-size:1.2rem;color:#fff'>🔥 {dest['popularity_score']:.0f}</span><br><span style='color:#888'>Pop.</span></div>", unsafe_allow_html=True)

                st.markdown(f"<b>{dest['name']}</b> — {dest['city']}, {dest['country']}", unsafe_allow_html=True)
                st.markdown(f"<i style='color:#888'>{dest.get('description','No description')}</i>", unsafe_allow_html=True)

                t1, t2, t3 = st.tabs(["🏨 Hotels", "🍽 Restaurants", "🎯 Activities"])
                with t1:
                    for h in dest.get("hotels",[]):
                        st.markdown(f"<div class='card' style='padding:8px 12px'><b>{h['name']}</b> — ${h['price_per_night']}/night ⭐ {h['rating']}</div>", unsafe_allow_html=True)
                with t2:
                    for r in dest.get("restaurants",[]):
                        st.markdown(f"<div class='card' style='padding:8px 12px'><b>{r['name']}</b> — {r['cuisine']} ({r['price_range']}) ⭐ {r['rating']}</div>", unsafe_allow_html=True)
                with t3:
                    for a in dest.get("activities",[]):
                        st.markdown(f"<div class='card' style='padding:8px 12px'><b>{a['name']}</b> — ${a['cost']} ({a['duration_hours']}h) ⭐ {a['rating']}</div>", unsafe_allow_html=True)
        except:
            pass
