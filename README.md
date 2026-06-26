# ✈️ Flight Price Tracker — Setup Guide

Monitor **Muscat → Kochi** and **Muscat → Trivandrum** flight prices daily with Telegram alerts.

---

## 🚀 Quick Setup (5 Steps)

### Step 1 — Get Amadeus API Credentials (Free)
1. Go to [https://developers.amadeus.com](https://developers.amadeus.com)
2. Click **Sign Up** (free)
3. Go to **My Apps** → **Create New App**
4. Copy your **API Key** and **API Secret**
5. ⚠️ Start with the **Test environment** (free, no charges)

### Step 2 — Create a Telegram Bot (Free)
1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Give it a name like `Flight Price Bot`
4. Copy the **Bot Token** (looks like `123456789:ABCdef...`)

### Step 3 — Get Your Telegram Chat ID
1. Open Telegram and search for **@userinfobot**
2. Send `/start`
3. It will reply with your **Chat ID** (a number like `987654321`)
4. Also send a message to your new bot first to activate it

### Step 4 — Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Step 5 — Deploy to Streamlit Cloud (Free)
1. Push this folder to a **GitHub repository**
2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Click **New App** → connect your GitHub repo
4. Set `app.py` as the main file
5. Deploy! ✅

---

## 🔐 Securing Your API Keys on Streamlit Cloud

Never put API keys in your code. Use **Streamlit Secrets**:

1. In Streamlit Cloud, go to your app → **Settings** → **Secrets**
2. Add:
```toml
AMADEUS_KEY = "your_amadeus_key"
AMADEUS_SECRET = "your_amadeus_secret"
TELEGRAM_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"
```

---

## 📋 Airport Codes Reference

| City | Code |
|------|------|
| Muscat, Oman | MCT |
| Kochi, India | COK |
| Trivandrum, India | TRV |

---

## 💰 Cost Estimate

| Service | Cost |
|---------|------|
| Amadeus API (test) | Free |
| Amadeus API (production) | Free up to certain limits |
| Telegram Bot | Free forever |
| Streamlit Cloud | Free |
| **Total** | **₹0** |

---

## ❓ Common Issues

**"No flights found"** → Try a date 1–3 months ahead. Amadeus test environment has limited data.

**Telegram alert not received** → Make sure you sent at least one message to your bot first.

**Amadeus auth error** → Double-check your API key and secret. They expire if unused.
