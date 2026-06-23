import streamlit as st
import requests

API = "http://127.0.0.1:5000/api"
DEFAULT_USER = 1

def show_chatbot():
    st.markdown("<h1>🤖 AI Travel Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888'>Your 24/7 travel companion — ask about destinations, weather, hotels, food, and more!</p>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role":"assistant","content":"👋 Hi! I'm your Smart Travel Assistant. Ask me anything about travel!\n\nTry: *\"Recommend places to visit\"*, *\"Weather in Paris\"*, *\"Hotels in Tokyo\"*, or *\"Budget tips\"*"}
        ]

    c1, c2 = st.columns([3,1])

    with c2:
        st.markdown("<h3>⚡ Quick Actions</h3>", unsafe_allow_html=True)
        qa = {"📍 Recommend":"Recommend places to visit","🌤 Weather Paris":"Weather in Paris",
              "🏨 Hotels Tokyo":"Hotels in Tokyo","🍽 Rome Food":"Restaurants in Rome",
              "💱 Exchange Rates":"Exchange rates","💰 Budget Tips":"Budget tips"}
        for label, query in qa.items():
            if st.button(label, key=f"qa_{label}", width='stretch'):
                st.session_state["quick_query"] = query; st.rerun()
        st.markdown("<div class='card'><h4 style='margin:0'>📋 What I Can Do</h4><p style='font-size:0.9em'>🌍 Destinations<br>🌤 Weather<br>🏨 Hotels<br>🍽 Restaurants<br>🎯 Activities<br>💱 Currency<br>💰 Budget<br>📊 Crowds<br>📋 Itineraries</p></div>", unsafe_allow_html=True)

    with c1:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style='background:#1a2a4a;padding:10px 16px;border-radius:18px 18px 5px 18px;margin:8px 0;max-width:85%;margin-left:auto;text-align:right;border:1px solid #0f3460'>
                    <b style='color:#0f3460'>You:</b> <span style='color:#e0e0e0'>{msg['content']}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background:#111;padding:10px 16px;border-radius:18px 18px 18px 5px;margin:8px 0;max-width:90%;border:1px solid #222'>
                    <b>🤖 Assistant:</b><br><span style='color:#ccc'>{msg['content']}</span>
                </div>
                """, unsafe_allow_html=True)

        user_input = st.chat_input("Ask me anything about travel...", key="chat_input")
        if user_input or "quick_query" in st.session_state:
            q = user_input or st.session_state.pop("quick_query", "")
            if q:
                st.session_state.chat_history.append({"role":"user","content":q})
                with st.spinner("Thinking..."):
                    try:
                        resp = requests.post(f"{API}/chat", json={"message":q,"user_id":DEFAULT_USER}, timeout=15)
                        reply = resp.json().get("reply","Sorry, I couldn't process that.") if resp.status_code == 200 else "Server error."
                        st.session_state.chat_history.append({"role":"assistant","content":reply})
                    except:
                        st.session_state.chat_history.append({"role":"assistant","content":"⚠️ Could not reach the server. Make sure the Flask backend is running."})
                st.rerun()
