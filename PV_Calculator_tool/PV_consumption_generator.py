"""
PV System Consumption Pattern Generator - Version 2
Generates realistic daily power consumption patterns based on:
- Gaussian distribution for seasonal variation (higher in autumn/winter)
- Workday patterns with baseline during day and evening peaks
- Weekend vs weekday differences
- Customizable consumption profiles
"""

import math
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class ConsumptionPattern:
    """Defines a consumption pattern template"""
    name: str
    description: str
    
    # Base hourly pattern (24 values, normalized to sum to 1.0)
    # Represents fraction of daily consumption per hour
    base_hourly_pattern: List[float]
    
    # Monthly consumption multipliers (12 values)
    # Uses Gaussian-like curve with peak in winter months
    monthly_multipliers: List[float]
    
    # Weekday vs weekend adjustment factors
    weekday_factor: float = 1.0  # Multiplier for weekdays
    weekend_factor: float = 1.1  # Multiplier for weekends
    
    # Average annual consumption in kWh
    annual_consumption_kwh: float = 6000


@dataclass
class EVConsumptionProfile:
    """Represents Electric Vehicle consumption profile"""
    enabled: bool = False
    weekly_distance_km: float = 300.0  # Weekly distance driven (km)
    consumption_per_100km: float = 18.0  # kWh per 100km (typical: 15-20 kWh/100km)
    
    # Charging schedule (which days EV is charged)
    # True = charging day, False = no charging
    # Default: charge on weekdays (Monday-Friday)
    charging_days: List[bool] = field(default_factory=lambda: [True, True, True, True, True, False, False])
    
    # Charging hours (when EV charging happens)
    # Default: overnight charging 22:00-06:00
    charging_hours: List[int] = field(default_factory=lambda: [22, 23, 0, 1, 2, 3, 4, 5, 6])
    
    def get_daily_ev_consumption(self) -> float:
        """Calculate average daily EV consumption in kWh"""
        if not self.enabled:
            return 0.0
        
        # Weekly consumption
        weekly_kwh = (self.weekly_distance_km / 100.0) * self.consumption_per_100km
        
        # Average daily
        return weekly_kwh / 7.0
    
    def get_charging_day_consumption(self) -> float:
        """Calculate consumption per charging day"""
        if not self.enabled:
            return 0.0
        
        weekly_kwh = (self.weekly_distance_km / 100.0) * self.consumption_per_100km
        charging_days_count = sum(self.charging_days)
        
        if charging_days_count == 0:
            return 0.0
        
        return weekly_kwh / charging_days_count


@dataclass
class HouseholdProfile:
    """Represents a specific household consumption profile"""
    name: str
    annual_consumption_kwh: float
    
    # Pattern type: 'working_family', 'retired', 'home_office', 'student', 'custom'
    pattern_type: str = 'working_family'
    
    # Seasonal variation strength (0.0 = no variation, 1.0 = strong variation)
    seasonal_strength: float = 0.5
    
    # Peak consumption time (hour of day, 0-23)
    peak_evening_hour: int = 19
    
    # Weekday/weekend consumption difference
    weekend_increase: float = 0.15  # 15% higher on weekends
    
    # Optional EV profile
    ev_profile: Optional[EVConsumptionProfile] = None


