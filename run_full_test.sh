#!/bin/bash

echo "================================================================================"
echo "           ASTROTRADE PERSONAL ASSISTANT - COMPLETE TEST REPORT"
echo "================================================================================"
echo "Test Date: $(date)"
echo "Directory: $(pwd)"
echo ""

# Detect python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found!"
    exit 1
fi

echo "Using Python: $PYTHON_CMD"
$PYTHON_CMD --version
echo ""

# Test 1: Check directory structure
echo "----------------------------------------------------------------------------"
echo "[TEST 1] Directory Structure"
echo "----------------------------------------------------------------------------"
echo "Files in current directory:"
ls -lh | grep -E '\.(py|json|sh)$'
echo ""
echo "Core directory contents:"
ls -lh core/ 2>/dev/null || echo "❌ core/ directory not found"
echo ""

# Test 2: Check packages
echo "----------------------------------------------------------------------------"
echo "[TEST 2] Python Packages"
echo "----------------------------------------------------------------------------"
$PYTHON_CMD << 'PYEOF'
packages = ['swisseph', 'pandas', 'streamlit', 'plotly', 'geopy', 'openpyxl']
for pkg in packages:
    try:
        __import__(pkg)
        print(f"  ✅ {pkg}")
    except ImportError:
        print(f"  ❌ {pkg} - NOT INSTALLED")
PYEOF
echo ""

# Test 3: Check app.py
echo "----------------------------------------------------------------------------"
echo "[TEST 3] App.py Verification"
echo "----------------------------------------------------------------------------"
echo "Total lines in app.py: $(wc -l < app.py)"
echo ""
echo "Checking key features:"
grep -q "Profile Input" app.py && echo "  ✅ Profile input radio button" || echo "  ❌ Profile input radio button - MISSING"
grep -q "Fetch Coordinates" app.py && echo "  ✅ Geocoding fetch button" || echo "  ❌ Geocoding fetch button - MISSING"
grep -q "market-alert" app.py && echo "  ✅ Market alert styling" || echo "  ❌ Market alert styling - MISSING"
grep -q "geopy.geocoders" app.py && echo "  ✅ Geopy import" || echo "  ❌ Geopy import - MISSING"
echo ""

# Test 4: Geocoding
echo "----------------------------------------------------------------------------"
echo "[TEST 4] Geocoding Test"
echo "----------------------------------------------------------------------------"
$PYTHON_CMD << 'PYEOF'
try:
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="astrotrade_test", timeout=10)
    
    for city in ["Mumbai", "Delhi", "Shimla"]:
        try:
            location = geolocator.geocode(f"{city}, India")
            if location:
                print(f"  ✅ {city}: {location.latitude:.4f}, {location.longitude:.4f}")
            else:
                print(f"  ❌ {city}: Not found")
        except Exception as e:
            print(f"  ⚠️ {city}: Timeout")
except Exception as e:
    print(f"  ❌ Geocoding failed: {e}")
PYEOF
echo ""

# Test 5: Core modules
echo "----------------------------------------------------------------------------"
echo "[TEST 5] Core Module Test"
echo "----------------------------------------------------------------------------"
$PYTHON_CMD << 'PYEOF'
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.trading_logic import TradingCalendar
    print("  ✅ TradingCalendar imported")
except Exception as e:
    print(f"  ❌ TradingCalendar: {e}")

try:
    from core.reports import ReportGenerator
    print("  ✅ ReportGenerator imported")
except Exception as e:
    print(f"  ❌ ReportGenerator: {e}")

try:
    import json
    with open('profiles.json') as f:
        profiles = json.load(f)
    print(f"  ✅ Profiles: {len(profiles)} loaded")
except Exception as e:
    print(f"  ❌ Profiles: {e}")
PYEOF
echo ""

# Test 6: Calendar generation
echo "----------------------------------------------------------------------------"
echo "[TEST 6] Calendar Generation"
echo "----------------------------------------------------------------------------"
$PYTHON_CMD << 'PYEOF'
import sys, os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.trading_logic import TradingCalendar
    import json
    
    with open('profiles.json') as f:
        profiles = json.load(f)
    
    calendar = TradingCalendar(profiles['Vijay'])
    df = calendar.generate_calendar(datetime(2025, 9, 1), datetime(2025, 9, 7))
    
    print(f"  ✅ Calendar: {len(df)} days generated")
    print(f"     Trade: {len(df[df['recommendation'] == 'TRADE'])}")
    print(f"     Avoid: {len(df[df['recommendation'] == 'AVOID'])}")
    
    market_changes = df[df.get('change_during_market', False) == True]
    print(f"     Market changes: {len(market_changes)}")
    
except Exception as e:
    print(f"  ❌ Failed: {e}")
PYEOF
echo ""

echo "================================================================================"
echo "                              SUMMARY"
echo "================================================================================"
echo ""
echo "✅ = Working correctly"
echo "❌ = Needs fixing"
echo ""
echo "================================================================================"
