"""
Solar Generation Pattern Generator - Version 2
Generates realistic solar PV generation patterns with location-based irradiance
Integrates with consumption patterns to calculate excess/deficit
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class LocationData:
    """Location information for solar irradiance"""
    name: str
    latitude: float
    longitude: float
    avg_daily_irradiance: float  # kWh/m²/day annual average
    
    # Monthly irradiance factors (relative to annual average)
    # Will be auto-calculated based on latitude if not provided
    monthly_irradiance_factors: Optional[List[float]] = None
    
    def __post_init__(self):
        if self.monthly_irradiance_factors is None:
            self.monthly_irradiance_factors = self.calculate_monthly_factors()
    
    def calculate_monthly_factors(self) -> List[float]:
        """
        Calculate monthly irradiance factors based on latitude
        More accurate than fixed values
        """
        # Simplified model based on latitude
        # Higher latitudes = more extreme seasonal variation
        lat_rad = np.radians(abs(self.latitude))
        
        # Base seasonal curve (Northern hemisphere, centered on June)
        months = np.arange(12)
        day_of_year = [15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345]
        
        # Solar declination and day length calculation
        factors = []
        for doy in day_of_year:
            # Declination angle
            declination = 23.45 * np.sin(np.radians((360/365) * (doy - 81)))
            decl_rad = np.radians(declination)
            
            # Relative day length factor
            # Accounts for shorter days in winter at high latitudes
            cos_sunset = -np.tan(lat_rad) * np.tan(decl_rad)
            cos_sunset = np.clip(cos_sunset, -1, 1)
            
            # Hour angle at sunset
            sunset_angle = np.arccos(cos_sunset)
            
            # Relative irradiance (simplified)
            # Includes day length and sun angle effects
            rel_irradiance = sunset_angle * np.cos(lat_rad - decl_rad)
            factors.append(rel_irradiance)
        
        # Normalize so average = 1.0
        factors = np.array(factors)
        factors = factors / np.mean(factors)
        
        return factors.tolist()


# Predefined locations with typical irradiance values
LOCATIONS = {
    'riga_latvia': LocationData(
        name='Riga, Latvia',
        latitude=56.95,
        longitude=24.11,
        avg_daily_irradiance=2.9  # kWh/m²/day
    ),
    'berlin_germany': LocationData(
        name='Berlin, Germany',
        latitude=52.52,
        longitude=13.40,
        avg_daily_irradiance=3.1
    ),
    'munich_germany': LocationData(
        name='Munich, Germany',
        latitude=48.14,
        longitude=11.58,
        avg_daily_irradiance=3.3
    ),
    'stockholm_sweden': LocationData(
        name='Stockholm, Sweden',
        latitude=59.33,
        longitude=18.07,
        avg_daily_irradiance=2.8
    ),
    'copenhagen_denmark': LocationData(
        name='Copenhagen, Denmark',
        latitude=55.68,
        longitude=12.57,
        avg_daily_irradiance=2.9
    ),
    'warsaw_poland': LocationData(
        name='Warsaw, Poland',
        latitude=52.23,
        longitude=21.01,
        avg_daily_irradiance=3.2
    ),
    'madrid_spain': LocationData(
        name='Madrid, Spain',
        latitude=40.42,
        longitude=-3.70,
        avg_daily_irradiance=4.8
    ),
    'rome_italy': LocationData(
        name='Rome, Italy',
        latitude=41.90,
        longitude=12.50,
        avg_daily_irradiance=4.5
    ),
    'paris_france': LocationData(
        name='Paris, France',
        latitude=48.86,
        longitude=2.35,
        avg_daily_irradiance=3.4
    ),
    'london_uk': LocationData(
        name='London, UK',
        latitude=51.51,
        longitude=-0.13,
        avg_daily_irradiance=2.7
    ),
}


@dataclass
class SolarSystemProfile:
    """Solar PV system profile"""
    name: str
    peak_power_kw: float  # System size in kWp
    location: LocationData
    system_efficiency: float = 0.85  # Inverter, cables, shading losses
    tilt_angle: float = 35.0  # Panel tilt (degrees from horizontal)
    azimuth: float = 180.0  # 180 = South facing (Northern hemisphere)
    annual_degradation_rate: float = 0.005  # 0.5% per year


class SolarGenerationCalculator:
    """Calculate solar PV generation patterns"""
    
    def __init__(self):
        self.pvgis_data = None  # Store PVGIS monthly data if available
    
    def set_pvgis_data(self, monthly_production: Dict[int, float]):
        """
        Set PVGIS monthly production data to use instead of built-in model
        
        Args:
            monthly_production: Dictionary mapping month (1-12) to production in kWh
        """
        self.pvgis_data = monthly_production
        print(f"✓ PVGIS data loaded: {sum(monthly_production.values()):.1f} kWh/year")
    
    def get_hourly_pv_pattern(self, location: LocationData, month: int, tilt: float = 35.0) -> List[float]:
        """
        Get hourly PV production pattern for a specific month
        Returns normalized values (sum = 1.0) representing fraction of daily production per hour
        
        Args:
            location: LocationData with latitude/longitude
            month: Month of year (1-12)
            tilt: Panel tilt angle in degrees
        
        Returns:
            List of 24 hourly fractions (sum = 1.0)
        """
        # Calculate sunrise and sunset based on latitude and month
        lat_rad = np.radians(location.latitude)
        
        # Day of year for middle of month
        days_to_month = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        day_of_year = days_to_month[month - 1] + 15
        
        # Solar declination
        declination = 23.45 * np.sin(np.radians((360/365) * (day_of_year - 81)))
        decl_rad = np.radians(declination)
        
        # Sunrise/sunset calculation
        cos_sunset = -np.tan(lat_rad) * np.tan(decl_rad)
        cos_sunset = np.clip(cos_sunset, -1, 1)
        sunset_hour_angle = np.degrees(np.arccos(cos_sunset)) / 15.0
        
        # Convert to clock time (solar noon at 12:00)
        sunrise_hour = 12.0 - sunset_hour_angle
        sunset_hour = 12.0 + sunset_hour_angle
        
        # Generate hourly pattern with realistic curve
        pattern = []
        for hour in range(24):
            if hour < sunrise_hour - 0.5 or hour > sunset_hour + 0.5:
                pattern.append(0.0)
            else:
                # Use sine curve for smooth production during daylight
                # Peak at solar noon (12:00)
                solar_time = hour - 12.0
                day_length = sunset_hour - sunrise_hour
                
                if abs(solar_time) < day_length / 2:
                    # Cosine squared for realistic bell curve
                    normalized_time = solar_time / (day_length / 2)
                    production = (np.cos(normalized_time * np.pi / 2)) ** 1.8
                    
                    # Account for tilt angle (simplified)
                    # Better tilt match = higher production
                    optimal_tilt = abs(location.latitude)
                    tilt_factor = 1.0 - 0.2 * abs(tilt - optimal_tilt) / 45.0
                    tilt_factor = max(0.7, min(1.0, tilt_factor))
                    
                    production *= tilt_factor
                    pattern.append(production)
                else:
                    pattern.append(0.0)
        
        # Normalize so sum = 1.0
        total = sum(pattern)
        if total > 0:
            pattern = [p / total for p in pattern]
        
        return pattern
    
    def calculate_daily_generation(self, 
                                   system: SolarSystemProfile,
                                   month: int,
                                   year: int = 0) -> float:
        """
        Calculate total daily PV generation for a specific month
        Uses PVGIS data if available, otherwise falls back to built-in model
        
        Args:
            system: SolarSystemProfile with system specs
            month: Month (1-12)
            year: Years since installation (for degradation)
        
        Returns:
            Daily generation in kWh
        """
        # If PVGIS data is available, use it instead of built-in model
        if self.pvgis_data and month in self.pvgis_data:
            # PVGIS gives monthly total, convert to average daily
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            monthly_total = self.pvgis_data[month]
            daily_production = monthly_total / days_in_month[month - 1]
            
            # Apply degradation
            degradation_factor = (1 - system.annual_degradation_rate) ** year
            daily_production *= degradation_factor
            
            return daily_production
        
        # Fall back to built-in model
        # Get monthly irradiance factor
        monthly_factor = system.location.monthly_irradiance_factors[month - 1]
        
        # Calculate daily irradiance for this month
        daily_irradiance = system.location.avg_daily_irradiance * monthly_factor
        
        # Calculate production
        # Production = System size × Daily irradiance × System efficiency
        daily_production = (system.peak_power_kw * 
                          daily_irradiance * 
                          system.system_efficiency)
        
        # Apply degradation
        degradation_factor = (1 - system.annual_degradation_rate) ** year
        daily_production *= degradation_factor
        
        return daily_production
    
    def get_hourly_generation(self,
                             system: SolarSystemProfile,
                             month: int,
                             hour: int,
                             year: int = 0) -> float:
        """
        Get generation for a specific hour
        
        Args:
            system: SolarSystemProfile
            month: Month (1-12)
            hour: Hour (0-23)
            year: Years since installation
        
        Returns:
            Hourly generation in kWh
        """
        daily = self.calculate_daily_generation(system, month, year)
        pattern = self.get_hourly_pv_pattern(system.location, month, system.tilt_angle)
        return daily * pattern[hour]
    
    def calculate_annual_generation(self,
                                   system: SolarSystemProfile,
                                   year: int = 0) -> Dict:
        """
        Calculate annual generation with monthly breakdown
        
        Returns:
            Dictionary with monthly and annual totals
        """
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        monthly_totals = []
        
        for month, days in enumerate(days_in_month, 1):
            daily = self.calculate_daily_generation(system, month, year)
            monthly = daily * days
            monthly_totals.append(monthly)
        
        return {
            'monthly_totals': monthly_totals,
            'annual_total': sum(monthly_totals),
            'average_daily': sum(monthly_totals) / 365,
            'peak_month': np.argmax(monthly_totals) + 1,
            'low_month': np.argmin(monthly_totals) + 1
        }
    
    def calculate_excess_deficit(self,
                                 system: SolarSystemProfile,
                                 consumption_hourly: List[float],
                                 month: int) -> Dict:
        """
        Calculate excess generation and deficit for a day
        
        Args:
            system: SolarSystemProfile
            consumption_hourly: List of 24 hourly consumption values (kWh)
            month: Month (1-12)
        
        Returns:
            Dictionary with excess, deficit, and self-sufficiency
        """
        generation_pattern = self.get_hourly_pv_pattern(system.location, month, system.tilt_angle)
        daily_generation = self.calculate_daily_generation(system, month)
        
        hourly_generation = [daily_generation * p for p in generation_pattern]
        
        excess = []
        deficit = []
        self_consumption = []
        
        for gen, cons in zip(hourly_generation, consumption_hourly):
            if gen > cons:
                excess.append(gen - cons)
                deficit.append(0)
                self_consumption.append(cons)
            else:
                excess.append(0)
                deficit.append(cons - gen)
                self_consumption.append(gen)
        
        total_generation = sum(hourly_generation)
        total_consumption = sum(consumption_hourly)
        total_self_consumption = sum(self_consumption)
        
        return {
            'hourly_generation': hourly_generation,
            'hourly_excess': excess,
            'hourly_deficit': deficit,
            'hourly_self_consumption': self_consumption,
            'total_generation': total_generation,
            'total_consumption': total_consumption,
            'total_excess': sum(excess),
            'total_deficit': sum(deficit),
            'total_self_consumption': total_self_consumption,
            'self_sufficiency_ratio': total_self_consumption / total_consumption if total_consumption > 0 else 0,
            'self_consumption_ratio': total_self_consumption / total_generation if total_generation > 0 else 0
        }


def main():
    """Example usage"""
    print("=" * 80)
    print("SOLAR GENERATION PATTERN CALCULATOR")
    print("=" * 80)
    print()
    
    calculator = SolarGenerationCalculator()
    
    # Create a solar system
    location = LOCATIONS['riga_latvia']
    system = SolarSystemProfile(
        name="5kW Residential System",
        peak_power_kw=5.0,
        location=location,
        tilt_angle=35.0,
        azimuth=180.0
    )
    
    print(f"System: {system.name}")
    print(f"Location: {location.name} ({location.latitude:.2f}°N, {location.longitude:.2f}°E)")
    print(f"System size: {system.peak_power_kw} kWp")
    print(f"Avg irradiance: {location.avg_daily_irradiance} kWh/m²/day")
    print()
    
    # Annual generation
    annual = calculator.calculate_annual_generation(system)
    print(f"Annual generation: {annual['annual_total']:.0f} kWh")
    print(f"Average daily: {annual['average_daily']:.1f} kWh")
    print(f"Peak month: {annual['peak_month']} ({annual['monthly_totals'][annual['peak_month']-1]:.0f} kWh)")
    print(f"Low month: {annual['low_month']} ({annual['monthly_totals'][annual['low_month']-1]:.0f} kWh)")
    print()
    
    # Hourly pattern for summer vs winter
    print("Hourly generation pattern:")
    print("Hour | June (kWh) | December (kWh)")
    print("-----|------------|---------------")
    
    for hour in [6, 9, 12, 15, 18, 21]:
        june_gen = calculator.get_hourly_generation(system, 6, hour)
        dec_gen = calculator.get_hourly_generation(system, 12, hour)
        print(f"{hour:02d}:00 | {june_gen:10.3f} | {dec_gen:13.3f}")


if __name__ == "__main__":
    main()