class ConsumptionPatternGenerator:
    """Generates realistic consumption patterns"""
    
    # Predefined patterns
    PATTERNS = {
        'working_family': {
            'name': 'Working Family',
            'description': 'Family with adults working outside home during day. Peak consumption in evening.',
            'base_pattern': [
                0.025, 0.020, 0.020, 0.020, 0.020, 0.025,  # 00:00-05:59 (baseline night)
                0.030, 0.055, 0.045, 0.030, 0.030, 0.030,  # 06:00-11:59 (small morning peak 7-8, then baseline)
                0.030, 0.030, 0.030, 0.030, 0.030, 0.035,  # 12:00-17:59 (baseline throughout day)
                0.065, 0.095, 0.080, 0.070, 0.045, 0.025   # 18:00-23:59 (evening peak 18-22, back to baseline at 23)
            ],
            'winter_peak': True
        },
        'home_office': {
            'name': 'Home Office',
            'description': 'One or more adults working from home. Consistent daytime consumption.',
            'base_pattern': [
                0.025, 0.020, 0.020, 0.020, 0.020, 0.025,  # 00:00-05:59 (baseline night)
                0.035, 0.050, 0.048, 0.048, 0.048, 0.048,  # 06:00-11:59 (morning, then work)
                0.048, 0.048, 0.048, 0.048, 0.048, 0.048,  # 12:00-17:59 (consistent work)
                0.060, 0.075, 0.065, 0.055, 0.040, 0.025   # 18:00-23:59 (evening peak, back to baseline)
            ],
            'winter_peak': True
        },
        'retired': {
            'name': 'Retired Couple',
            'description': 'Retired couple at home most of the day. Steady consumption throughout day.',
            'base_pattern': [
                0.025, 0.020, 0.020, 0.020, 0.020, 0.030,  # 00:00-05:59 (baseline night)
                0.040, 0.048, 0.048, 0.048, 0.048, 0.048,  # 06:00-11:59 (morning activities)
                0.048, 0.048, 0.048, 0.048, 0.048, 0.048,  # 12:00-17:59 (steady afternoon)
                0.055, 0.065, 0.058, 0.050, 0.035, 0.025   # 18:00-23:59 (evening, back to baseline)
            ],
            'winter_peak': True
        },
        'student': {
            'name': 'Student Apartment',
            'description': 'Young adults with irregular schedule. Lower overall consumption.',
            'base_pattern': [
                0.030, 0.028, 0.028, 0.028, 0.028, 0.028,  # 00:00-05:59 (night, some late)
                0.030, 0.042, 0.042, 0.042, 0.042, 0.042,  # 06:00-11:59 (morning)
                0.042, 0.042, 0.042, 0.042, 0.045, 0.050,  # 12:00-17:59 (afternoon)
                0.065, 0.085, 0.075, 0.065, 0.050, 0.030   # 18:00-23:59 (evening peak, back to baseline)
            ],
            'winter_peak': True
        },
        'commercial_small': {
            'name': 'Small Commercial',
            'description': 'Small business or shop with daytime operation.',
            'base_pattern': [
                0.012, 0.012, 0.012, 0.012, 0.012, 0.015,  # 00:00-05:59 (closed, baseline)
                0.025, 0.050, 0.070, 0.075, 0.075, 0.075,  # 06:00-11:59 (opening, peak)
                0.075, 0.075, 0.075, 0.075, 0.070, 0.060,  # 12:00-17:59 (business hours)
                0.045, 0.030, 0.020, 0.012, 0.012, 0.012   # 18:00-23:59 (closing, back to baseline)
            ],
            'winter_peak': False  # More consistent year-round
        }
    }
    
    def __init__(self):
        """Initialize the consumption pattern generator"""
        pass
    
    def generate_gaussian_seasonal_curve(self, 
                                        peak_month: int = 1, 
                                        strength: float = 0.5,
                                        weekend_factor: float = 1.15) -> List[float]:
        """
        Generate Gaussian seasonal curve with peak in winter months
        Properly normalized so annual consumption matches target exactly
        
        Args:
            peak_month: Month with peak consumption (1-12), default 1 (January)
            strength: Strength of seasonal variation (0.0-0.5 recommended)
                     0.0 = flat (no variation)
                     0.1 = minimal variation (1.2x winter/summer, well-insulated home)
                     0.2 = typical variation (1.5x winter/summer, moderate heating)
                     0.3 = high variation (1.9x winter/summer, electric heating)
                     0.5 = very high variation (3x winter/summer, extreme case)
            weekend_factor: Weekend consumption multiplier (default 1.15 = 15% higher)
        
        Returns:
            List of 12 monthly multipliers that account for days per month
            and weekend/weekday distribution
        """
        months = np.arange(12)
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        # Create Gaussian curve centered on peak_month
        # Account for circular nature of months (December -> January)
        center = peak_month - 1  # Convert to 0-indexed
        
        # Calculate distance from center, accounting for circular nature
        distances = []
        for m in months:
            # Distance considering wrap-around
            direct_dist = abs(m - center)
            wrap_dist = 12 - direct_dist
            distances.append(min(direct_dist, wrap_dist))
        
        distances = np.array(distances)
        
        # Gaussian with sigma ~ 2 months for realistic seasonal variation
        sigma = 2.5
        gaussian = np.exp(-(distances ** 2) / (2 * sigma ** 2))
        
        # Normalize to range from (1-strength) to (1+strength)
        # So with strength=0.5: range is 0.5 to 1.5 (3x variation)
        min_val = 1.0 - strength
        max_val = 1.0 + strength
        
        curve = min_val + (max_val - min_val) * (gaussian - gaussian.min()) / (gaussian.max() - gaussian.min())
        
        # IMPORTANT: Normalize to account for:
        # 1. Different number of days per month
        # 2. Weekend consumption factor (weekends are higher)
        
        # Calculate weighted average accounting for weekday/weekend distribution
        # Assume approximately 22 weekdays and rest weekends per month
        weighted_sum = 0
        total_days = 0
        
        for i, days in enumerate(days_in_month):
            weekdays = 22 if days >= 30 else int(days * 22/30)
            weekends = days - weekdays
            
            # Weighted contribution of this month
            # weekday consumption: curve[i] × weekdays
            # weekend consumption: curve[i] × weekend_factor × weekends
            month_weight = curve[i] * weekdays + curve[i] * weekend_factor * weekends
            weighted_sum += month_weight
            total_days += days
        
        # Normalize so that the weighted average across the year equals 1.0
        # This ensures: sum(daily_consumption) = annual_consumption
        normalization_factor = weighted_sum / total_days
        normalized_curve = curve / normalization_factor
        
        return normalized_curve.tolist()
    
    def generate_workday_pattern(self, 
                                 pattern_type: str = 'working_family',
                                 peak_hour: int = 19) -> List[float]:
        """
        Generate hourly consumption pattern for a workday
        
        Args:
            pattern_type: Type of household pattern
            peak_hour: Hour of day with peak consumption (0-23)
        
        Returns:
            List of 24 hourly fractions (sum = 1.0)
        """
        if pattern_type not in self.PATTERNS:
            pattern_type = 'working_family'
        
        base_pattern = self.PATTERNS[pattern_type]['base_pattern'].copy()
        
        # Adjust peak hour if different from default
        default_peak = 19  # 7 PM
        if peak_hour != default_peak:
            shift = peak_hour - default_peak
            # Shift the evening peak
            base_pattern = self.shift_pattern(base_pattern, shift)
        
        # Ensure sum = 1.0
        total = sum(base_pattern)
        if total > 0:
            base_pattern = [p / total for p in base_pattern]
        
        return base_pattern
    
    def shift_pattern(self, pattern: List[float], hours: int) -> List[float]:
        """Shift a pattern by a number of hours"""
        if hours == 0:
            return pattern
        return pattern[hours:] + pattern[:hours]
    
    def generate_weekend_pattern(self) -> List[float]:
        """
        Generate hourly consumption pattern for weekend
        Weekend patterns have:
        - No timed peaks like workdays
        - More spread out throughout the day
        - Overall higher consumption than weekday
        - More consistent/flatter distribution
        
        Returns:
            List of 24 hourly fractions (sum = 1.0)
        """
        # Start with a flatter base pattern for weekends
        weekend = [
            0.025, 0.020, 0.020, 0.020, 0.020, 0.025,  # 00:00-05:59 (night baseline)
            0.035, 0.045, 0.048, 0.048, 0.048, 0.048,  # 06:00-11:59 (gradual increase)
            0.048, 0.048, 0.048, 0.048, 0.048, 0.048,  # 12:00-17:59 (steady throughout day)
            0.050, 0.055, 0.052, 0.048, 0.040, 0.030   # 18:00-23:59 (slight evening increase, back to baseline)
        ]
        
        # Ensure sum = 1.0
        total = sum(weekend)
        if total > 0:
            weekend = [p / total for p in weekend]
        
        return weekend
    
    def create_household_profile(self,
                                name: str,
                                annual_consumption_kwh: float,
                                pattern_type: str = 'working_family',
                                seasonal_strength: float = 0.2,
                                peak_hour: int = 19) -> HouseholdProfile:
        """
        Create a complete household consumption profile
        
        Args:
            name: Name/identifier for the profile
            annual_consumption_kwh: Total annual consumption in kWh
            pattern_type: Type of consumption pattern
            seasonal_strength: Strength of seasonal variation (0.0-1.0)
            peak_hour: Hour of peak evening consumption (0-23)
        
        Returns:
            HouseholdProfile object
        """
        return HouseholdProfile(
            name=name,
            annual_consumption_kwh=annual_consumption_kwh,
            pattern_type=pattern_type,
            seasonal_strength=seasonal_strength,
            peak_evening_hour=peak_hour
        )
    
    def get_daily_consumption(self,
                             profile: HouseholdProfile,
                             month: int,
                             is_weekday: bool = True,
                             day_of_week: int = 0,
                             include_ev: bool = True) -> float:
        """
        Calculate daily consumption for a specific month and day type
        
        Args:
            profile: HouseholdProfile object
            month: Month (1-12)
            is_weekday: True for weekday, False for weekend
            day_of_week: Day of week (0=Monday, 6=Sunday)
            include_ev: Whether to include EV consumption
        
        Returns:
            Daily consumption in kWh (household + EV if enabled)
        """
        # Get seasonal multiplier
        seasonal_curve = self.generate_gaussian_seasonal_curve(
            peak_month=1,  # January peak
            strength=profile.seasonal_strength
        )
        seasonal_multiplier = seasonal_curve[month - 1]
        
        # Calculate base daily consumption (household only)
        base_daily = profile.annual_consumption_kwh / 365.0
        
        # Apply seasonal multiplier
        daily = base_daily * seasonal_multiplier
        
        # Apply weekday/weekend adjustment
        if not is_weekday:
            daily *= (1.0 + profile.weekend_increase)
        
        # Add EV consumption if enabled
        if include_ev and profile.ev_profile and profile.ev_profile.enabled:
            ev_consumption = self.get_ev_daily_consumption(profile.ev_profile, day_of_week)
            daily += ev_consumption
        
        return daily
    
    def get_ev_daily_consumption(self, ev_profile: EVConsumptionProfile, day_of_week: int) -> float:
        """
        Get EV consumption for a specific day
        
        Args:
            ev_profile: EVConsumptionProfile object
            day_of_week: Day of week (0=Monday, 6=Sunday)
        
        Returns:
            Daily EV consumption in kWh (0 if not a charging day)
        """
        if not ev_profile.enabled:
            return 0.0
        
        # Check if this is a charging day
        if not ev_profile.charging_days[day_of_week]:
            return 0.0
        
        return ev_profile.get_charging_day_consumption()
    
    def get_ev_hourly_consumption(self, ev_profile: EVConsumptionProfile, 
                                   day_of_week: int, hour: int) -> float:
        """
        Get EV consumption for a specific hour
        
        Args:
            ev_profile: EVConsumptionProfile object
            day_of_week: Day of week (0=Monday, 6=Sunday)
            hour: Hour of day (0-23)
        
        Returns:
            Hourly EV consumption in kWh (0 if not charging at this hour)
        """
        if not ev_profile.enabled:
            return 0.0
        
        # Check if this is a charging day
        if not ev_profile.charging_days[day_of_week]:
            return 0.0
        
        # Check if this is a charging hour
        if hour not in ev_profile.charging_hours:
            return 0.0
        
        # Distribute daily EV consumption across charging hours
        daily_ev = ev_profile.get_charging_day_consumption()
        return daily_ev / len(ev_profile.charging_hours)
    
    def get_hourly_consumption(self,
                              profile: HouseholdProfile,
                              month: int,
                              day_of_week: int,
                              hour: int,
                              include_ev: bool = True) -> float:
        """
        Get consumption for a specific hour (household + EV)
        
        Args:
            profile: HouseholdProfile object
            month: Month (1-12)
            day_of_week: Day of week (0=Monday, 6=Sunday)
            hour: Hour of day (0-23)
            include_ev: Whether to include EV consumption
        
        Returns:
            Hourly consumption in kWh (household + EV if enabled)
        """
        is_weekday = day_of_week < 5  # Monday-Friday
        
        # Get daily household consumption (without EV)
        daily_household = self.get_daily_consumption(profile, month, is_weekday, day_of_week, include_ev=False)
        
        # Get hourly pattern for household
        if is_weekday:
            pattern = self.generate_workday_pattern(
                profile.pattern_type,
                profile.peak_evening_hour
            )
        else:
            pattern = self.generate_weekend_pattern()
        
        # Calculate household hourly consumption
        hourly_household = daily_household * pattern[hour]
        
        # Add EV consumption if enabled
        hourly_ev = 0.0
        if include_ev and profile.ev_profile and profile.ev_profile.enabled:
            hourly_ev = self.get_ev_hourly_consumption(profile.ev_profile, day_of_week, hour)
        
        return hourly_household + hourly_ev
    
    def generate_year_consumption(self,
                                 profile: HouseholdProfile,
                                 start_date: datetime = None) -> Dict:
        """
        Generate full year of hourly consumption data (household + EV)
        
        Args:
            profile: HouseholdProfile object
            start_date: Starting date (defaults to Jan 1 of current year)
        
        Returns:
            Dictionary with consumption data and statistics
        """
        if start_date is None:
            start_date = datetime(datetime.now().year, 1, 1)
        
        # Generate data for each day of the year
        daily_data = []
        hourly_data = []
        
        # Track totals
        total_household_annual = 0.0
        total_ev_annual = 0.0
        
        current_date = start_date
        for _ in range(365):
            month = current_date.month
            day_of_week = current_date.weekday()
            is_weekday = day_of_week < 5
            
            # Get household consumption (without EV)
            daily_household = self.get_daily_consumption(profile, month, is_weekday, day_of_week, include_ev=False)
            
            # Get EV consumption for this day
            daily_ev = 0.0
            if profile.ev_profile and profile.ev_profile.enabled:
                daily_ev = self.get_ev_daily_consumption(profile.ev_profile, day_of_week)
            
            # Total daily consumption
            daily_consumption = daily_household + daily_ev
            
            total_household_annual += daily_household
            total_ev_annual += daily_ev
            
            day_hourly = []
            day_hourly_household = []
            day_hourly_ev = []
            
            for hour in range(24):
                # Household hourly
                hourly_household = self.get_hourly_consumption(profile, month, day_of_week, hour, include_ev=False)
                day_hourly_household.append(hourly_household)
                
                # EV hourly
                hourly_ev = 0.0
                if profile.ev_profile and profile.ev_profile.enabled:
                    hourly_ev = self.get_ev_hourly_consumption(profile.ev_profile, day_of_week, hour)
                day_hourly_ev.append(hourly_ev)
                
                # Total hourly
                hourly_total = hourly_household + hourly_ev
                day_hourly.append(hourly_total)
                
                hourly_data.append({
                    'date': current_date,
                    'hour': hour,
                    'consumption_kwh': hourly_total,
                    'household_kwh': hourly_household,
                    'ev_kwh': hourly_ev
                })
            
            daily_data.append({
                'date': current_date,
                'month': month,
                'day_of_week': day_of_week,
                'is_weekday': is_weekday,
                'daily_consumption_kwh': daily_consumption,
                'household_consumption_kwh': daily_household,
                'ev_consumption_kwh': daily_ev,
                'hourly_consumption': day_hourly,
                'hourly_household': day_hourly_household,
                'hourly_ev': day_hourly_ev
            })
            
            current_date += timedelta(days=1)
        
        # Calculate statistics
        total_annual = total_household_annual + total_ev_annual
        avg_daily = total_annual / 365
        avg_daily_household = total_household_annual / 365
        avg_daily_ev = total_ev_annual / 365
        
        monthly_totals = {}
        monthly_household = {}
        monthly_ev = {}
        
        for d in daily_data:
            month = d['month']
            if month not in monthly_totals:
                monthly_totals[month] = 0
                monthly_household[month] = 0
                monthly_ev[month] = 0
            monthly_totals[month] += d['daily_consumption_kwh']
            monthly_household[month] += d['household_consumption_kwh']
            monthly_ev[month] += d['ev_consumption_kwh']
        
        return {
            'profile': profile,
            'daily_data': daily_data,
            'hourly_data': hourly_data,
            'statistics': {
                'total_annual_kwh': total_annual,
                'household_annual_kwh': total_household_annual,
                'ev_annual_kwh': total_ev_annual,
                'average_daily_kwh': avg_daily,
                'average_daily_household_kwh': avg_daily_household,
                'average_daily_ev_kwh': avg_daily_ev,
                'monthly_totals': monthly_totals,
                'monthly_household': monthly_household,
                'monthly_ev': monthly_ev,
                'peak_month': max(monthly_totals, key=monthly_totals.get),
                'low_month': min(monthly_totals, key=monthly_totals.get)
            }
        }
    
    def get_pattern_info(self, pattern_type: str) -> Optional[Dict]:
        """Get information about a pattern type"""
        if pattern_type in self.PATTERNS:
            return self.PATTERNS[pattern_type]
        return None
    
    def get_available_patterns(self) -> List[str]:
        """Get list of available pattern types"""
        return list(self.PATTERNS.keys())


