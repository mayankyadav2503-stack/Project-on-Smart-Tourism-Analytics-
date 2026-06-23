import streamlit as st
import requests
from datetime import datetime, timedelta

API = "http://127.0.0.1:5000/api"
DEFAULT_USER = 1

def show_itinerary():
    st.markdown("# 📋 AI Itinerary Planner")
    st.markdown("Generate intelligent day-by-day trip plans with automatic budget allocation.")

    tab1, tab2 = st.tabs(["✈️ Plan New Trip", "📂 Saved Itineraries"])

    with tab1:
        st.markdown("### Plan Your Trip")
        dests = []
        try:
            r = requests.get(f"{API}/destinations", timeout=5)
            dests = r.json()
        except:
            pass

        if dests:
            dest_options = {f"{d['name']}, {d['city']}, {d['country']}": d["id"] for d in dests}
            default_idx = 0
            if "itinerary_dest_id" in st.session_state:
                for label, did in dest_options.items():
                    if did == st.session_state.itinerary_dest_id:
                        default_idx = list(dest_options.values()).index(did)
                        break

            selected = st.selectbox("Select Destination", list(dest_options.keys()), index=default_idx)
            dest_id = dest_options[selected]

            col1, col2, col3 = st.columns(3)
            with col1:
                start = st.date_input("Start Date", datetime.now() + timedelta(days=7))
            with col2:
                end = st.date_input("End Date", datetime.now() + timedelta(days=10))
            with col3:
                budget = st.number_input("Budget (USD)", min_value=100, max_value=50000, value=2000, step=100)

            days = (end - start).days + 1
            if days < 1:
                st.error("End date must be after start date")
                return

            st.success(f"Planning a **{days}-day** trip to **{selected.split(',')[0]}** with **${budget:,}** budget")

            if st.button("✨ Generate Smart Itinerary", width='stretch', type="primary"):
                with st.spinner("AI is building your personalized itinerary..."):
                    try:
                        resp = requests.post(f"{API}/itinerary/generate", json={
                            "user_id": DEFAULT_USER,
                            "destination_id": dest_id,
                            "start_date": start.strftime("%Y-%m-%d"),
                            "end_date": end.strftime("%Y-%m-%d"),
                            "budget": budget,
                        }, timeout=15)
                        if resp.status_code == 200:
                            plan = resp.json()
                            st.session_state["current_plan"] = plan
                            st.success("Itinerary generated successfully!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"Failed to generate: {resp.text}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")

        if "current_plan" in st.session_state:
            plan = st.session_state["current_plan"]
            st.markdown("---")
            st.markdown(f"## 🗺 Trip: {plan['destination']}")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📅 Duration", f"{plan['start_date']} to {plan['end_date']}")
            col2.metric("💰 Budget", f"${plan['total_budget']:,.0f}")
            col3.metric("💵 Est. Cost", f"${plan['estimated_cost']:,.0f}")
            col4.metric("💲 Remaining", f"${plan['total_budget'] - plan['estimated_cost']:,.0f}")

            if plan.get("hotel"):
                h = plan["hotel"]
                st.markdown(f"### 🏨 Accommodation: {h['name']}")
                st.markdown(f"💰 ${h['price_per_night']}/night · ⭐ {h['rating']}/5 · 🛋 {h.get('amenities','N/A')[:60]}")
            if plan.get("activities"):
                st.markdown("### 🎯 Selected Activities")
                for a in plan["activities"]:
                    cost = f"${a['cost']:.0f}" if a['cost'] > 0 else "Free"
                    st.markdown(f"- **{a['name']}** — {cost} ({a['duration_hours']}h)")
            if plan.get("restaurants"):
                st.markdown("### 🍽 Recommended Restaurants")
                for r in plan["restaurants"]:
                    st.markdown(f"- **{r['name']}** — {r['cuisine']} ({r['price_range']})")

            st.markdown("### 📅 Daily Plan")
            for day in plan.get("daily_plan", []):
                with st.expander(f"Day {day['day']} — {day['date']}", expanded=True):
                    st.markdown(f"| Time | Activity |\n|:---|---:|\n| 🌅 **Morning** | {day['morning']} |\n| ☀️ **Afternoon** | {day['afternoon']} |\n| 🌙 **Evening** | {day['evening']} |")

    with tab2:
        st.markdown("### 📂 Saved Itineraries")
        try:
            r = requests.get(f"{API}/itinerary/user/{DEFAULT_USER}", timeout=5)
            itineraries = r.json()
            if itineraries:
                for it in itineraries:
                    with st.expander(f"🗺 {it['name']} — {it.get('destination_name','')}"):
                        st.markdown(f"📍 {it.get('city','')}, {it.get('country','')}")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("📅 Dates", f"{it['start_date']} → {it['end_date']}")
                        col2.metric("💰 Budget", f"${it['budget']:,.0f}")
                        col3.metric("💵 Spent", f"${it['total_cost']:,.0f}")
                        st.caption(f"Created: {it['created_at']}")
            else:
                st.info("No saved itineraries yet. Create your first trip above!")
        except Exception as e:
            st.error(f"Error loading: {e}")
