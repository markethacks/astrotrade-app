import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.trading_logic import TradingCalendar
from core.reports import ReportGenerator
from core.astro_engine import calculate_lagna

st.set_page_config(
    page_title="AstroTrade",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "AstroTrade Personal Assistant v1.6"
    }
)

# Mobile-responsive CSS
st.markdown("""
<style>
    /* Mobile optimizations */
    @media (max-width: 768px) {
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
        
        /* Make metrics stack vertically on mobile */
        [data-testid="stMetric"] {
            background-color: #f8f9fa;
            padding: 0.5rem;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
        }
    }
    
    /* Desktop table styles */
    .cal-table { 
        width: 100%; 
        border-collapse: collapse; 
        font-size: 13px; 
        margin-top: 20px;
        overflow-x: auto;
        display: block;
    }
    
    /* Mobile table styles */
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
    
    /* Mobile-friendly inputs */
    @media (max-width: 768px) {
        input[type="number"] {
            font-size: 16px !important; /* Prevents zoom on iOS */
        }
        .stTextInput input {
            font-size: 16px !important;
        }
    }
    
    /* Improve sidebar on mobile */
    @media (max-width: 768px) {
        section[data-testid="stSidebar"] {
            width: 100% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Mobile detection
def is_mobile():
    return st.session_state.get('mobile_view', False)

# Header - more compact on mobile
st.title("🌙 AstroTrade")
st.caption("*Personalized Astro-Trading Calendar*")

GEOPY_AVAILABLE = False
try:
    from geopy.geocoders import Nominatim
    GEOPY_AVAILABLE = True
except ImportError:
    pass

with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown("### 📋 Profile")
    input_method = st.radio("Choose:", ["📌 Existing", "✏️ Manual"], index=0, label_visibility="collapsed")
    st.markdown("---")
    
    if input_method == "📌 Existing":
        profile_name = st.selectbox("Select Profile", ["Vijay", "Rahul", "Priya"])
        profiles = st.secrets.get("profiles", {})
        if not profiles:
            st.warning("No profiles configured. Contact admin.")
            profiles = {}
        profile_data = profiles[profile_name]
        with st.expander("📄 Details"):
            st.write(f"**DOB:** {profile_data['dob']}")
            st.write(f"**TOB:** {profile_data['tob']}")
            st.write(f"**POB:** {profile_data['pob']}")
            st.write(f"**Lagna:** {profile_data['lagna']}")
    else:
        st.markdown("### ✏️ Manual Entry")
        profile_name = st.text_input("Name", "My Profile", label_visibility="collapsed", placeholder="Your Name")
        
        # Mobile-friendly date/time inputs
        dob = st.date_input("📅 DOB", datetime(1990, 5, 15))
        
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
                        geolocator = Nominatim(user_agent="astrotrade_v1", timeout=10)
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
    
    st.markdown("---")
    st.subheader("📅 Date Range")
    
    today = datetime.now().date()
    three_months = today + timedelta(days=90)
    
    start_date = st.date_input("Start", today, key="start_dt")
    end_date = st.date_input("End", three_months, key="end_dt")
    
    st.markdown("---")
    
    if st.button("🚀 Generate", type="primary", use_container_width=True):
        st.session_state.generate = True
        st.session_state.start_date = start_date
        st.session_state.end_date = end_date
        st.session_state.profile = profile_name
        st.session_state.profile_data = profile_data

if 'generate' not in st.session_state:
    st.info("👆 Configure settings and click Generate")
else:
    with st.spinner('🔮 Calculating...'):
        try:
            calendar = TradingCalendar(st.session_state.profile_data)
            df = calendar.generate_calendar(st.session_state.start_date, st.session_state.end_date)
            st.success(f"✅ {len(df)} days generated!")
            st.session_state.df = df
        except Exception as e:
            st.error(f"Error: {str(e)[:100]}")
            st.stop()
    
    df = st.session_state.df
    tabs = st.tabs(["📅 Calendar", "🌔 Day", "📊 Charts", "📥 Export"])
    
    with tabs[0]:
        st.subheader("📅 Trading Calendar")
        market_changes = df[df.get('change_during_market', False) == True]
        if len(market_changes) > 0:
            st.warning(f"⚠️ {len(market_changes)} market-hour changes")
        
        # Mobile-friendly metrics
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
        
        # Mobile-responsive table
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
                        st.download_button("⬇️ Download Excel", f, file_name=f"astrotrade_{st.session_state.profile}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                    st.success("✅ Ready!")
                except Exception as e:
                    st.error(f"Error: {str(e)[:50]}")
        
        with col2:
            if st.button("📄 CSV", use_container_width=True):
                csv = df.to_csv(index=False)
                st.download_button("⬇️ Download CSV", csv, file_name=f"astrotrade_{st.session_state.profile}.csv", mime="text/csv", use_container_width=True)
        
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

st.markdown("---")
st.caption(f"*v1.7 Mobile | {st.session_state.get('profile', 'Not Set')}*")
