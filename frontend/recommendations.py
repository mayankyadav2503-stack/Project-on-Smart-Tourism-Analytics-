import streamlit as st
import requests

API = "http://127.0.0.1:5000/api"
DEFAULT_USER = 1

def show_recommendations():
    st.markdown("<h1>🎯 Discover Destinations</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888'>Personalized recommendations based on your preferences, or browse by category.</p>", unsafe_allow_html=True)

    if "selected_dest_detail" not in st.session_state:
        st.session_state.selected_dest_detail = None

    if st.session_state.selected_dest_detail:
        _show_dest_detail(st.session_state.selected_dest_detail)
        if st.button("← Back to recommendations"):
            st.session_state.selected_dest_detail = None
            st.rerun()
        return

    t1, t2, t3 = st.tabs(["✨ Personalized", "🔥 Popular", "🏷 By Category"])

    with t1:
        dests = []
        try:
            r = requests.get(f"{API}/recommendations/personalized/{DEFAULT_USER}?limit=12", timeout=5)
            dests = r.json()
        except:
            pass
        if dests:
            _show_dest_grid(dests, "pers")
        else:
            try:
                dests = requests.get(f"{API}/recommendations/popular?limit=12", timeout=5).json()
            except:
                pass
            if dests:
                _show_dest_grid(dests, "pers")

    with t2:
        dests = []
        try:
            dests = requests.get(f"{API}/recommendations/popular?limit=12", timeout=5).json()
        except:
            pass
        if dests:
            _show_dest_grid(dests, "pop")
        else:
            st.info("No popular destinations data yet")

    with t3:
        cats = ["landmark","museum","beach","nature","temple","shopping","park","island"]
        sel_cat = st.selectbox("Select category", cats)
        all_dests = []
        try:
            all_dests = requests.get(f"{API}/destinations", timeout=5).json()
        except:
            pass
        filtered = [d for d in all_dests if d.get("category") == sel_cat]
        if filtered:
            for d in filtered:
                st.markdown(f"""
                <div class='card' style='padding:12px 16px'>
                    <h4 style='margin:0'>{d['name']}</h4>
                    <p style='margin:2px 0;color:#888'>{d['city']}, {d['country']} · ⭐ {d['avg_rating']}/5 · 💬 {d['review_count']} reviews</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View Details", key=f"cat_detail_{d['id']}", width='stretch'):
                    st.session_state.selected_dest_detail = d["id"]
                    st.rerun()
        else:
            st.info(f"No destinations in '{sel_cat}' category")

def _show_dest_grid(dests, prefix="g"):
    cols = st.columns(3)
    for i, item in enumerate(dests):
        d = item["destination"] if "destination" in item else item
        score = item.get("score", 0)
        with cols[i % 3]:
            st.markdown(f"""
            <div class='card' style='border-top:3px solid #0f3460'>
                <h4 style='margin:0 0 4px 0'>{d['name']}</h4>
                <p style='margin:2px 0;color:#888'>📍 {d['city']}, {d['country']}</p>
                <p style='margin:2px 0'>⭐ {d['avg_rating']}/5 · 💬 {d['review_count']}</p>
                <p style='margin:2px 0'>🏷 {d['category'].title()}</p>
                <p style='margin:4px 0;color:#0f3460;font-weight:bold'>🎯 Score: {score:.1f}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Explore", key=f"{prefix}_grid_{d['id']}", width='stretch'):
                st.session_state.selected_dest_detail = d["id"]
                st.rerun()

def _show_dest_detail(dest_id):
    try:
        r = requests.get(f"{API}/destinations/{dest_id}", timeout=5)
        if r.status_code != 200:
            st.error("Destination not found"); return
        dest = r.json()
    except:
        st.error("Could not load destination details"); return

    st.markdown(f"<h1>📍 {dest['name']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#888'>{dest['city']}, {dest['country']} — {dest['category'].title()}</p>", unsafe_allow_html=True)

    k1, k2, k3 = st.columns(3)
    with k1: st.markdown(f"<div class='metric-card'><span style='font-size:1.5rem;color:#fff'>⭐ {dest['avg_rating']}/5</span><br><span style='color:#888'>Rating</span></div>", unsafe_allow_html=True)
    with k2: st.markdown(f"<div class='metric-card'><span style='font-size:1.5rem;color:#fff'>💬 {dest['review_count']}</span><br><span style='color:#888'>Reviews</span></div>", unsafe_allow_html=True)
    with k3: st.markdown(f"<div class='metric-card'><span style='font-size:1.5rem;color:#fff'>🔥 {dest['popularity_score']:.0f}</span><br><span style='color:#888'>Popularity</span></div>", unsafe_allow_html=True)

    try:
        w = requests.get(f"{API}/weather", params={"city": dest['city']}, timeout=5).json()
        if w.get("temperature"):
            st.info(f"🌤 Current Weather in {dest['city']}: {w['temperature']}°C, {w['description'].title()}")
    except:
        pass

    t1, t2, t3, t4 = st.tabs(["🏨 Hotels", "🍽 Restaurants", "🎯 Activities", "💬 Reviews"])
    with t1:
        for h in dest.get("hotels", []):
            st.markdown(f"<div class='card' style='padding:10px 14px;border-left:3px solid #2ecc71'><b>{h['name']}</b> — 💰 ${h['price_per_night']}/night ⭐ {h['rating']}/5<br><small style='color:#888'>🛋 {h.get('amenities','N/A')[:80]}</small></div>", unsafe_allow_html=True)
        if not dest.get("hotels"): st.info("No hotels listed")
    with t2:
        for r in dest.get("restaurants", []):
            st.markdown(f"<div class='card' style='padding:10px 14px;border-left:3px solid #e74c3c'><b>{r['name']}</b> — 🍳 {r['cuisine']} ({r['price_range']}) ⭐ {r['rating']}/5</div>", unsafe_allow_html=True)
        if not dest.get("restaurants"): st.info("No restaurants listed")
    with t3:
        for a in dest.get("activities", []):
            cost = f"${a['cost']:.0f}" if a['cost'] > 0 else "Free"
            st.markdown(f"<div class='card' style='padding:10px 14px;border-left:3px solid #3498db'><b>{a['name']}</b> — {cost} · ⏱ {a['duration_hours']}h ⭐ {a['rating']}/5<br><small style='color:#888'>📂 {a.get('category','General').title()}</small></div>", unsafe_allow_html=True)
        if not dest.get("activities"): st.info("No activities listed")
        if st.button("📋 Generate Itinerary for this Destination", width='stretch'):
            st.session_state.itinerary_dest_id = dest_id
            st.session_state.itinerary_dest_name = dest['name']
            st.session_state.page = "itinerary"
            st.rerun()
    with t4:
        try:
            rv = requests.get(f"{API}/reviews/{dest_id}", timeout=5).json()
            if rv:
                for rev in rv[:10]:
                    stars = "⭐" * rev['rating'] + "☆" * (5 - rev['rating'])
                    st.markdown(f"<div class='card' style='padding:8px 12px'><b>{rev.get('username','Anonymous')}</b> {stars}<br><i>\"{rev['text']}\"</i></div>", unsafe_allow_html=True)
            else:
                st.info("No reviews yet")
        except:
            st.info("Could not load reviews")
