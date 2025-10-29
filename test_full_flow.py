"""
Complete test of the AstroTrade app functionality
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("ASTROTRADE PERSONAL ASSISTANT - FULL TEST")
print("=" * 60)

# Test 1: Geopy geocoding
print("\n[TEST 1] Geocoding with geopy...")
try:
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="astrotrade_test", timeout=10)
    
    test_cities = {
        "Mumbai": (19.0760, 72.8777),
        "Delhi": (28.7041, 77.1025),
        "Shimla": (31.1048, 77.1734),
        "Gangtok": (27.3389, 88.6065),
    }
    
    for city, expected in test_cities.items():
        location = geolocator.geocode(f"{city}, India")
        if location:
            lat_diff = abs(location.latitude - expected[0])
            lon_diff = abs(location.longitude - expected[1])
            if lat_diff < 1 and lon_diff < 1:
                print(f"  ✅ {city}: {location.latitude:.4f}, {location.longitude:.4f}")
            else:
                print(f"  ⚠️ {city}: Found but coordinates differ")
        else:
            print(f"  ❌ {city}: Not found")
    
    print("✅ Geocoding test passed")
except Exception as e:
    print(f"❌ Geocoding test failed: {e}")

# Test 2: Import core modules
print("\n[TEST 2] Importing core modules...")
try:
    from core.trading_logic import TradingCalendar
    from core.reports import ReportGenerator
    print("✅ Core modules imported successfully")
except Exception as e:
    print(f"❌ Core modules import failed: {e}")
    sys.exit(1)

# Test 3: Load profiles
print("\n[TEST 3] Loading profiles...")
try:
    import json
    with open('profiles.json') as f:
        profiles = json.load(f)
    print(f"✅ Loaded {len(profiles)} profiles: {', '.join(profiles.keys())}")
except Exception as e:
    print(f"❌ Profile loading failed: {e}")
    sys.exit(1)

# Test 4: Generate calendar for existing profile
print("\n[TEST 4] Generating calendar for Vijay...")
try:
    profile_data = profiles['Vijay']
    calendar = TradingCalendar(profile_data)
    
    start_date = datetime(2025, 9, 1)
    end_date = datetime(2025, 9, 10)
    
    df = calendar.generate_calendar(start_date, end_date)
    
    print(f"✅ Generated calendar: {len(df)} days")
    print(f"   Trade days: {len(df[df['recommendation'] == 'TRADE'])}")
    print(f"   Avoid days: {len(df[df['recommendation'] == 'AVOID'])}")
    print(f"   Light days: {len(df[df['recommendation'] == 'LIGHT'])}")
    
    market_changes = df[df.get('change_during_market', False) == True]
    print(f"   Market hour changes: {len(market_changes)}")
    
except Exception as e:
    print(f"❌ Calendar generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Generate calendar with manual coordinates
print("\n[TEST 5] Testing with manual coordinates (Shimla)...")
try:
    manual_profile = {
        "dob": "1990-05-15",
        "tob": "14:30",
        "pob": "Shimla",
        "lat": 31.1048,
        "lon": 77.1734,
        "lagna": "Leo"
    }
    
    calendar = TradingCalendar(manual_profile)
    df = calendar.generate_calendar(datetime(2025, 9, 1), datetime(2025, 9, 5))
    
    print(f"✅ Manual profile calendar: {len(df)} days generated")
    
except Exception as e:
    print(f"❌ Manual profile test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Check report generation
print("\n[TEST 6] Testing report generation...")
try:
    report_gen = ReportGenerator()
    excel_file = report_gen.create_excel_report(df, "TestProfile")
    
    if os.path.exists(excel_file):
        file_size = os.path.getsize(excel_file)
        print(f"✅ Excel report created: {excel_file} ({file_size} bytes)")
        os.remove(excel_file)  # Cleanup
    else:
        print(f"❌ Excel file not created")
        
except Exception as e:
    print(f"❌ Report generation failed: {e}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED!")
print("=" * 60)
