# 🚀 Quick Start Guide

Get up and running with AstroTrade Personal Assistant in 5 minutes!

## 📦 Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection (for initial setup)

## ⚡ Installation

### Method 1: Automated Setup (Recommended)

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh

# Run the application
./run.sh
```

### Method 2: Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p sweph outputs

# Download Swiss Ephemeris files
cd sweph
wget https://www.astro.com/ftp/swisseph/ephe/seas_18.se1
wget https://www.astro.com/ftp/swisseph/ephe/semo_18.se1
wget https://www.astro.com/ftp/swisseph/ephe/sepl_18.se1
cd ..

# Run the app
streamlit run app.py
```

### Method 3: Docker

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access at http://localhost:8501
```

## 🎯 First Steps

### 1. Configure Your Profile

Edit `profiles.json`:

```json
{
  "YourName": {
    "dob": "1990-01-15",
    "tob": "14:30",
    "pob": "Mumbai, India",
    "lat": 19.076,
    "lon": 72.877,
    "lagna": "Leo"
  }
}
```

**How to find coordinates:**
- Google Maps: Right-click → "What's here?"
- Or use: https://www.latlong.net/

### 2. Run Example

Test the installation:

```bash
python example_run.py
```

This will:
- Generate a 4-month calendar for Vijay (sample profile)
- Create Excel and CSV reports in `outputs/`
- Display statistics and sample days

### 3. Launch Web App

```bash
streamlit run app.py
```

Browser will open automatically at `http://localhost:8501`

## 🎨 Using the App

### Basic Workflow

1. **Select Profile** (Sidebar)
   - Choose from dropdown
   
2. **Set Date Range** (Sidebar)
   - Start Date: When to begin analysis
   - End Date: When to end analysis
   
3. **Configure Options** (Sidebar)
   - ☑️ Include Hora View
   - ☑️ Include Panchanga Details
   - ☐ Backtest with Trade Log
   - ☐ Send Telegram Alert
   
4. **Generate** (Sidebar)
   - Click "🚀 Generate Calendar"
   - Wait 10-30 seconds
   
5. **Explore Tabs**
   - 🗓️ Daily Calendar
   - 🌔 Hora & Panchanga
   - 📊 Analytics
   - 🔔 Alerts & Reports

## 📊 Understanding Results

### Color Codes

- 🟢 **TRADE**: Normal trading day (favorable conditions)
- 🟡 **LIGHT**: Cautious trading (reduced positions recommended)
- 🔴 **AVOID**: No trading (unfavorable conditions)
- 🔒 **CLOSED**: Market holiday or weekend

### Key Indicators

- **Nakshatra**: Current moon constellation
- **Navatara**: 9-star classification from your birth nakshatra
- **Change Time**: When nakshatra transitions
- **🔺 Marker**: Nakshatra changes during market hours (9:15 AM - 3:30 PM)

## 📥 Exporting Data

### Excel Report
1. Go to "🔔 Alerts & Reports" tab
2. Click "📊 Generate Excel Report"
3. Click "⬇️ Download Excel"
4. Opens in Excel/LibreOffice with color coding

### CSV Export
1. Go to "🔔 Alerts & Reports" tab
2. Click "📄 Generate CSV Report"
3. Click "⬇️ Download CSV"
4. Use in Python, R, or any data tool

## 🐛 Common Issues

### "No module named 'swisseph'"

**Solution:**
```bash
pip install pyswisseph
```

### "Swiss Ephemeris files not found"

**Solution:**
```bash
# Manually download to sweph/ directory
cd sweph
wget https://www.astro.com/ftp/swisseph/ephe/seas_18.se1
wget https://www.astro.com/ftp/swisseph/ephe/semo_18.se1
wget https://www.astro.com/ftp/swisseph/ephe/sepl_18.se1
```

### App is slow

**Normal behavior** for long date ranges (1+ years)
- Each day requires multiple astronomical calculations
- Reduce date range for faster results
- First run is slower; subsequent runs use caching

### Wrong birth time format

**Format:** 24-hour time as HH:MM
- ✅ Correct: "14:30"
- ❌ Wrong: "2:30 PM"

## 📱 Telegram Alerts (Optional)

### Setup

1. Create bot: Talk to [@BotFather](https://t.me/botfather)
2. Get token: `/newbot` → follow prompts
3. Get chat ID: Talk to [@userinfobot](https://t.me/userinfobot)
4. Enter in app settings

### Test

1. Enable "Send Telegram Alert" in sidebar
2. Enter Bot Token and Chat ID
3. Go to "🔔 Alerts & Reports" tab
4. Select a date
5. Click "Send Test Alert"

## 🎓 Learning Resources

### Understanding Navatara

| Position | Name | Trading Impact |
|----------|------|----------------|
| 1st | Janma | Cautious (your own nakshatra) |
| 2nd | Sampat | Favorable (wealth) |
| 3rd | Vipat | Avoid (danger) |
| 4th | Kshema | Cautious (well-being) |
| 5th | Pratyari | Avoid (obstacle) |
| 6th | Sadhana | Good (achievement) |
| 7th | Naidhana | Avoid (destruction) |
| 8th | Mitra | Favorable (friend) |
| 9th | Parama Mitra | Best (best friend) |

### Ashtama (8th House)

The 8th house from Moon or Lagna (ascendant) is considered challenging for new ventures:
- **From Moon**: Avoid trading
- **From Lagna**: Cautious/light trading

## 💡 Pro Tips

1. **Start with 3 months** - Test the system before committing to longer periods
2. **Review weekends** - Many insights come from analyzing patterns over time
3. **Combine with TA** - Use astro calendar alongside technical analysis
4. **Track results** - Upload trade logs to see correlations
5. **Check holidays** - App automatically marks NSE holidays
6. **Backup profiles** - Save profiles.json before editing

## 🆘 Getting Help

1. Check README.md for detailed documentation
2. Run `python example_run.py` to verify installation
3. Check `outputs/` folder for generated reports
4. Review error messages for specific issues

## ⏭️ Next Steps

Once you're comfortable:
- Add multiple profiles for comparison
- Upload trade logs for backtesting
- Experiment with date ranges
- Configure Telegram alerts
- Customize trading rules in `core/trading_logic.py`

## 🎉 You're Ready!

That's it! You now have a powerful astro-trading calendar at your fingertips.

Remember: Use this as ONE tool in your trading toolkit, not your only decision-making criteria.

Happy Trading! 🌙📈

---

For advanced features and customization, see the full [README.md](README.md)
