"""
Enhanced Solar Generation Calculator with PVGIS Integration
Uses real-world data from PVGIS API and weather data for accurate predictions
"""

from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class EnhancedLocationData:
    """Enhanced location data with PVGIS support"""
    latitude: float
    longitude: float
    # Optional weather data
    avg_cloud_cover: Optional[float] = None  # Average cloud cover (0-1)
    monthly_cloud_cover: Optional[List[float]] = None  # Monthly cloud cover (0-1)


class EnhancedSolarCalculator:
    """Enhanced solar calculator with PVGIS and weather data integration"""
    
    def __init__(self, use_pvgis: bool = True, use_weather_data: bool = True):
        """
        Initialize enhanced solar calculator
        
        Args:
            use_pvgis: Try to use PVGIS API for accurate data
            use_weather_data: Try to fetch weather data for cloud cover
        """
        self.use_pvgis = use_pvgis
        self.use_weather_data = use_weather_data
        self.pvgis_available = True  # Always available via direct API
        
        # PVGIS API configuration (EU Science Hub)
        self.pvgis_url_base = "https://re.jrc.ec.europa.eu/api/v5_3/"
        
        if use_pvgis:
            print("✓ PVGIS API available (EU Science Hub direct API)")
    
    def get_pvgis_monthly_data(self, lat: float, lon: float, 
                                peak_power_kw: float,
                                tilt: float = 35.0,
                                azimuth: float = 180.0,
                                loss: float = 14.0) -> Optional[Dict]:
        """
        Get monthly solar production data from PVGIS using direct API
        Based on EU Science Hub API documentation
        
        Args:
            lat: Latitude
            lon: Longitude
            peak_power_kw: System peak power in kWp
            tilt: Panel tilt angle (0-90)
            azimuth: Panel azimuth (0=North, 90=East, 180=South, 270=West)
            loss: System losses in % (cables, inverter, etc.)
        
        Returns:
            Dictionary with monthly data or None if unavailable
        """
        if not self.pvgis_available:
            return None
        
        try:
            import urllib.request
            import json
            
            # Build PVGIS API URL according to official documentation
            # https://re.jrc.ec.europa.eu/api/v5_3/PVcalc?
            params = {
                'lat': lat,
                'lon': lon,
                'peakpower': peak_power_kw,
                'angle': tilt,
                'aspect': azimuth,
                'loss': loss,
                'pvtechchoice': 'crystSi',  # Crystalline silicon (most common)
                'mountingplace': 'free',     # Free-standing (vs building-integrated)
                'outputformat': 'json'
            }
            
            # Build query string
            query_string = '&'.join([f'{key}={value}' for key, value in params.items()])
            url = f"{self.pvgis_url_base}PVcalc?{query_string}"
            
            # Debug: print the URL being called
            print(f"🔗 PVGIS API URL: {url}")
            print(f"   Peak Power: {peak_power_kw} kWp")
            print(f"   Tilt: {tilt}°, Azimuth: {azimuth}°")
            print(f"   System Losses: {loss}%")
            
            # Make API request
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            # Extract monthly production values
            result = {
                'monthly_production': {},  # kWh per month
                'monthly_irradiance': {},  # kWh/m² per month
                'annual_production': 0.0,  # Total annual kWh
                'source': 'PVGIS (EU Science Hub)',
                'api_version': 'v5.3'
            }
            
            # Parse the PVGIS JSON response
            # The data is nested under outputs -> monthly -> fixed
            if 'outputs' in data and 'monthly' in data['outputs']:
                monthly_data = data['outputs']['monthly']
                # Data is nested under 'fixed' key for fixed-mounted systems
                if 'fixed' in monthly_data:
                    for entry in monthly_data['fixed']:
                        month = entry.get('month')
                        if month:
                            result['monthly_production'][month] = entry.get('E_m', 0)  # kWh per month
                            result['monthly_irradiance'][month] = entry.get('H(i)_m', 0)  # kWh/m²
            
            # Get annual totals if available
            if 'outputs' in data and 'totals' in data['outputs']:
                totals = data['outputs']['totals']
                if 'fixed' in totals:
                    result['annual_production'] = totals['fixed'].get('E_y', 0)
            
            return result
            
        except urllib.error.HTTPError as e:
            print(f"⚠ PVGIS HTTP error: {e.code} - {e.reason}")
            return None
        except urllib.error.URLError as e:
            print(f"⚠ PVGIS connection error: {str(e)}")
            return None
        except Exception as e:
            print(f"⚠ PVGIS API error: {str(e)}")
            return None
    
    def get_pvgis_hourly_data(self, lat: float, lon: float,
                               peak_power_kw: float,
                               tilt: float = 35.0,
                               azimuth: float = 180.0,
                               loss: float = 14.0,
                               year: int = 2020) -> Optional[Dict]:
        """
        Get hourly solar production data from PVGIS for a full year using direct API
        Based on EU Science Hub API documentation
        
        Args:
            lat: Latitude
            lon: Longitude
            peak_power_kw: System peak power in kWp
            tilt: Panel tilt angle
            azimuth: Panel azimuth
            loss: System losses in %
            year: Year for data (2005-2020 for most locations)
        
        Returns:
            Dictionary with hourly data or None
        """
        if not self.pvgis_available:
            return None
        
        try:
            import urllib.request
            import json
            
            # Build PVGIS API URL for hourly data
            # https://re.jrc.ec.europa.eu/api/v5_3/seriescalc?
            params = {
                'lat': lat,
                'lon': lon,
                'peakpower': peak_power_kw,
                'angle': tilt,
                'aspect': azimuth,
                'loss': loss,
                'startyear': year,
                'endyear': year,
                'outputformat': 'json'
            }
            
            # Build query string
            query_string = '&'.join([f'{key}={value}' for key, value in params.items()])
            url = f"{self.pvgis_url_base}seriescalc?{query_string}"
            
            # Make API request
            with urllib.request.urlopen(url, timeout=30) as response:
                data = json.loads(response.read().decode())
            
            # Process hourly data
            result = {
                'hourly_production': [],  # List of hourly production values in kW
                'timestamps': [],
                'source': 'PVGIS (EU Science Hub)',
                'api_version': 'v5.3'
            }
            
            if 'outputs' in data and 'hourly' in data['outputs']:
                for entry in data['outputs']['hourly']:
                    result['hourly_production'].append(entry.get('P', 0) / 1000.0)  # Convert W to kW
                    result['timestamps'].append(entry.get('time'))
            
            return result
            
        except urllib.error.HTTPError as e:
            print(f"⚠ PVGIS HTTP error: {e.code} - {e.reason}")
            return None
        except urllib.error.URLError as e:
            print(f"⚠ PVGIS connection error: {str(e)}")
            return None
        except Exception as e:
            print(f"⚠ PVGIS hourly data error: {str(e)}")
            return None
    
    def fetch_weather_data(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Fetch historical weather data (cloud cover) from Open-Meteo API
        Open-Meteo is free and doesn't require API key
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            Dictionary with weather data or None
        """
        if not self.use_weather_data:
            return None
        
        try:
            import urllib.request
            import json
            from datetime import datetime, timedelta
            
            # Get last year's data for historical cloud cover
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            # Open-Meteo API endpoint for historical weather
            url = (
                f"https://archive-api.open-meteo.com/v1/archive?"
                f"latitude={lat}&longitude={lon}"
                f"&start_date={start_date.strftime('%Y-%m-%d')}"
                f"&end_date={end_date.strftime('%Y-%m-%d')}"
                f"&daily=cloud_cover_mean"
                f"&timezone=auto"
            )
            
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            if 'daily' in data and 'cloud_cover_mean' in data['daily']:
                cloud_cover_data = data['daily']['cloud_cover_mean']
                
                # Calculate monthly averages
                monthly_cloud_cover = []
                days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                
                start_idx = 0
                for days in days_in_month:
                    end_idx = start_idx + days
                    month_data = cloud_cover_data[start_idx:end_idx]
                    # Filter out None values
                    month_data = [x for x in month_data if x is not None]
                    if month_data:
                        avg = sum(month_data) / len(month_data) / 100.0  # Convert to 0-1
                        monthly_cloud_cover.append(avg)
                    else:
                        monthly_cloud_cover.append(0.5)  # Default
                    start_idx = end_idx
                
                # Overall average
                valid_data = [x for x in cloud_cover_data if x is not None]
                avg_cloud_cover = sum(valid_data) / len(valid_data) / 100.0 if valid_data else 0.5
                
                return {
                    'monthly_cloud_cover': monthly_cloud_cover,
                    'avg_cloud_cover': avg_cloud_cover,
                    'source': 'Open-Meteo Historical Data',
                    'data_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
                }
            
            return None
            
        except Exception as e:
            print(f"⚠ Weather data fetch error: {str(e)}")
            return None
    
    def apply_cloud_cover_correction(self, base_production: float, 
                                     cloud_cover: float) -> float:
        """
        Apply cloud cover correction to solar production
        
        Args:
            base_production: Base production without cloud correction
            cloud_cover: Cloud cover factor (0=clear, 1=fully overcast)
        
        Returns:
            Corrected production value
        """
        # Empirical formula: production reduces with cloud cover
        # Clear sky = 100%, full overcast ≈ 10-20% of clear sky
        reduction_factor = 1.0 - (0.85 * cloud_cover)  # Max 85% reduction
        return base_production * reduction_factor


def calculate_enhanced_solar_production(
    lat: float,
    lon: float,
    peak_power_kw: float,
    tilt: float = 35.0,
    azimuth: float = 180.0,
    system_efficiency: float = 0.965,  # 3.5% losses (PVGIS website default: 1% cable + 2% inverter + 0.5% PV)
    use_pvgis: bool = True,
    use_weather: bool = True
) -> Dict:
    """
    Calculate solar production using enhanced methods
    
    Args:
        lat: Latitude
        lon: Longitude
        peak_power_kw: System size in kWp
        tilt: Panel tilt angle (0-90)
        azimuth: Panel azimuth (0-360, 180=South)
        system_efficiency: Overall system efficiency (0-1)
        use_pvgis: Use PVGIS API if available
        use_weather: Fetch weather data if available
    
    Returns:
        Dictionary with production data and metadata
    """
    calculator = EnhancedSolarCalculator(use_pvgis=use_pvgis, use_weather_data=use_weather)
    
    result = {
        'pvgis_data': None,
        'weather_data': None,
        'monthly_production': {},
        'data_source': 'built-in'
    }
    
    # Calculate system losses (convert efficiency to loss %)
    loss_percent = (1.0 - system_efficiency) * 100.0
    
    # Try PVGIS first
    if use_pvgis:
        pvgis_data = calculator.get_pvgis_monthly_data(
            lat, lon, peak_power_kw, tilt, azimuth, loss_percent
        )
        if pvgis_data:
            result['pvgis_data'] = pvgis_data
            result['monthly_production'] = pvgis_data['monthly_production']
            result['data_source'] = 'PVGIS'
    
    # Fetch weather data (for information only)
    # NOTE: Weather correction is NOT applied to PVGIS data because PVGIS
    # already includes real historical weather conditions from satellite data
    if use_weather:
        weather_data = calculator.fetch_weather_data(lat, lon)
        if weather_data:
            result['weather_data'] = weather_data
            # Store weather info but don't apply correction to PVGIS data
            # PVGIS uses historical satellite irradiance data which already accounts for clouds
    
    # If no PVGIS data, fall back to built-in model
    if not result['monthly_production']:
        result['data_source'] = 'Built-in model (PVGIS unavailable)'
        # Here you could add a simple fallback calculation if needed
    
    return result


if __name__ == "__main__":
    # Example usage
    print("Enhanced Solar Production Calculator")
    print("=" * 60)
    
    # Riga, Latvia coordinates
    lat = 56.95
    lon = 24.11
    
    print(f"\nLocation: Riga, Latvia ({lat}, {lon})")
    print(f"System: 10 kWp, 35° tilt, South-facing")
    print()
    
    result = calculate_enhanced_solar_production(
        lat=lat,
        lon=lon,
        peak_power_kw=10.0,
        tilt=35.0,
        azimuth=180.0,
        system_efficiency=0.965,  # 3.5% losses (PVGIS website default: 1% cable + 2% inverter + 0.5% PV)
        use_pvgis=True,
        use_weather=True
    )
    
    print(f"Data Source: {result['data_source']}")
    print()
    
    if result['monthly_production']:
        print("Monthly Production (kWh):")
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        for i, month_name in enumerate(months, 1):
            production = result['monthly_production'].get(i, 0)
            print(f"  {month_name}: {production:>8.1f} kWh")
        
        annual = sum(result['monthly_production'].values())
        print(f"\n  Annual Total: {annual:>8.1f} kWh")
    
    if result['weather_data']:
        print(f"\nWeather Data: {result['weather_data']['source']}")
        print(f"Average Cloud Cover: {result['weather_data']['avg_cloud_cover']*100:.1f}%")

