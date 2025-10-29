import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.trading_logic import TradingCalendar
from core.reports import ReportGenerator
from core.astro_engine import calculate_lagna

st.set_page_config(
    page_title="AstroTradeDays",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "AstroTradeDays by Market Hacks | v2.0"
    }
)

# Mobile-responsive CSS
st.markdown("""
<style>
    /* Market Hacks Branding */
    .market-hacks-badge {
        position: fixed;
        top: 10px;
        right: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
        z-index: 1000;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    @media (max-width: 768px) {
        .market-hacks-badge {
            top: 5px;
            right: 5px;
            padding: 6px 12px;
            font-size: 11px;
        }
        .main .block-container {
            padding: 1rem 0.5rem;
            max-width: 100%;
        }
        .stButton button {
            width: 100%;
            font-size: 16px !important;
            padding: 0.75rem !important;
        }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
    }
    
    .cal-table { 
        width: 100%; 
        border-collapse: collapse; 
        font-size: 13px; 
        margin-top: 20px;
        overflow-x: auto;
        display: block;
    }
    
    @media (max-width: 768px) {
        .cal-table {
            font-size: 11px;
        }
        .cal-table th, .cal-table td {
            padding: 6px 4px !important;
        }
    }
    
    .cal-table th { 
        background: #2c3e50; 
        color: white; 
        padding: 12px 8px; 
        text-align: left; 
        font-weight: bold;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    .cal-table td { padding: 10px 8px; border: 1px solid #ddd; }
    .market-alert { 
        border: 3px solid #dc3545 !important; 
        box-shadow: 0 0 10px rgba(220, 53, 69, 0.5); 
    }
    .trade-bg { background-color: #d4edda; }
    .light-bg { background-color: #fff3cd; }
    .avoid-bg { background-color: #f8d7da; }
    .closed-bg { background-color: #e2e3e5; }
    .warn-text { color: #dc3545; font-weight: bold; }
    
    @media (max-width: 768px) {
        input[type="number"], .stTextInput input {
            font-size: 16px !important;
        }
    }
</style>

<div class="market-hacks-badge">
    ⚡ Market Hacks
</div>
""", unsafe_allow_html=True)

# Header
st.title("🌙 AstroTradeDays")
st.caption("*Personalized Astro-Trading Calendar by Market Hacks*")

GEOPY_AVAILABLE = False
try:
    from geopy.geocoders import Nominatim
    GEOPY_AVAILABLE = True
except ImportError:
    pass

# Local storage helper functions
def get_saved_profiles():
    """Get saved profiles from browser storage simulation"""
    if 'saved_profiles' not in st.session_state:
        st.session_state.saved_profiles = {}
    return st.session_state.saved_profiles

def save_profile(name, data):
    """Save profile locally"""
    if 'saved_profiles' not in st.session_state:
        st.session_state.saved_profiles = {}
    st.session_state.saved_profiles[name] = data
    return True

def delete_profile(name):
    """Delete saved profile"""
    if 'saved_profiles' in st.session_state and name in st.session_state.saved_profiles:
        del st.session_state.saved_profiles[name]
        return True
    return False

def generate_google_calendar_link(date, title, description):
    """Generate Google Calendar add event link"""
    from urllib.parse import quote
    
    # Format: YYYYMMDD
    date_str = date.strftime('%Y%m%d')
    
    # All-day event format
    dates = f"{date_str}/{date_str}"
    
    # Encode parameters
    text = quote(title)
    details = quote(description)
    
    # Generate link
    link = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={text}&dates={dates}&details={details}&sf=true"
    
    return link

