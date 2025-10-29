# 🌙 AstroTrade Personal Assistant

Personalized Astro-Trading Calendar & Analytics Dashboard based on Vedic Astrology.

## ✨ Features

- 🔮 **Auto-Calculate Lagna (Ascendant)** - Accurate sidereal calculations using Swiss Ephemeris
- 🌍 **Geocoding** - Search cities and auto-fetch coordinates
- 📅 **Trading Calendar** - Daily recommendations based on Nakshatra & Navatara
- ⚠️ **Market Hour Alerts** - Highlights nakshatra changes during trading hours (9:15 AM - 3:30 PM IST)
- 🌔 **Panchanga Details** - Tithi, Yoga, Moon Phase, Moon Sign
- 📊 **Analytics Dashboard** - Visualize trading patterns
- 📥 **Export** - Download Excel/CSV reports
- 📱 **Mobile Responsive** - Works perfectly on iPhone/Android

## 🎯 How It Works

1. Enter birth details (Date, Time, Place)
2. Auto-calculate Lagna or select manually
3. Set date range (defaults to next 3 months)
4. Generate personalized trading calendar
5. View recommendations: TRADE (favorable), LIGHT (caution), AVOID (high risk)

## 🌟 Astrological Logic

- **Navatara System**: Classifies days based on birth nakshatra
  - Janma, Sampat, Vipat, Kshema, Pratyak, Sadhaka, Naidhana, Mitra, Parama Mitra
- **Market Hour Changes**: Alerts when nakshatra changes between 9:15 AM - 3:30 PM IST
- **Sidereal Zodiac**: Uses Lahiri Ayanamsa for accurate Indian astrology calculations

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Python)
- **Calculations**: Swiss Ephemeris (pyswisseph)
- **Geocoding**: Geopy
- **Visualization**: Plotly
- **Reports**: OpenPyXL, Pandas

## 📦 Local Setup
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 👨‍💻 Developer

Created with ❤️ for astro-traders

---

**Disclaimer**: This tool is for educational and research purposes. Astrological insights should not be the sole basis for trading decisions. Always do your own research and consult financial advisors.
