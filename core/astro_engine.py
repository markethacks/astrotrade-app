"""
Core Astrological Calculations using Swiss Ephemeris
"""
import swisseph as swe
from datetime import datetime, timedelta
import pytz
import math
import json

class AstroCalculator:
    def __init__(self, ayanamsha='LAHIRI'):
        """Initialize Swiss Ephemeris with Lahiri Ayanamsha"""
        # Set ephemeris path (will use default if not set)
        swe.set_ephe_path('')  # Use built-in ephemeris
        
        # Set Ayanamsha
        if ayanamsha == 'LAHIRI':
            swe.set_sid_mode(swe.SIDM_LAHIRI)
        
        # Load nakshatras
        self.nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
            "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        
        self.zodiac_signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        
        self.hora_lords = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
        
    def get_julian_day(self, dt, tz='Asia/Kolkata'):
        """Convert datetime to Julian Day"""
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt)
        
        # Convert to UTC
        if dt.tzinfo is None:
            local_tz = pytz.timezone(tz)
            dt = local_tz.localize(dt)
        
        dt_utc = dt.astimezone(pytz.UTC)
        
        jd = swe.julday(
            dt_utc.year, 
            dt_utc.month, 
            dt_utc.day,
            dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
        )
        return jd
    
    def get_moon_position(self, jd):
        """Get Moon's sidereal longitude"""
        result = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
        return result[0][0]  # Longitude in degrees
    
    def get_planet_position(self, jd, planet):
        """Get planet position"""
        planet_ids = {
            'Sun': swe.SUN,
            'Moon': swe.MOON,
            'Mercury': swe.MERCURY,
            'Venus': swe.VENUS,
            'Mars': swe.MARS,
            'Jupiter': swe.JUPITER,
            'Saturn': swe.SATURN
        }
        
        if planet not in planet_ids:
            return None
        
        result = swe.calc_ut(jd, planet_ids[planet], swe.FLG_SIDEREAL)
        return result[0][0]
    
    def get_nakshatra(self, longitude):
        """Get Nakshatra from longitude"""
        nakshatra_span = 360.0 / 27.0  # 13.333... degrees per nakshatra
        nakshatra_index = int(longitude / nakshatra_span)
        pada = int((longitude % nakshatra_span) / (nakshatra_span / 4)) + 1
        
        return {
            'name': self.nakshatras[nakshatra_index],
            'index': nakshatra_index,
            'pada': pada,
            'longitude': longitude
        }
    
    def get_moon_sign(self, longitude):
        """Get Moon's zodiac sign"""
        sign_index = int(longitude / 30.0)
        return self.zodiac_signs[sign_index]
    
    def calculate_navatara(self, current_nakshatra_idx, birth_nakshatra_idx):
        """Calculate Navatara (9-star classification)"""
        diff = (current_nakshatra_idx - birth_nakshatra_idx) % 27
        navatara_idx = diff % 9
        
        navatara_names = [
            "Janma", "Sampat", "Vipat", "Kshema", "Pratyari", 
            "Sadhana", "Naidhana", "Mitra", "Parama_Mitra"
        ]
        
        return navatara_names[navatara_idx]
    
    def find_nakshatra_change_time(self, date, tz='Asia/Kolkata'):
        """Find exact time when nakshatra changes on a given date"""
        local_tz = pytz.timezone(tz)
        dt_start = local_tz.localize(datetime.combine(date, datetime.min.time()))
        dt_end = dt_start + timedelta(days=1)
        
        jd_start = self.get_julian_day(dt_start)
        jd_end = self.get_julian_day(dt_end)
        
        # Get nakshatra at start
        moon_long_start = self.get_moon_position(jd_start)
        nak_start = self.get_nakshatra(moon_long_start)
        
        # Check if nakshatra changes during the day
        moon_long_end = self.get_moon_position(jd_end)
        nak_end = self.get_nakshatra(moon_long_end)
        
        if nak_start['index'] == nak_end['index']:
            return None  # No change
        
        # Binary search for exact change time
        jd_low = jd_start
        jd_high = jd_end
        
        while (jd_high - jd_low) > 0.0001:  # ~8.6 seconds precision
            jd_mid = (jd_low + jd_high) / 2.0
            moon_long_mid = self.get_moon_position(jd_mid)
            nak_mid = self.get_nakshatra(moon_long_mid)
            
            if nak_mid['index'] == nak_start['index']:
                jd_low = jd_mid
            else:
                jd_high = jd_mid
        
        # Convert JD to datetime
        change_jd = jd_high
        year, month, day, hour = swe.revjul(change_jd)
        
        change_dt_utc = datetime(year, month, day, int(hour), int((hour % 1) * 60))
        change_dt_utc = pytz.UTC.localize(change_dt_utc)
        change_dt_local = change_dt_utc.astimezone(local_tz)
        
        return change_dt_local
    
    def is_change_during_market_hours(self, change_time):
        """Check if nakshatra change occurs during NSE market hours"""
        if change_time is None:
            return False
        
        market_start = change_time.replace(hour=9, minute=15, second=0)
        market_end = change_time.replace(hour=15, minute=30, second=0)
        
        return market_start <= change_time <= market_end
    
    def get_tithi(self, jd):
        """Calculate Tithi (Lunar day)"""
        sun_long = self.get_planet_position(jd, 'Sun')
        moon_long = self.get_moon_position(jd)
        
        # Tithi calculation
        diff = (moon_long - sun_long) % 360
        tithi_num = int(diff / 12.0) + 1
        
        tithi_names = [
            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
            "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
            "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
            "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
            "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
        ]
        
        paksha = "Shukla" if tithi_num <= 15 else "Krishna"
        tithi_name = tithi_names[tithi_num - 1]
        
        return {
            'number': tithi_num,
            'name': tithi_name,
            'paksha': paksha
        }
    
    def get_yoga(self, jd):
        """Calculate Yoga"""
        sun_long = self.get_planet_position(jd, 'Sun')
        moon_long = self.get_moon_position(jd)
        
        yoga_value = (sun_long + moon_long) % 360
        yoga_num = int(yoga_value / (360.0 / 27.0))
        
        yoga_names = [
            "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
            "Atiganda", "Sukarma", "Dhriti", "Shoola", "Ganda",
            "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
            "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
            "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
            "Indra", "Vaidhriti"
        ]
        
        return yoga_names[yoga_num]
    
    def get_hora(self, dt):
        """Calculate Hora (Planetary hour)"""
        # Get weekday (0=Monday, 6=Sunday)
        weekday = dt.weekday()
        
        # Day lords
        day_lords = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
        day_lord = day_lords[weekday]
        
        # Calculate hora from sunrise
        # Simplified: Using 6 AM as sunrise
        sunrise = dt.replace(hour=6, minute=0, second=0)
        
        if dt < sunrise:
            # Before sunrise - use previous day's night hora
            dt_diff = (sunrise - dt).total_seconds() / 3600.0
            hora_num = int(dt_diff) % 7
            prev_day_lord_idx = (weekday - 1) % 7
            lord_idx = (prev_day_lord_idx + 12 - hora_num) % 7
        else:
            # After sunrise
            dt_diff = (dt - sunrise).total_seconds() / 3600.0
            hora_num = int(dt_diff) % 7
            day_lord_idx = weekday
            lord_idx = (day_lord_idx + hora_num) % 7
        
        return {
            'lord': day_lords[lord_idx],
            'day_lord': day_lord
        }
    
    def get_moon_phase(self, jd):
        """Calculate Moon phase"""
        sun_long = self.get_planet_position(jd, 'Sun')
        moon_long = self.get_moon_position(jd)
        
        phase_angle = (moon_long - sun_long) % 360
        
        if phase_angle < 45:
            return "New Moon"
        elif phase_angle < 90:
            return "Waxing Crescent"
        elif phase_angle < 135:
            return "First Quarter"
        elif phase_angle < 180:
            return "Waxing Gibbous"
        elif phase_angle < 225:
            return "Full Moon"
        elif phase_angle < 270:
            return "Waning Gibbous"
        elif phase_angle < 315:
            return "Last Quarter"
        else:
            return "Waning Crescent"
    
    def is_planet_retrograde(self, jd, planet):
        """Check if planet is retrograde"""
        planet_ids = {
            'Mercury': swe.MERCURY,
            'Venus': swe.VENUS,
            'Mars': swe.MARS,
            'Jupiter': swe.JUPITER,
            'Saturn': swe.SATURN
        }
        
        if planet not in planet_ids:
            return False
        
        result = swe.calc_ut(jd, planet_ids[planet], swe.FLG_SIDEREAL | swe.FLG_SPEED)
        speed = result[0][3]  # Daily motion in longitude
        
        return speed < 0
    
    def calculate_ashtama(self, current_sign_idx, reference_sign_idx):
        """Calculate if Moon is in 8th house from reference"""
        diff = (current_sign_idx - reference_sign_idx) % 12
        return diff == 7  # 8th house (0-indexed becomes 7)


def calculate_lagna(date_obj, time_obj, lat, lon):
    """
    Calculate Lagna (Ascendant) for given birth details
    Assumes input time is in IST (Indian Standard Time)
    Converts to UTC for accurate calculation
    """
    import swisseph as swe
    from datetime import datetime, timedelta
    
    # Convert IST to UTC (IST = UTC + 5:30)
    ist_dt = datetime.combine(date_obj, time_obj)
    utc_dt = ist_dt - timedelta(hours=5, minutes=30)
    
    # Calculate Julian day in UTC
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 
                    utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
    
    # Set Lahiri ayanamsa (sidereal zodiac standard in India)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    # Calculate houses using Placidus system
    cusps, ascmc = swe.houses(jd, lat, lon, b'P')
    
    # Get ascendant degree (tropical)
    asc_degree_tropical = ascmc[0]
    
    # Apply ayanamsa to get sidereal ascendant
    ayanamsa = swe.get_ayanamsa(jd)
    sidereal_asc = (asc_degree_tropical - ayanamsa) % 360
    
    # Convert degree to zodiac sign
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    sign_index = int(sidereal_asc / 30)
    return signs[sign_index]
