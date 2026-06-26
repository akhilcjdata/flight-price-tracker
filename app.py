import streamlit as st
import requests
from datetime import datetime, timedelta

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Flight Price Tracker",
    page_icon="✈️",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main { background: #0a0e1a; }
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0f1729 50%, #0a1628 100%);
    min-height: 100vh;
}
.hero-banner {
    background: linear-gradient(135deg, #1a2744 0%, #0d1f3c 100%);
    border: 1px solid #2a3f6f;
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-size: 2rem;
    font-weight: 700;
    color: #f0f6ff;
    letter-spacing: -0.5px;
    margin: 0 0 6px 0;
}
.hero-sub { font-size: 0.95rem; color: #7a9cc4; margin: 0; }
.route-card {
    background: linear-gradient(135deg, #111c35 0%, #0e1a30 100%);
    border: 1px solid #1e3054;
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 16px;
}
.route-title { font-size: 1.2rem; font-weight: 600; color: #e8f0fc; margin: 2px 0 0 0; }
.route-label { font-size: 0.7rem; font-weight: 600; letter-spacing: 1.5px; color: #3b82f6; text-transform: uppercase; }
.price-badge {
    background: linear-gradient(135deg, #1e3a5f, #162d4a);
    border: 1px solid #2a4f7a;
    border-radius: 10px;
    padding: 12px 18px;
    display: inline-block;
    margin: 4px;
    width: 100%;
    text-align: center;
}
.price-amount { font-size: 1.5rem; font-weight: 700; color: #60a5fa; }
.price-airline { font-size: 0.78rem; color: #94a3b8; margin-top: 2px; }
.price-duration { font-size: 0.72rem; color: #64748b; }
.alert-box {
    background: linear-gradient(135deg, #0f2a1a, #0a1f14);
    border: 1px solid #16a34a;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 16px 0;
}
.alert-box-warn {
    background: linear-gradient(135deg, #2a1a0f, #1f140a);
    border: 1px solid #d97706;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 16px 0;
}
.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #22c55e;
    margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
.stat-card {
    background: #111c35;
    border: 1px solid #1e3054;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.stat-number { font-size: 1.8rem; font-weight: 700; color: #60a5fa; }
.stat-label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
.last-updated { font-size: 0.78rem; color: #475569; text-align: right; margin-top: 8px; }
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white; border: none;
    border-radius: 10px; font-weight: 600;
    padding: 10px 24px; transition: all 0.2s;
}
div[data-testid="stButton"] button:hover {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    transform: translateY(-1px);
}
.stTextInput input, .stNumberInput input {
    background: #111c35 !important;
    border: 1px solid #1e3054 !important;
    color: #e8f0fc !important;
    border-radius: 8px !important;
}
label { color: #94a3b8 !important; }
.sidebar-section {
    background: #111c35;
    border: 1px solid #1e3054;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
}
hr { border-color: #1e3054 !important; }
.no-results { text-align: center; padding: 40px; color: #475569; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = {}
if "last_checked" not in st.session_state:
    st.session_state.last_checked = None
if "alert_log" not in st.session_state:
    st.session_state.alert_log = []


# ── Routes config ─────────────────────────────────────────────────────────────
ROUTES = {
    "Muscat → Kochi": {
        "departure_id": "MCT",
        "arrival_id": "COK",
        "key": "MCT-COK"
    },
    "Muscat → Trivandrum": {
        "departure_id": "MCT",
        "arrival_id": "TRV",
        "key": "MCT-TRV"
    },
}


# ── Serpapi flight fetch ───────────────────────────────────────────────────────
def fetch_flights_serpapi(api_key, departure_id, arrival_id, date_str, adults=1):
    """Fetch flights from Google Flights via Serpapi."""
    params = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": date_str,
        "currency": "INR",
        "hl": "en",
        "adults": adults,
        "api_key": api_key,
        "type": "2",   # 2 = one-way
    }
    try:
        r = requests.get("https://serpapi.com/search", params=params, timeout=20)
        data = r.json()
        if "error" in data:
            st.error(f"Serpapi error: {data['error']}")
            return []
        return data.get("best_flights", []) + data.get("other_flights", [])
    except Exception as e:
        st.error(f"Request failed: {e}")
        return []


def parse_serpapi_flights(flights):
    """Parse Serpapi Google Flights response into clean list."""
    results = []
    for flight in flights:
        try:
            price = float(flight.get("price", 0))
            if price == 0:
                continue
            legs = flight.get("flights", [])
            if not legs:
                continue
            first_leg = legs[0]
            last_leg = legs[-1]
            airline = first_leg.get("airline", "Unknown")
            flight_number = first_leg.get("flight_number", "")
            dep_time = first_leg.get("departure_airport", {}).get("time", "")[:5]
            arr_time = last_leg.get("arrival_airport", {}).get("time", "")[:5]
            duration_min = flight.get("total_duration", 0)
            hours = duration_min // 60
            mins = duration_min % 60
            duration = f"{hours}h {mins}m" if hours else f"{mins}m"
            stops = len(legs) - 1
            results.append({
                "price": price,
                "airline": airline,
                "flight_number": flight_number,
                "dep_time": dep_time,
                "arr_time": arr_time,
                "duration": duration,
                "stops": stops,
            })
        except Exception:
            continue
    return sorted(results, key=lambda x: x["price"])


# ── Telegram ──────────────────────────────────────────────────────────────────
def send_telegram(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception:
        return False


def format_telegram_alert(route_name, offers, threshold, travel_date):
    cheapest = offers[0]
    stops_label = "Non-stop" if cheapest["stops"] == 0 else f"{cheapest['stops']} stop(s)"
    lines = [
        "✈️ <b>Flight Price Alert!</b>",
        "",
        f"🛫 <b>{route_name}</b>",
        f"📅 Travel Date: {travel_date}",
        "",
        f"💰 Cheapest Fare: <b>₹{cheapest['price']:,.0f}</b>",
        f"🏷 Airline: {cheapest['airline']} ({cheapest['flight_number']})",
        f"🕐 Departure: {cheapest['dep_time']}  →  Arrival: {cheapest['arr_time']}",
        f"⏱ Duration: {cheapest['duration']}  |  {stops_label}",
        "",
        f"🔔 Price is below your threshold of ₹{threshold:,}",
        f"🕵️ Checked at: {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
        "",
        "Book now before prices go up! 🚀",
    ]
    return "\n".join(lines)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("**🔑 Serpapi Key**")
    serpapi_key = st.text_input("API Key", type="password", placeholder="Your Serpapi private API key")
    st.markdown("Get your key at [serpapi.com/manage-api-key](https://serpapi.com/manage-api-key)")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("**📱 Telegram Alerts**")
    tg_token = st.text_input("Bot Token", type="password", placeholder="123456:ABC-DEF...")
    tg_chat_id = st.text_input("Chat ID", placeholder="Your Telegram chat ID")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("**🗓️ Search Settings**")
    search_date = st.date_input(
        "Travel Date",
        value=datetime.now() + timedelta(days=30),
        min_value=datetime.now() + timedelta(days=1),
    )
    adults = st.selectbox("Passengers", [1, 2, 3, 4], index=0)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("**🔔 Price Thresholds (₹)**")
    threshold_kochi = st.number_input("Muscat → Kochi alert below", value=20000, step=500, min_value=1000)
    threshold_trv = st.number_input("Muscat → Trivandrum alert below", value=22000, step=500, min_value=1000)
    st.markdown("</div>", unsafe_allow_html=True)

    check_now = st.button("🔍 Check Prices Now", use_container_width=True)

    st.markdown("---")
    st.markdown("**📋 Setup Guide**")
    st.markdown("""
1. Get Serpapi key at [serpapi.com](https://serpapi.com)
2. Create Telegram bot via [@BotFather](https://t.me/BotFather)
3. Get your Chat ID from [@userinfobot](https://t.me/userinfobot)
4. Enter keys above & click Check Prices!
    """)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">✈️ Flight Price Tracker</div>
    <p class="hero-sub">Daily monitoring · Muscat → Kochi &amp; Muscat → Trivandrum · Powered by Google Flights via Serpapi</p>
</div>
""", unsafe_allow_html=True)

thresholds = {"MCT-COK": threshold_kochi, "MCT-TRV": threshold_trv}

# ── Fetch on button click ─────────────────────────────────────────────────────
if check_now:
    if not serpapi_key:
        st.error("Please enter your Serpapi API Key in the sidebar.")
    else:
        date_str = search_date.strftime("%Y-%m-%d")
        with st.spinner("Fetching live prices from Google Flights..."):
            for route_name, route in ROUTES.items():
                raw = fetch_flights_serpapi(
                    serpapi_key,
                    route["departure_id"],
                    route["arrival_id"],
                    date_str,
                    adults,
                )
                parsed = parse_serpapi_flights(raw)
                st.session_state.results[route["key"]] = {
                    "route_name": route_name,
                    "offers": parsed,
                    "date": date_str,
                }

                # Telegram alert check
                if parsed:
                    cheapest_price = parsed[0]["price"]
                    threshold = thresholds[route["key"]]
                    if cheapest_price <= threshold and tg_token and tg_chat_id:
                        msg = format_telegram_alert(route_name, parsed, threshold, date_str)
                        sent = send_telegram(tg_token, tg_chat_id, msg)
                        st.session_state.alert_log.append({
                            "time": datetime.now().strftime("%d %b %H:%M"),
                            "route": route_name,
                            "price": cheapest_price,
                            "sent": sent,
                        })

        st.session_state.last_checked = datetime.now().strftime("%d %b %Y, %I:%M %p")
        st.success("✅ Prices updated successfully!")
        st.rerun()


# ── Stats row ─────────────────────────────────────────────────────────────────
total_results = sum(len(v.get("offers", [])) for v in st.session_state.results.values())
all_prices = [o["price"] for v in st.session_state.results.values() for o in v.get("offers", [])]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{total_results}</div><div class="stat-label">Flights Found</div></div>', unsafe_allow_html=True)
with col2:
    cheapest_overall = f"₹{min(all_prices):,.0f}" if all_prices else "—"
    st.markdown(f'<div class="stat-card"><div class="stat-number">{cheapest_overall}</div><div class="stat-label">Cheapest Found</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{len(st.session_state.alert_log)}</div><div class="stat-label">Alerts Sent</div></div>', unsafe_allow_html=True)
with col4:
    status = '<span class="status-dot"></span>Live' if st.session_state.last_checked else "Not checked"
    st.markdown(f'<div class="stat-card"><div class="stat-number" style="font-size:1rem;padding-top:6px">{status}</div><div class="stat-label">Status</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Flight Results ────────────────────────────────────────────────────────────
if not st.session_state.results:
    st.markdown("""
    <div class="no-results">
        <div style="font-size:3rem">✈️</div>
        <div style="color:#7a9cc4; font-size:1rem; margin-top:12px">Enter your Serpapi key and click <b>Check Prices Now</b></div>
        <div style="color:#475569; margin-top:6px">Live prices from Google Flights will appear here</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for route_key, data in st.session_state.results.items():
        offers = data.get("offers", [])
        route_name = data.get("route_name", route_key)
        threshold = thresholds[route_key]

        st.markdown(f"""
        <div class="route-card">
            <div class="route-label">Route</div>
            <div class="route-title">🛫 {route_name} &nbsp;·&nbsp; <span style="color:#64748b;font-size:0.9rem">{data.get('date','')}</span></div>
        </div>
        """, unsafe_allow_html=True)

        if not offers:
            st.markdown('<div class="no-results">No flights found for this route/date. Try a different date.</div>', unsafe_allow_html=True)
            continue

        cheapest_price = offers[0]["price"]
        if cheapest_price <= threshold:
            st.markdown(f"""
            <div class="alert-box">
                🟢 <b>Price Alert!</b> Cheapest is ₹{cheapest_price:,.0f} — below your threshold of ₹{threshold:,}. Telegram alert sent! 📱
            </div>
            """, unsafe_allow_html=True)
        else:
            diff = cheapest_price - threshold
            st.markdown(f"""
            <div class="alert-box-warn">
                🟡 Cheapest is ₹{cheapest_price:,.0f} — ₹{diff:,.0f} above your alert threshold of ₹{threshold:,}
            </div>
            """, unsafe_allow_html=True)

        cols = st.columns(min(len(offers), 5))
        for i, (col, offer) in enumerate(zip(cols, offers)):
            with col:
                stops_label = "Non-stop ✅" if offer["stops"] == 0 else f"{offer['stops']} stop"
                badge_color = "#22c55e" if i == 0 else "#60a5fa"
                crown = "🏆 " if i == 0 else ""
                st.markdown(f"""
                <div class="price-badge">
                    {crown}<span class="price-amount" style="color:{badge_color}">₹{offer['price']:,.0f}</span>
                    <div class="price-airline">{offer['airline']} {offer['flight_number']}</div>
                    <div class="price-duration">{offer['dep_time']} → {offer['arr_time']} · {offer['duration']}</div>
                    <div class="price-duration">{stops_label}</div>
                </div>
                """, unsafe_allow_html=True)

        if st.session_state.last_checked:
            st.markdown(f'<div class="last-updated">Last checked: {st.session_state.last_checked}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)


# ── Alert Log ─────────────────────────────────────────────────────────────────
if st.session_state.alert_log:
    st.markdown("---")
    st.markdown("### 📬 Telegram Alert History")
    for log in reversed(st.session_state.alert_log[-10:]):
        icon = "✅" if log["sent"] else "❌"
        st.markdown(f"`{log['time']}` &nbsp; {icon} &nbsp; **{log['route']}** &nbsp;—&nbsp; ₹{log['price']:,.0f}", unsafe_allow_html=True)
