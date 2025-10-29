import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.trading_logic import TradingCalendar
from core.reports import ReportGenerator

st.set_page_config(page_title="AstroTrade", page_icon="🌙", layout="wide")
st.title("🌙 AstroTrade Personal Assistant")

with st.sidebar:
    st.header("⚙️ Settings")
    
    # THIS IS THE RADIO BUTTON - MAKE SURE IT'S VISIBLE
    st.markdown("### 📋 How do you want to input your profile?")
    
    input_method = st.radio(
        "Choose input method:",
        options=["📌 Use Existing Profile", "✏️ Enter Manual Details"],
        index=0
    )
    
    st.markdown("---")
    
    if input_method == "📌 Use Existing Profile":
        st.markdown("### 👤 Select Profile")
        profile_name = st.selectbox("Profile", ["Vijay", "Rahul", "Priya"])
        
        import json
        with open('profiles.json') as f:
            profiles = json.load(f)
        profile_data = profiles[profile_name]
        
        with st.expander("View Details"):
            st.write(f"**DOB:** {profile_data['dob']}")
            st.write(f"**TOB:** {profile_data['tob']}")
            st.write(f"**POB:** {profile_data['pob']}")
    
    else:
        st.markdown("### ✏️ Manual Entry")
        
        profile_name = st.text_input("Name", "My Profile")
        
        col1, col2 = st.columns(2)
        with col1:
            dob = st.date_input("DOB", datetime(1990, 5, 15))
        with col2:
            tob = st.time_input("TOB", datetime.strptime("14:30", "%H:%M").time())
        
        pob = st.text_input("Place", "Mumbai")
        
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Lat", value=19.0760, format="%.4f")
        with col2:
            lon = st.number_input("Lon", value=72.8777, format="%.4f")
        
        lagna = st.selectbox("Lagna", ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                                       "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"], index=4)
        
        profile_data = {
            "dob": dob.strftime("%Y-%m-%d"),
            "tob": tob.strftime("%H:%M"),
            "pob": pob,
            "lat": lat,
            "lon": lon,
            "lagna": lagna
        }
    
    st.markdown("---")
    st.subheader("📅 Date Range")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start", datetime(2025, 9, 1))
    with col2:
        end_date = st.date_input("End", datetime(2025, 12, 31))
    
    st.markdown("---")
    
    if st.button("🚀 Generate", type="primary", use_container_width=True):
        st.session_state.generate = True
        st.session_state.start_date = start_date
        st.session_state.end_date = end_date
        st.session_state.profile = profile_name
        st.session_state.profile_data = profile_data

if 'generate' not in st.session_state:
    st.info("Configure sidebar and click Generate")
else:
    with st.spinner('Calculating...'):
        try:
            calendar = TradingCalendar(st.session_state.profile_data)
            df = calendar.generate_calendar(st.session_state.start_date, st.session_state.end_date)
            st.success(f"✅ Generated {len(df)} days!")
            st.session_state.df = df
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.stop()
    
    df = st.session_state.df
    tabs = st.tabs(["Calendar", "Panchanga", "Analytics", "Reports"])
    
    with tabs[0]:
        st.subheader("Trading Calendar")
        
        market_changes = df[df.get('change_during_market', False) == True]
        if len(market_changes) > 0:
            st.error(f"⚠️ {len(market_changes)} days with market hour changes!")
        
        col1, col2, col3, col4 = st.columns(4)
        total = len(df)
        with col1:
            st.metric("Total", total)
        with col2:
            st.metric("Trade", len(df[df['recommendation'] == 'TRADE']))
        with col3:
            st.metric("Avoid", len(df[df['recommendation'] == 'AVOID']))
        with col4:
            st.metric("Market Changes", len(market_changes))
        
        st.dataframe(df, use_container_width=True, height=600)
    
    with tabs[1]:
        st.subheader("Panchanga")
        selected_date = st.date_input("Date", pd.to_datetime(df['date'].iloc[0]).date())
        day_data = df[pd.to_datetime(df['date']).dt.date == selected_date]
        if not day_data.empty:
            row = day_data.iloc[0]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Nakshatra", row['nakshatra'])
            with col2:
                st.metric("Navatara", row['navatara'])
            with col3:
                st.metric("Recommendation", row['recommendation'])
    
    with tabs[2]:
        st.subheader("Analytics")
        rec_counts = df['recommendation'].value_counts()
        fig = px.pie(values=rec_counts.values, names=rec_counts.index, title="Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[3]:
        st.subheader("Reports")
        if st.button("Download CSV"):
            csv = df.to_csv(index=False)
            st.download_button("Download", csv, "calendar.csv", "text/csv")

st.markdown(f"*v1.1 | {st.session_state.get('profile', 'Not Set')}*")
