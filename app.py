import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.trading_logic import TradingCalendar
from core.reports import ReportGenerator
from core.astro_engine import calculate_lagna

st.set_page_config(
    page_title="AstroTradeDays",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': "AstroTradeDays by Market Hacks | v2.0"}
)

# CSS
st.markdown("""
<style>
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
    }
</style>
<div class="market-hacks-badge">⚡ Market Hacks</div>
""", unsafe_allow_html=True)

st.title("🌙 AstroTradeDays")
st.caption("*Personalized Astro-Trading Calendar by Market Hacks*")

GEOPY_AVAILABLE = False
try:
    from geopy.geocoders import Nominatim
    GEOPY_AVAILABLE = True
except ImportError:
    pass

# Profile Management Functions
def get_saved_profiles():
    if 'saved_profiles' not in st.session_state:
        st.session_state.saved_profiles = {}
    return st.session_state.saved_profiles

def save_profile(name, data):
    if 'saved_profiles' not in st.session_state:
        st.session_state.saved_profiles = {}
    st.session_state.saved_profiles[name] = data
    return True

def delete_profile(name):
    if 'saved_profiles' in st.session_state and name in st.session_state.saved_profiles:
        del st.session_state.saved_profiles[name]
        return True
    return False

with st.sidebar:
    st.header("⚙️ Settings")
    
    # Profile Management
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
        profile_name = st.text_input("Profile Name", value=profile_name or "My Profile")
        
        dob = st.date_input("📅 DOB", value=datetime(1990, 5, 15), 
                           min_value=datetime(1900, 1, 1), 
                           max_value=datetime.now())
        
        st.write("⏰ **Time of Birth (IST)**")
        col1, col2 = st.columns(2)
        with col1:
            hour = st.number_input("Hour", min_value=0, max_value=23, value=14, step=1)
        with col2:
            minute = st.number_input("Min", min_value=0, max_value=59, value=30, step=1)
        
        tob_str = f"{hour:02d}:{minute:02d}"
        st.info(f"⏰ **{tob_str}** IST")
        
        st.markdown("### 📍 Birth Place")
        pob_input = st.text_input("City", value="", placeholder="Mumbai, Delhi, etc.")
        
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
                            st.success("✅ Found!")
                        else:
                            st.error("❌ Not found")
                    except Exception as e:
                        st.error(f"❌ {str(e)[:50]}")
        
        if st.session_state.get('fetched_lat'):
            st.success(f"✅ **{st.session_state.get('fetched_city')}**")
            pob = st.session_state.get('fetched_city')
            lat = st.session_state.fetched_lat
            lon = st.session_state.fetched_lon
            if st.button("🔄 Clear", use_container_width=True):
                st.session_state.fetched_lat = None
                st.session_state.fetched_lon = None
                st.rerun()
        else:
            pob = pob_input if pob_input else "Unknown"
            col1, col2 = st.columns(2)
            with col1:
                lat = st.number_input("Lat", value=19.0760, format="%.4f")
            with col2:
                lon = st.number_input("Lon", value=72.8777, format="%.4f")
        
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
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.calc_lagna = None
                st.rerun()
            lagna = st.session_state.calc_lagna
        else:
            lagna = st.selectbox("Select:", ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                                            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"], 
                               index=4)
        
        profile_data = {
            "dob": dob.strftime("%Y-%m-%d"), 
            "tob": tob_str, 
            "pob": pob, 
            "lat": lat, 
            "lon": lon, 
            "lagna": lagna
        }
        
        if st.button("💾 Save Profile", use_container_width=True, type="secondary"):
            if profile_name and profile_name != "My Profile":
                save_profile(profile_name, profile_data)
                st.success(f"✅ Saved '{profile_name}'!")
                st.rerun()
            else:
                st.warning("Please enter a unique profile name")
    else:
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
    
    start_date = st.date_input("Start", today)
    end_date = st.date_input("End", three_months)
    
    st.markdown("---")

    # Generate Button
    if st.button("🚀 Generate Calendar", type="primary", use_container_width=True):
        st.session_state.generate = True
        st.session_state.start_date = start_date
        st.session_state.end_date = end_date
        st.session_state.profile = profile_name
        st.session_state.profile_data = profile_data
        st.rerun()
    
    # GENERATE BUTTON - SIMPLE VERSION

