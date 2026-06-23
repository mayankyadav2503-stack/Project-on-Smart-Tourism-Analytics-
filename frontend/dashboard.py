import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API = "http://127.0.0.1:5000/api"
DEFAULT_USER = 1

def _style(fig, title="", x_title="", y_title=""):
    fig.update_layout(
        paper_bgcolor="#111", plot_bgcolor="#111", font_color="#ccc",
        title_font_color="#fff", title=title,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    fig.update_xaxes(gridcolor="#333", title=x_title)
    fig.update_yaxes(gridcolor="#333", title=y_title)

def show_dashboard():
    trends = {}
    budget = {}
    dests = []
    try:
        trends = requests.get(f"{API}/trends", timeout=5).json()
        budget = requests.get(f"{API}/budget/{DEFAULT_USER}", timeout=5).json()
        dests = requests.get(f"{API}/destinations", timeout=5).json()
    except:
        pass

    st.markdown("<h1>📊 Travel Analytics Hub</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#999'>Real-time insights across destinations, spending, and trends.</p>", unsafe_allow_html=True)

    hs = trends.get("hotel_stats", {})
    top = trends.get("top_destinations", [])
    bsum = budget.get("summary", {})
    cat_data = trends.get("category_distribution", [])

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"<div class='metric-card'><span style='font-size:2rem'>🗺</span><br><span style='font-size:1.5rem;color:#fff'>{len(cat_data) or 15}</span><br><span style='color:#888'>Destinations</span></div>", unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='metric-card'><span style='font-size:2rem'>🏨</span><br><span style='font-size:1.5rem;color:#fff'>${hs.get('avg_hotel_price',0):.0f}</span><br><span style='color:#888'>Avg Hotel/Night</span></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='metric-card'><span style='font-size:2rem'>💰</span><br><span style='font-size:1.5rem;color:#fff'>${bsum.get('total_spent',0):,.0f}</span><br><span style='color:#888'>Total Spent</span></div>", unsafe_allow_html=True)
    with k4:
        st.markdown(f"<div class='metric-card'><span style='font-size:2rem'>✈️</span><br><span style='font-size:1.5rem;color:#fff'>{bsum.get('total_trips',0)}</span><br><span style='color:#888'>Trips</span></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- SPENDING ---
    bk = budget.get("bookings", [])
    if bk:
        st.markdown("<h2>💰 Spending Breakdown</h2>", unsafe_allow_html=True)
        dfb = pd.DataFrame(bk)
        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(dfb, x="destination", y="total_spent", color="country",
                         color_discrete_sequence=px.colors.qualitative.Vivid)
            _style(fig, title="Spending by Destination")
            st.plotly_chart(fig, width='stretch')
        with c2:
            fig = px.pie(dfb, values="total_spent", names="destination",
                         color_discrete_sequence=px.colors.qualitative.Vivid)
            _style(fig, title="Spending Distribution")
            st.plotly_chart(fig, width='stretch')

    # --- RATING + POPULARITY SCATTER ---
    if dests:
        st.markdown("<h2>⭐ Destination Quality Snapshot</h2>", unsafe_allow_html=True)
        df_d = pd.DataFrame(dests)
        fig = px.scatter(df_d, x="popularity_score", y="avg_rating",
                         size="review_count", color="category",
                         hover_data=["name", "city"],
                         color_discrete_sequence=px.colors.qualitative.Vivid)
        _style(fig, title="Popularity vs Rating (bubble size = review count)",
               x_title="Popularity Score", y_title="Avg Rating")
        fig.update_layout(yaxis_range=[3, 5.5])
        st.plotly_chart(fig, width='stretch')

    # --- HOTEL PRICE SPECTRUM ---
    if hs:
        st.markdown("<h2>🏨 Hotel Price Overview</h2>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-card'><span style='font-size:1.3rem;color:#2ecc71'>${hs.get('min_price',0):.0f}</span><br><span style='color:#888'>Cheapest/Night</span></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><span style='font-size:1.3rem;color:#fff'>${hs.get('avg_hotel_price',0):.0f}</span><br><span style='color:#888'>Average/Night</span></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><span style='font-size:1.3rem;color:#e74c3c'>${hs.get('max_price',0):.0f}</span><br><span style='color:#888'>Most Expensive/Night</span></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- TABS: CATEGORIES / CROWD / TOP DESTINATIONS ---
    t1, t2, t3 = st.tabs(["📂 Categories", "📈 Crowd Trends", "🏆 Top Destinations"])

    with t1:
        if cat_data:
            df = pd.DataFrame(cat_data)
            c1, c2 = st.columns(2)
            with c1:
                fig = px.bar(df, y="category", x="count", color="avg_rating",
                             orientation="h", text_auto=True,
                             color_continuous_scale="Viridis")
                _style(fig, title="Destinations by Category")
                st.plotly_chart(fig, width='stretch')
            with c2:
                fig = px.pie(df, values="count", names="category",
                             color_discrete_sequence=px.colors.qualitative.Vivid)
                _style(fig, title="Category Mix")
                st.plotly_chart(fig, width='stretch')

            low = df[df["avg_rating"] < 4.0]
            high = df[df["avg_rating"] >= 4.0]
            st.markdown(f"""
            <div class='card'>
            <p>⭐ <b>Top-rated categories</b> (avg ≥ 4.0): {', '.join(high['category'].tolist())}</p>
            <p>📉 <b>Needs improvement</b> (avg &lt; 4.0): {', '.join(low['category'].tolist()) if len(low) > 0 else 'None'}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No category data yet")

    with t2:
        crowd_data = trends.get("monthly_crowd", [])
        if crowd_data:
            df2 = pd.DataFrame(crowd_data)
            month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            df2["month_name"] = df2["month"].astype(int).map(lambda m: month_names[m-1] if 1<=m<=12 else m)
            df2["avg_crowd"] = df2["avg_crowd"].round(1)

            fig = px.bar(df2, x="month_name", y="avg_crowd", text="avg_crowd",
                         color="avg_crowd", color_continuous_scale="RdYlGn_r",
                         range_color=[1, 7])
            fig.update_traces(texttemplate="%{text}", textposition="outside")
            _style(fig, title="Average Crowd Level by Month (data available May–Jul)",
                   x_title="", y_title="Crowd Level (1–5 scale)")
            fig.update_layout(yaxis_range=[0, 7])
            st.plotly_chart(fig, width='stretch')

            peak = df2.loc[df2["avg_crowd"].idxmax()]
            low = df2.loc[df2["avg_crowd"].idxmin()]
            st.markdown(f"""
            <div class='card'>
            <p>🔴 <b>Peak month:</b> {peak['month_name']} — Crowd level {peak['avg_crowd']}/7</p>
            <p>🟢 <b>Quietest month:</b> {low['month_name']} — Crowd level {low['avg_crowd']}/7</p>
            <p style='font-size:0.9em;color:#666'>Data covers May through July. Crowd levels above 5 indicate peak summer congestion.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No crowd data yet")

    with t3:
        if top:
            df3 = pd.DataFrame(top).head(10)
            c1, c2 = st.columns(2)
            with c1:
                fig = px.bar(df3, y="name", x="bookings", orientation="h",
                             text="bookings", color="bookings",
                             color_continuous_scale="Viridis")
                _style(fig, title="Top Destinations by Booking Volume",
                       x_title="Number of Bookings", y_title="")
                fig.update_traces(texttemplate="%{text}", textposition="outside")
                st.plotly_chart(fig, width='stretch')
            with c2:
                fig = px.bar(df3, y="name", x="revenue", orientation="h",
                             text="revenue", color="revenue",
                             color_continuous_scale="Plasma")
                fig.update_traces(texttemplate="$%{text}", textposition="outside")
                _style(fig, title="Top Destinations by Revenue",
                       x_title="Revenue ($)", y_title="")
                st.plotly_chart(fig, width='stretch')

            st.markdown("<div class='card'><p><b>🏆 Most booked:</b> " + df3.iloc[0]["name"] + " — " + str(int(df3.iloc[0]["bookings"])) + " bookings</p><p><b>💰 Highest revenue:</b> " + df3.loc[df3["revenue"].idxmax()]["name"] + " — $" + f"{df3['revenue'].max():,.0f}</p></div>", unsafe_allow_html=True)
        else:
            st.info("No booking data yet")

    st.markdown("<br><hr style='border-color:#222'>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;padding:10px;color:#555'>Smart Tourism Analytics Platform · Built with Flask + Streamlit + ML</div>", unsafe_allow_html=True)
