"""
Example Run Script - Demonstrates AstroTrade Calendar Generation
This script generates a sample calendar and saves outputs
"""

import sys
import os
from datetime import date, datetime
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.trading_logic import TradingCalendar
from core.reports import ReportGenerator

def main():
    print("=" * 70)
    print("🌙 AstroTrade Personal Assistant - Example Run")
    print("=" * 70)
    print()
    
    # Profile data for Vijay
    profile_data = {
        "dob": "1983-11-21",
        "tob": "05:50",
        "pob": "Delhi, India",
        "lat": 28.661,
        "lon": 77.133,
        "lagna": "Libra"
    }
    
    print("📋 Profile: Vijay")
    print(f"   DOB: {profile_data['dob']}")
    print(f"   TOB: {profile_data['tob']}")
    print(f"   POB: {profile_data['pob']}")
    print(f"   Lagna: {profile_data['lagna']}")
    print()
    
    # Date range
    start_date = date(2025, 9, 1)
    end_date = date(2025, 12, 31)
    
    print(f"📅 Generating calendar from {start_date} to {end_date}")
    print()
    
    try:
        # Create trading calendar
        print("🔄 Initializing trading calendar...")
        trading_calendar = TradingCalendar(profile_data)
        
        print(f"   Birth Nakshatra: {trading_calendar.birth_nakshatra['name']}")
        print(f"   Birth Moon Sign: {trading_calendar.birth_moon_sign}")
        print()
        
        # Generate calendar
        print("⏳ Calculating planetary positions...")
        calendar_df = trading_calendar.generate_calendar(start_date, end_date)
        
        print(f"✅ Calendar generated for {len(calendar_df)} days")
        print()
        
        # Statistics
        stats = trading_calendar.get_statistics(calendar_df)
        
        print("=" * 70)
        print("📊 SUMMARY STATISTICS")
        print("=" * 70)
        print(f"Total Days:              {stats['summary']['total_days']}")
        print(f"Trade Days (🟢):         {stats['summary']['trade_days']} ({stats['summary']['trade_days']/stats['summary']['total_days']*100:.1f}%)")
        print(f"Light Days (🟡):         {stats['summary']['light_days']} ({stats['summary']['light_days']/stats['summary']['total_days']*100:.1f}%)")
        print(f"Avoid Days (🔴):         {stats['summary']['avoid_days']} ({stats['summary']['avoid_days']/stats['summary']['total_days']*100:.1f}%)")
        print(f"Closed Days (🔒):        {stats['summary']['closed_days']} ({stats['summary']['closed_days']/stats['summary']['total_days']*100:.1f}%)")
        print(f"Nakshatra Changes:       {stats['summary']['nakshatra_changes_market']} during market hours")
        print()
        
        # Sample days
        print("=" * 70)
        print("📅 SAMPLE TRADING DAYS")
        print("=" * 70)
        print()
        
        # Show first 10 days
        for idx, row in calendar_df.head(10).iterrows():
            emoji_map = {
                'TRADE': '🟢',
                'LIGHT': '🟡',
                'AVOID': '🔴',
                'CLOSED': '🔒'
            }
            
            emoji = emoji_map.get(row['recommendation'], '📊')
            date_str = row['date'].strftime('%d-%b-%Y')
            
            print(f"{emoji} {date_str} ({row['weekday'][:3]})")
            print(f"   Nakshatra: {row['nakshatra']} (Pada {row['pada']}) • {row['navatara']}")
            print(f"   Recommendation: {row['recommendation']}")
            print(f"   Change Time: {row['change_time']}")
            print(f"   Reason: {row['reasons']}")
            print()
        
        # Generate reports
        print("=" * 70)
        print("📄 GENERATING REPORTS")
        print("=" * 70)
        
        report_gen = ReportGenerator()
        
        # Create outputs directory
        os.makedirs('outputs', exist_ok=True)
        
        # Excel report
        excel_path = f"outputs/example_calendar_vijay_{datetime.now().strftime('%Y%m%d')}.xlsx"
        print(f"📊 Generating Excel report: {excel_path}")
        report_gen.generate_excel(calendar_df, "Vijay", excel_path)
        print(f"   ✅ Excel report saved")
        
        # CSV report
        csv_path = f"outputs/example_calendar_vijay_{datetime.now().strftime('%Y%m%d')}.csv"
        print(f"📄 Generating CSV report: {csv_path}")
        report_gen.generate_csv(calendar_df, csv_path)
        print(f"   ✅ CSV report saved")
        
        print()
        
        # Telegram message sample
        print("=" * 70)
        print("📱 SAMPLE TELEGRAM ALERT")
        print("=" * 70)
        print()
        
        sample_day = calendar_df.iloc[5].to_dict()
        message = report_gen.create_telegram_message(sample_day)
        print(message)
        print()
        
        # Navatara distribution
        print("=" * 70)
        print("🌟 NAVATARA DISTRIBUTION")
        print("=" * 70)
        print()
        
        navatara_counts = calendar_df['navatara'].value_counts()
        for navatara, count in navatara_counts.items():
            percentage = count / len(calendar_df) * 100
            bar = '█' * int(percentage / 2)
            print(f"{navatara:15} {count:3d} days ({percentage:5.1f}%) {bar}")
        
        print()
        print("=" * 70)
        print("✅ EXAMPLE RUN COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print()
        print("📁 Reports saved in: outputs/")
        print("🚀 To run the full app: streamlit run app.py")
        print()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print()
        print("💡 Make sure:")
        print("   1. Swiss Ephemeris files are in ./sweph/")
        print("   2. All dependencies are installed: pip install -r requirements.txt")
        print("   3. profiles.json and config.json exist")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