# Main content
if 'generate' not in st.session_state:
    st.info("👈 Configure your birth details in the sidebar, then click **🚀 Generate Calendar**")
    st.markdown("---")
    st.markdown("""
    ### ⚡ About Market Hacks
    
    **Market Hacks** is your trusted source for innovative trading tools and insights.
    
    AstroTradeDays combines ancient Vedic wisdom with modern technology to help traders 
    make informed decisions based on personalized astrological analysis.
    
    🌟 **Features:**
    - ✅ Personalized trading calendars
    - ✅ Nakshatra & Navatara analysis
    - ✅ Market-hour change alerts
    - ✅ Google Calendar integration
    - ✅ Profile management
    - ✅ Mobile responsive
    
    *Built with ❤️ by Market Hacks team*
    """)
else:
    with st.spinner('🔮 Generating your calendar...'):
        try:
            calendar = TradingCalendar(st.session_state.profile_data)
            df = calendar.generate_calendar(st.session_state.start_date, st.session_state.end_date)
            st.balloons()
            st.success(f"✅ **{len(df)} days generated successfully!**")
            st.session_state.df = df
        except Exception as e:
            st.error(f"Error: {str(e)[:100]}")
            st.stop()
    
    df = st.session_state.df
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Days", len(df))
    with col2:
        st.metric("🟢 Trade", len(df[df['recommendation'] == 'TRADE']))
    with col3:
        st.metric("🟡 Light", len(df[df['recommendation'] == 'LIGHT']))
    with col4:
        st.metric("🔴 Avoid", len(df[df['recommendation'] == 'AVOID']))
    
    st.markdown("---")
    
    # Create tabs
    tabs = st.tabs(["📅 Calendar", "📊 Analytics", "📥 Export"])
    
    with tabs[0]:
        st.subheader("📅 Trading Calendar")
        
        # Show market hour changes warning
        market_changes = df[df.get('change_during_market', False) == True]
        if len(market_changes) > 0:
            st.warning(f"⚠️ **{len(market_changes)} market-hour changes detected!**")
        
        # Filter option
        show_only = st.checkbox("Show only market-hour changes", False)
        display_df = market_changes if show_only else df
        
        # Display calendar table
        st.dataframe(
            display_df[['date', 'weekday', 'nakshatra', 'navatara', 'recommendation', 'moon_sign']],
            use_container_width=True,
            hide_index=True
        )
    
    with tabs[1]:
        st.subheader("📊 Analytics")
        
        # Pie chart for recommendations
        import plotly.express as px
        rec_counts = df['recommendation'].value_counts()
        fig = px.pie(
            values=rec_counts.values, 
            names=rec_counts.index,
            title="Recommendation Distribution",
            color=rec_counts.index,
            color_discrete_map={
                'TRADE': '#28a745',
                'LIGHT': '#ffc107', 
                'AVOID': '#dc3545',
                'CLOSED': '#6c757d'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Navatara distribution
        st.markdown("### Navatara Distribution")
        nav_counts = df['navatara'].value_counts()
        fig2 = px.bar(
            x=nav_counts.index,
            y=nav_counts.values,
            labels={'x': 'Navatara', 'y': 'Count'},
            title="Days by Navatara"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with tabs[2]:
        st.subheader("📥 Export Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV export
            csv = df.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv,
                file_name=f"astrotradedays_{st.session_state.profile}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Excel export
            if st.button("📊 Generate Excel", use_container_width=True):
                try:
                    report_gen = ReportGenerator()
                    excel_file = report_gen.create_excel_report(df, st.session_state.profile)
                    with open(excel_file, 'rb') as f:
                        st.download_button(
                            label="⬇️ Download Excel",
                            data=f,
                            file_name=f"astrotradedays_{st.session_state.profile}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    st.success("✅ Excel ready!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        st.markdown("---")
        
        # Show upcoming market-hour changes
        st.markdown("### ⚠️ Upcoming Market-Hour Changes")
        today = datetime.now().date()
        upcoming = df[pd.to_datetime(df['date']).dt.date >= today]
        changes = upcoming[upcoming.get('change_during_market', False) == True].head(10)
        
        if len(changes) > 0:
            for _, row in changes.iterrows():
                date_str = pd.to_datetime(row['date']).strftime('%d %b %Y')
                with st.expander(f"⚠️ {date_str} - {row['weekday']} - {row['recommendation']}"):
                    st.write(f"**Nakshatra:** {row['nakshatra']}")
                    st.write(f"**Navatara:** {row['navatara']}")
                    st.write(f"**Change Time:** {row.get('change_time', 'N/A')}")
                    if row['recommendation'] == 'AVOID':
                        st.error("🚫 Avoid trading on this day")
                    elif row['recommendation'] == 'LIGHT':
                        st.warning("⚠️ Trade with caution")
                    else:
                        st.success("✅ Favorable for trading")
        else:
            st.success("✅ No market-hour changes in upcoming days!")

st.markdown("---")
st.markdown(f"*AstroTradeDays v2.0 by ⚡ Market Hacks*")
