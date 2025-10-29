"""
Trading Logic and Calendar Generator
"""
from datetime import datetime, timedelta, date
import pandas as pd
import json
from .astro_engine import AstroCalculator

class TradingCalendar:
    def __init__(self, profile_data, config_path='config.json', holidays_path='data/nse_holidays.csv'):
        """Initialize Trading Calendar"""
        self.profile = profile_data
        self.astro_calc = AstroCalculator()
        
        # Load config
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Load holidays
        try:
            self.holidays_df = pd.read_csv(holidays_path)
            self.holidays_df['date'] = pd.to_datetime(self.holidays_df['date'])
            self.holidays = set(self.holidays_df['date'].dt.date)
        except:
            self.holidays = set()
        
        # Calculate birth chart data
        self.birth_nakshatra = self._get_birth_nakshatra()
        self.birth_moon_sign = self._get_birth_moon_sign()
        self.lagna_sign = self.profile.get('lagna', 'Aries')
    
    def _get_birth_nakshatra(self):
        """Get birth nakshatra"""
        dob = datetime.fromisoformat(self.profile['dob'])
        tob = self.profile['tob']
        
        birth_dt = datetime.combine(dob.date(), datetime.strptime(tob, '%H:%M').time())
        jd = self.astro_calc.get_julian_day(birth_dt)
        moon_long = self.astro_calc.get_moon_position(jd)
        
        return self.astro_calc.get_nakshatra(moon_long)
    
    def _get_birth_moon_sign(self):
        """Get birth moon sign"""
        dob = datetime.fromisoformat(self.profile['dob'])
        tob = self.profile['tob']
        
        birth_dt = datetime.combine(dob.date(), datetime.strptime(tob, '%H:%M').time())
        jd = self.astro_calc.get_julian_day(birth_dt)
        moon_long = self.astro_calc.get_moon_position(jd)
        
        return self.astro_calc.get_moon_sign(moon_long)
    
    def generate_calendar(self, start_date, end_date):
        """Generate complete trading calendar"""
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date).date()
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date).date()
        
        calendar_data = []
        current_date = start_date
        
        while current_date <= end_date:
            day_data = self._analyze_day(current_date)
            calendar_data.append(day_data)
            current_date += timedelta(days=1)
        
        return pd.DataFrame(calendar_data)
    
    def _analyze_day(self, check_date):
        """Analyze a single day for trading"""
        # Create datetime at market open
        dt = datetime.combine(check_date, datetime.strptime('09:15', '%H:%M').time())
        jd = self.astro_calc.get_julian_day(dt)
        
        # Get Moon details
        moon_long = self.astro_calc.get_moon_position(jd)
        nakshatra = self.astro_calc.get_nakshatra(moon_long)
        moon_sign = self.astro_calc.get_moon_sign(moon_long)
        
        # Calculate Navatara
        navatara = self.astro_calc.calculate_navatara(
            nakshatra['index'],
            self.birth_nakshatra['index']
        )
        
        # Find nakshatra change time
        change_time = self.astro_calc.find_nakshatra_change_time(check_date)
        change_during_market = self.astro_calc.is_change_during_market_hours(change_time)
        
        # Get other panchanga details
        tithi = self.astro_calc.get_tithi(jd)
        yoga = self.astro_calc.get_yoga(jd)
        hora = self.astro_calc.get_hora(dt)
        moon_phase = self.astro_calc.get_moon_phase(jd)
        
        # Check retrograde planets
        retrogrades = []
        for planet in ['Mercury', 'Jupiter', 'Saturn']:
            if self.astro_calc.is_planet_retrograde(jd, planet):
                retrogrades.append(planet)
        
        # Check Ashtama
        moon_sign_idx = self.astro_calc.zodiac_signs.index(moon_sign)
        birth_moon_sign_idx = self.astro_calc.zodiac_signs.index(self.birth_moon_sign)
        lagna_idx = self.astro_calc.zodiac_signs.index(self.lagna_sign)
        
        is_ashtama_from_moon = self.astro_calc.calculate_ashtama(moon_sign_idx, birth_moon_sign_idx)
        is_ashtama_from_lagna = self.astro_calc.calculate_ashtama(moon_sign_idx, lagna_idx)
        
        # Determine trading decision
        decision, reasons = self._get_trading_decision(
            navatara, 
            is_ashtama_from_moon, 
            is_ashtama_from_lagna,
            change_during_market,
            moon_phase,
            retrogrades,
            check_date in self.holidays,
            check_date.weekday() in [5, 6]  # Saturday, Sunday
        )
        
        return {
            'date': check_date,
            'weekday': check_date.strftime('%A'),
            'nakshatra': nakshatra['name'],
            'pada': nakshatra['pada'],
            'navatara': navatara,
            'moon_sign': moon_sign,
            'change_time': change_time.strftime('%H:%M') if change_time else 'No change',
            'change_during_market': change_during_market,
            'tithi': f"{tithi['paksha']} {tithi['name']}",
            'yoga': yoga,
            'hora_lord': hora['lord'],
            'day_lord': hora['day_lord'],
            'moon_phase': moon_phase,
            'retrogrades': ', '.join(retrogrades) if retrogrades else 'None',
            'ashtama_moon': is_ashtama_from_moon,
            'ashtama_lagna': is_ashtama_from_lagna,
            'is_holiday': check_date in self.holidays,
            'holiday_name': self._get_holiday_name(check_date),
            'recommendation': decision,
            'reasons': ' | '.join(reasons)
        }
    
    def _get_trading_decision(self, navatara, ashtama_moon, ashtama_lagna, 
                             change_during_market, moon_phase, retrogrades,
                             is_holiday, is_weekend):
        """Determine trading recommendation"""
        reasons = []
        
        # Market closed
        if is_holiday:
            return 'CLOSED', ['Market Holiday']
        if is_weekend:
            return 'CLOSED', ['Weekend']
        
        # Critical avoid conditions
        if navatara in ['Vipat', 'Pratyari', 'Naidhana']:
            reasons.append(f'Navatara: {navatara}')
            return 'AVOID', reasons
        
        if ashtama_moon:
            reasons.append('Moon in 8th from natal Moon')
            return 'AVOID', reasons
        
        # Light trading conditions
        if navatara in ['Janma', 'Kshema']:
            reasons.append(f'Navatara: {navatara}')
            return 'LIGHT', reasons
        
        if ashtama_lagna:
            reasons.append('Moon in 8th from Lagna')
            return 'LIGHT', reasons
        
        if change_during_market:
            reasons.append('Nakshatra changes during market hours')
            return 'LIGHT', reasons
        
        if moon_phase in ['Full Moon', 'New Moon']:
            reasons.append(f'{moon_phase}')
            return 'LIGHT', reasons
        
        if 'Mercury' in retrogrades:
            reasons.append('Mercury Retrograde')
            return 'LIGHT', reasons
        
        # Normal trading
        reasons.append(f'Favorable Navatara: {navatara}')
        return 'TRADE', reasons
    
    def _get_holiday_name(self, check_date):
        """Get holiday name if it's a holiday"""
        if check_date not in self.holidays:
            return ''
        
        holiday_row = self.holidays_df[self.holidays_df['date'].dt.date == check_date]
        if not holiday_row.empty:
            return holiday_row.iloc[0]['description']
        return ''
    
    def get_statistics(self, df):
        """Calculate trading statistics"""
        stats = {
            'total_days': len(df),
            'trade_days': len(df[df['recommendation'] == 'TRADE']),
            'light_days': len(df[df['recommendation'] == 'LIGHT']),
            'avoid_days': len(df[df['recommendation'] == 'AVOID']),
            'closed_days': len(df[df['recommendation'] == 'CLOSED']),
            'nakshatra_changes_market': len(df[df['change_during_market'] == True])
        }
        
        # Navatara distribution
        navatara_dist = df['navatara'].value_counts().to_dict()
        
        # Recommendations by navatara
        rec_by_navatara = df.groupby('navatara')['recommendation'].value_counts().unstack(fill_value=0).to_dict()
        
        return {
            'summary': stats,
            'navatara_distribution': navatara_dist,
            'recommendations_by_navatara': rec_by_navatara
        }