def main():
    """Example usage of the consumption pattern generator"""
    print("=" * 80)
    print("PV Consumption Pattern Generator - Version 2 (with EV support)")
    print("=" * 80)
    print()
    
    generator = ConsumptionPatternGenerator()
    
    # Example 1: Working family without EV
    print("Example 1: Working Family (without EV)")
    print("-" * 80)
    profile1 = generator.create_household_profile(
        name="Working Family",
        annual_consumption_kwh=6000,
        pattern_type='working_family',
        seasonal_strength=0.6,  # Strong seasonal variation
        peak_hour=19
    )
    
    # Show some example days
    print(f"Annual Consumption: {profile1.annual_consumption_kwh} kWh")
    print(f"Pattern Type: {profile1.pattern_type}")
    print(f"Seasonal Strength: {profile1.seasonal_strength}")
    print()
    
    # January weekday (winter, high consumption)
    jan_weekday = generator.get_daily_consumption(profile1, 1, True, 0)
    print(f"January Weekday: {jan_weekday:.2f} kWh/day")
    
    # July weekday (summer, low consumption)
    jul_weekday = generator.get_daily_consumption(profile1, 7, True, 0)
    print(f"July Weekday: {jul_weekday:.2f} kWh/day")
    
    # Weekend vs weekday
    jan_weekend = generator.get_daily_consumption(profile1, 1, False, 5)
    print(f"January Weekend: {jan_weekend:.2f} kWh/day")
    print()
    
    # Example 2: Working family WITH EV
    print("=" * 80)
    print("Example 2: Working Family with EV")
    print("-" * 80)
    
    # Create EV profile
    ev_profile = EVConsumptionProfile(
        enabled=True,
        weekly_distance_km=300,  # 300 km per week
        consumption_per_100km=18.0,  # 18 kWh/100km (typical for mid-size EV)
        charging_days=[True, True, True, True, True, False, False],  # Charge Mon-Fri
        charging_hours=[22, 23, 0, 1, 2, 3, 4, 5, 6]  # Charge 22:00-06:00
    )
    
    profile2 = generator.create_household_profile(
        name="Working Family with EV",
        annual_consumption_kwh=6000,
        pattern_type='working_family',
        seasonal_strength=0.6,
        peak_hour=19
    )
    profile2.ev_profile = ev_profile
    
    print(f"Household Annual Consumption: {profile2.annual_consumption_kwh} kWh")
    print(f"EV Weekly Distance: {ev_profile.weekly_distance_km} km")
    print(f"EV Consumption: {ev_profile.consumption_per_100km} kWh/100km")
    print(f"EV Daily Average: {ev_profile.get_daily_ev_consumption():.2f} kWh/day")
    print(f"EV Annual: {ev_profile.get_daily_ev_consumption() * 365:.0f} kWh/year")
    print()
    
    # Show daily consumption with EV
    jan_weekday_ev = generator.get_daily_consumption(profile2, 1, True, 0)  # Monday
    jan_weekend_ev = generator.get_daily_consumption(profile2, 1, False, 5)  # Saturday
    print(f"January Weekday (with EV): {jan_weekday_ev:.2f} kWh/day")
    print(f"January Weekend (no EV charging): {jan_weekend_ev:.2f} kWh/day")
    print()
    
    # Show hourly pattern with EV
    print("Hourly Pattern (January Monday - with EV charging):")
    for hour in range(24):
        consumption = generator.get_hourly_consumption(profile2, 1, 0, hour)  # Monday
        household = generator.get_hourly_consumption(profile2, 1, 0, hour, include_ev=False)
        ev = consumption - household
        bar = "█" * int(consumption * 10)
        ev_marker = " ⚡" if ev > 0 else ""
        print(f"{hour:02d}:00 | {consumption:5.3f} kWh (H:{household:5.3f} EV:{ev:5.3f}) {bar}{ev_marker}")
    print()
    
    # Example 3: Generate full year with EV
    print("=" * 80)
    print("Generating Full Year Data (with EV)...")
    year_data = generator.generate_year_consumption(profile2)
    
    stats = year_data['statistics']
    print("\nStatistics:")
    print(f"Total Annual: {stats['total_annual_kwh']:.0f} kWh")
    print(f"  - Household: {stats['household_annual_kwh']:.0f} kWh")
    print(f"  - EV: {stats['ev_annual_kwh']:.0f} kWh")
    print(f"Average Daily: {stats['average_daily_kwh']:.2f} kWh")
    print(f"  - Household: {stats['average_daily_household_kwh']:.2f} kWh")
    print(f"  - EV: {stats['average_daily_ev_kwh']:.2f} kWh")
    print(f"Peak Month: {stats['peak_month']} ({stats['monthly_totals'][stats['peak_month']]:.0f} kWh)")
    print(f"Low Month: {stats['low_month']} ({stats['monthly_totals'][stats['low_month']]:.0f} kWh)")
    print()
    
    # Example 4: Available patterns
    print("=" * 80)
    print("Available Patterns:")
    for pattern_type in generator.get_available_patterns():
        info = generator.get_pattern_info(pattern_type)
        print(f"\n{info['name']}:")
        print(f"  {info['description']}")


if __name__ == "__main__":
    main()