with st.sidebar:
    st.header("⚙️ Settings")
    
    # Profile Management Section
    st.markdown("### 👤 Profile Management")
    
    saved_profiles = get_saved_profiles()
    
    if saved_profiles:
        profile_names = ["➕ New Profile"] + list(saved_profiles.keys())
        selected_profile = st.selectbox("Select Profile", profile_names)
        
        if selected_profile != "➕ New Profile":
            if st.button("🗑️ Delete Profile", use_container_width=True):
                delete_profile(selected_profile)
                st.success(f"Deleted {selected_profile}")
                st.rerun()
            
            # Load profile data
            profile_data = saved_profiles[selected_profile]
            profile_name = selected_profile
            load_existing = True
        else:
            load_existing = False
            profile_name = ""
    else:
        load_existing = False
        profile_name = ""
    
    st.markdown("---")
    
    if not load_existing:
        st.markdown("### ✏️ Enter Details")
        profile_name = st.text_input("Profile Name", value=profile_name or "My Profile", placeholder="e.g., John Trader")
        
        dob = st.date_input("📅 DOB", value=datetime(1990, 5, 15), min_value=datetime(1900, 1, 1), max_value=datetime.now())
        
        st.write("⏰ **Time of Birth (IST)**")
        col1, col2 = st.columns(2)
        with col1:
            hour = st.number_input("Hour", min_value=0, max_value=23, value=14, step=1, format="%d", key="hour_input")
        with col2:
            minute = st.number_input("Min", min_value=0, max_value=59, value=30, step=1, format="%d", key="min_input")
        
        tob_str = f"{hour:02d}:{minute:02d}"
        st.info(f"⏰ **{tob_str}** IST")
        
        st.markdown("### 📍 Birth Place")
        pob_input = st.text_input("City", value="", placeholder="Mumbai, Delhi, etc.", label_visibility="collapsed")
        
        if pob_input and GEOPY_AVAILABLE:
            if st.button("🔍 Fetch Coordinates", use_container_width=True):
                with st.spinner('Searching...'):
                    try:
                        geolocator = Nominatim(user_agent="astrotradedays_v2", timeout=10)
                        location = geolocator.geocode(f"{pob_input}, India")
                        if location:
                            st.session_state.fetched_lat = location.latitude
                            st.session_state.fetched_lon = location.longitude
                            st.session_state.fetched_city = pob_input
                            st.success(f"✅ Found!")
                        else:
                            st.error("❌ Not found")
                            st.session_state.fetched_lat = None
                            st.session_state.fetched_lon = None
                    except Exception as e:
                        st.error(f"❌ {str(e)[:50]}")
        
        if st.session_state.get('fetched_lat'):
            st.success(f"✅ **{st.session_state.get('fetched_city')}**")
            pob = st.session_state.get('fetched_city')
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Lat", f"{st.session_state.fetched_lat:.4f}")
                lat = st.session_state.fetched_lat
            with col2:
                st.metric("Lon", f"{st.session_state.fetched_lon:.4f}")
                lon = st.session_state.fetched_lon
            if st.button("🔄 Clear", use_container_width=True):
                st.session_state.fetched_lat = None
                st.session_state.fetched_lon = None
                st.rerun()
        else:
            st.caption("📍 Manual Coordinates")
            pob = pob_input if pob_input else "Unknown"
            col1, col2 = st.columns(2)
            with col1:
                lat = st.number_input("Lat", value=19.0760, format="%.4f", key="lat_manual")
            with col2:
                lon = st.number_input("Lon", value=72.8777, format="%.4f", key="lon_manual")
        
        st.markdown("---")
        st.markdown("### 🌟 Lagna")
        
        if st.button("🔮 Calculate", use_container_width=True):
            with st.spinner("Calculating..."):
                try:
                    tob = datetime.strptime(tob_str, "%H:%M").time()
                    result = calculate_lagna(dob, tob, lat, lon)
                    st.session_state.calc_lagna = result
                    st.success(f"✅ **{result}**")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {str(e)[:50]}")
        
        if st.session_state.get('calc_lagna'):
            st.info(f"**{st.session_state.calc_lagna}**")
            if st.button("🔄 Reset", use_container_width=True, key="reset_lagna"):
                st.session_state.calc_lagna = None
                st.rerun()
            lagna = st.session_state.calc_lagna
        else:
            lagna = st.selectbox("Select:", ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"], index=4, label_visibility="collapsed")
        
        profile_data = {"dob": dob.strftime("%Y-%m-%d"), "tob": tob_str, "pob": pob, "lat": lat, "lon": lon, "lagna": lagna}
        
        # Save profile button
        if st.button("💾 Save Profile", use_container_width=True, type="secondary"):
            if profile_name and profile_name != "My Profile":
                save_profile(profile_name, profile_data)
                st.success(f"✅ Saved '{profile_name}'!")
                st.rerun()
            else:
                st.warning("Please enter a unique profile name")
    else:
        # Show loaded profile
        st.success(f"📋 **{profile_name}**")
        with st.expander("View Details"):
            st.write(f"**DOB:** {profile_data['dob']}")
            st.write(f"**TOB:** {profile_data['tob']}")
            st.write(f"**POB:** {profile_data['pob']}")
            st.write(f"**Lagna:** {profile_data['lagna']}")
    
    st.markdown("---")
    st.subheader("📅 Date Range")
    
    today = datetime.now().date()
    three_months = today + timedelta(days=90)
    
    start_date = st.date_input("Start", today, key="start_dt")
    end_date = st.date_input("End", three_months, key="end_dt")
    
    st.markdown("---")
    
    # Initialize states
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'generation_complete' not in st.session_state:
    st.session_state.generation_complete = False

# Button styling and logic
button_clicked = False

if st.session_state.get('generation_complete', False):
    # GREEN button after completion
    st.markdown("""
    <style>
    div[data-testid="stSidebar"] .stButton > button {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }
    div[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #218838 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    button_clicked = st.button("✅ Complete - Regenerate?", key="gen_btn", use_container_width=True)
    
elif st.session_state.get('processing', False):
    # ORANGE button during processing
    st.markdown("""
    <style>
    div[data-testid="stSidebar"] .stButton > button {
        background-color: #ff9800 !important;
        color: white !important;
        border: none !important;
        cursor: not-allowed !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.button("⏳ Processing...", key="gen_btn", disabled=True, use_container_width=True)
    
else:
    # RED button initially
    st.markdown("""
    <style>
    div[data-testid="stSidebar"] .stButton > button {
        background-color: #dc3545 !important;
        color: white !important;
        border: none !important;
    }
    div[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #c82333 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Handle button click
if button_clicked:
        
    # Yellow/Orange button during processing
    st.markdown("""
    <style>
    .stButton button[kind="primary"] {
        background-color: #ff9800 !important;
        border-color: #ff9800 !important;
        cursor: wait !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.button("⏳ Processing... Please Wait", type="primary", disabled=True, use_container_width=True)
    
else:
    # Red button initially (default primary color or custom red)
    st.markdown("""
    <style>
    .stButton button[kind="primary"] {
        background-color: #dc3545 !important;
        border-color: #dc3545 !important;
    }
    .stButton button[kind="primary"]:hover {
        background-color: #c82333 !important;
        border-color: #bd2130 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    

if 'generate' not in st.session_state:
    st.info("👈 Configure your birth details in the **sidebar** on the left, then click the **Generate Calendar** button at the bottom of the sidebar.")
    
    # Show Market Hacks branding
    st.markdown("""
    ### ⚡ About Market Hacks
    
    **Market Hacks** is your trusted source for innovative trading tools and insights. 
    
    AstroTradeDays combines ancient Vedic wisdom with modern technology to help traders 
    make informed decisions based on personalized astrological analysis.
    
    🌟 **Features:**
    - Personalized trading calendars
    - Nakshatra & Navatara analysis
    - Market-hour change alerts
    - Google Calendar integration
    - Profile management
    
    *Built with ❤️ by Market Hacks team*
    """)
else:
    with st.spinner('🔮 Calculating...'):
        try:
            calendar = TradingCalendar(st.session_state.profile_data)
            df = calendar.generate_calendar(st.session_state.start_date, st.session_state.end_date)
            st.success(f"✅ {len(df)} days generated!")
            st.session_state.df = df
            
            # IMPORTANT: Update states BEFORE showing success
            st.session_state.processing = False
            st.session_state.generation_complete = True
        except Exception as e:
            st.error(f"Error: {str(e)[:100]}")
            st.stop()
    
    df = st.session_state.df
    tabs = st.tabs(["📅 Calendar", "🌔 Day", "📊 Charts", "📥 Export", "📆 Google Cal"])
    
    with tabs[0]:
        st.subheader("📅 Trading Calendar")
        market_changes = df[df.get('change_during_market', False) == True]
        if len(market_changes) > 0:
            st.warning(f"⚠️ {len(market_changes)} market-hour changes")
        
        cols = st.columns(5)
        with cols[0]:
            st.metric("Total", len(df))
        with cols[1]:
            st.metric("Trade", len(df[df['recommendation'] == 'TRADE']))
        with cols[2]:
            st.metric("Light", len(df[df['recommendation'] == 'LIGHT']))
        with cols[3]:
            st.metric("Avoid", len(df[df['recommendation'] == 'AVOID']))
        with cols[4]:
            st.metric("Changes", len(market_changes))
        
        st.markdown("---")
        show_only = st.checkbox("Show changes only", False)
        filtered_df = df.copy()
        if show_only:
            filtered_df = filtered_df[filtered_df.get('change_during_market', False) == True]
        
        html = """<div style="overflow-x: auto;"><table class="cal-table"><thead><tr><th>Date</th><th>Day</th><th>Nakshatra</th><th>Navatara</th><th>Time</th><th>Rec</th></tr></thead><tbody>"""
        for _, row in filtered_df.iterrows():
            rec = row['recommendation']
            is_market = row.get('change_during_market', False)
            bg = 'trade-bg' if rec == 'TRADE' else 'light-bg' if rec == 'LIGHT' else 'avoid-bg' if rec == 'AVOID' else 'closed-bg'
            row_class = f"{bg} {'market-alert' if is_market else ''}"
            date_str = pd.to_datetime(row['date']).strftime('%d %b')
            warn = '⚠️ ' if is_market else ''
            html += f"""<tr class="{row_class}"><td>{warn}{date_str}</td><td>{row['weekday'][:3]}</td><td>{row['nakshatra'][:8]}</td><td>{row['navatara'][:6]}</td><td>{row.get('change_time', '-')}</td><td><b>{rec}</b></td></tr>"""
        html += "</tbody></table></div>"
        st.markdown(html, unsafe_allow_html=True)
    
    with tabs[1]:
        st.subheader("🌔 Daily Panchanga")
        selected_date = st.date_input("Select Date", pd.to_datetime(df['date'].iloc[0]).date(), key="day_select")
        day_data = df[pd.to_datetime(df['date']).dt.date == selected_date]
        if not day_data.empty:
            row = day_data.iloc[0]
            if row.get('change_during_market', False):
                st.error(f"⚠️ Change at {row.get('change_time')}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Date", str(row['date'])[:10])
                st.metric("Day", row['weekday'])
            with col2:
                st.metric("Nakshatra", row['nakshatra'])
                st.metric("Navatara", row['navatara'])
            with col3:
                st.metric("Recommendation", row['recommendation'])
                st.metric("Moon", row['moon_sign'])
            
            st.markdown("---")
            st.write(row['reasons'])
    
    with tabs[2]:
        st.subheader("📊 Analytics")
        rec_counts = df['recommendation'].value_counts()
        fig = px.pie(values=rec_counts.values, names=rec_counts.index, title="Distribution",
                     color=rec_counts.index, color_discrete_map={'TRADE': '#28a745', 'LIGHT': '#ffc107', 'AVOID': '#dc3545', 'CLOSED': '#6c757d'})
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[3]:
        st.subheader("📥 Export Reports")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Excel", use_container_width=True):
                try:
                    report_gen = ReportGenerator()
                    excel_file = report_gen.create_excel_report(df, st.session_state.profile)
                    with open(excel_file, 'rb') as f:
                        st.download_button("⬇️ Download Excel", f, file_name=f"astrotradedays_{st.session_state.profile}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                    st.success("✅ Ready!")
                except Exception as e:
                    st.error(f"Error: {str(e)[:50]}")
        
        with col2:
            if st.button("📄 CSV", use_container_width=True):
                csv = df.to_csv(index=False)
                st.download_button("⬇️ Download CSV", csv, file_name=f"astrotradedays_{st.session_state.profile}.csv", mime="text/csv", use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📍 Upcoming Changes")
        today = datetime.now().date()
        upcoming = df[pd.to_datetime(df['date']).dt.date >= today]
        changes = upcoming[upcoming.get('change_during_market', False) == True].head(5)
        
        if len(changes) > 0:
            for _, row in changes.iterrows():
                date_str = pd.to_datetime(row['date']).strftime('%d %b')
                rec = row['recommendation']
                emoji = "✅" if rec == 'TRADE' else "⚠️" if rec == 'LIGHT' else "🚫"
                with st.expander(f"{emoji} {date_str} - {row.get('change_time')} - {rec}"):
                    st.write(f"**{row['nakshatra']}** ({row['navatara']})")
                    if rec == 'TRADE':
                        st.success("💡 Favorable for trading")
                    elif rec == 'LIGHT':
                        st.warning("💡 Trade with caution")
                    else:
                        st.error("💡 Avoid trading")
        else:
            st.success("✅ No changes ahead")
    
    with tabs[4]:
        st.subheader("📆 Add No-Trading Days to Google Calendar")
        
        st.info("💡 Click links below to add AVOID days to your Google Calendar")
        
        # Filter AVOID days
        avoid_days = df[df['recommendation'] == 'AVOID']
        
        if len(avoid_days) > 0:
            st.write(f"**{len(avoid_days)} No-Trading Days Found:**")
            
            for _, row in avoid_days.iterrows():
                date = pd.to_datetime(row['date']).date()
                date_str = date.strftime('%d %b %Y')
                
                title = f"🚫 No Trading Day - {row['nakshatra']}"
                description = f"Navatara: {row['navatara']}\\n{row['reasons']}\\n\\nGenerated by AstroTradeDays (Market Hacks)"
                
                gcal_link = generate_google_calendar_link(date, title, description)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{date_str}** - {row['weekday']} - {row['nakshatra']}")
                with col2:
                    st.link_button("➕ Add", gcal_link, use_container_width=True)
            
            # Bulk add option
            st.markdown("---")
            st.markdown("### 🔗 Bulk Add (Copy Links)")
            
            with st.expander("📋 Show All Links"):
                for _, row in avoid_days.iterrows():
                    date = pd.to_datetime(row['date']).date()
                    title = f"🚫 No Trading Day - {row['nakshatra']}"
                    description = f"Navatara: {row['navatara']}\\n{row['reasons']}\\n\\nBy AstroTradeDays"
                    gcal_link = generate_google_calendar_link(date, title, description)
                    st.code(gcal_link, language=None)
        else:
            st.success("✅ No AVOID days in selected range!")

st.markdown("---")
st.markdown(f"*AstroTradeDays v2.0 by ⚡ Market Hacks | Profile: {st.session_state.get('profile', 'Not Set')}*")
