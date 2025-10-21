"""
EV Database from Google Sheets - Real-world test data
Fetches actual consumption data from public Google Sheet with real-world EV tests

DATA SOURCE: https://docs.google.com/spreadsheets/d/1V6ucyFGKWuSQzvI8lMzvvWJHrBS82echMVJH37kwgjE
- Real-world test data with actual consumption at different speeds
- Temperature-adjusted values
- Multiple tire/season configurations
- Regularly updated test results

Features:
- Auto-fetches from Google Sheet (if public)
- 24-hour cache for performance
- Falls back to cached data if offline
- Provides consumption at 90 km/h and 120 km/h
"""

import requests
import csv
import json
import os
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import io


class GoogleSheetsEVDatabase:
    """
    EV Database that fetches real-world test data from Google Sheets
    """
    
    # Google Sheets public CSV export URL
    SHEET_ID = "1V6ucyFGKWuSQzvI8lMzvvWJHrBS82echMVJH37kwgjE"
    GID = "735351678"  # TB test results tab
    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
    
    CACHE_FILE = "ev_google_cache.json"
    CACHE_DURATION = 86400  # 24 hours
    
    def __init__(self):
        self.vehicles = {}  # {make: {model: {config: data}}}
        self.cache = self._load_cache()
        self._fetch_data()
    
    def _load_cache(self) -> Dict:
        """Load cached data from file"""
        cache_path = os.path.join(os.path.dirname(__file__), self.CACHE_FILE)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    # Check if cache is still valid
                    if time.time() - cache.get('timestamp', 0) < self.CACHE_DURATION:
                        print(f"Using cached EV data (age: {(time.time() - cache.get('timestamp', 0))/3600:.1f} hours)")
                        return cache
            except Exception as e:
                print(f"Error loading cache: {e}")
        return {'timestamp': 0, 'vehicles': {}}
    
    def _save_cache(self):
        """Save data to cache file"""
        cache_path = os.path.join(os.path.dirname(__file__), self.CACHE_FILE)
        try:
            cache_data = {
                'timestamp': time.time(),
                'vehicles': self.vehicles
            }
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            print(f"Cached EV data saved ({len(self.vehicles)} manufacturers)")
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def _fetch_data(self):
        """Fetch data from Google Sheets or use cache"""
        # Try to use cached data first
        if self.cache.get('vehicles'):
            self.vehicles = self.cache['vehicles']
            total_configs = sum(len(configs) for models in self.vehicles.values() for configs in models.values())
            print(f"Loaded {len(self.vehicles)} manufacturers, {total_configs} configurations from cache")
            return
        
        try:
            print(f"Fetching EV test data from Google Sheets...")
            
            # Fetch CSV data
            response = requests.get(self.SHEET_URL, timeout=10)
            response.raise_for_status()
            
            # Parse CSV
            csv_data = io.StringIO(response.text)
            reader = csv.DictReader(csv_data)
            
            parsed_count = 0
            for row in reader:
                if self._parse_row(row):
                    parsed_count += 1
            
            print(f"Successfully fetched {parsed_count} EV test results from Google Sheets")
            
            # Save to cache
            if self.vehicles:
                self._save_cache()
                total_configs = sum(len(configs) for models in self.vehicles.values() for configs in models.values())
                print(f"Loaded {len(self.vehicles)} manufacturers, {total_configs} configurations")
            
        except Exception as e:
            print(f"Error fetching from Google Sheets: {e}")
            print("Using cached data or fallback")
            # If we have cached data, use it even if expired
            if self.cache.get('vehicles'):
                self.vehicles = self.cache['vehicles']
            else:
                print("No cached data available, using minimal fallback")
                self._load_minimal_fallback()
    
    def _parse_row(self, row: Dict) -> bool:
        """Parse a single CSV row into vehicle data"""
        try:
            # Get car name from first column
            car_name = row.get('Car', '').strip()
            if not car_name or car_name == 'Car':  # Skip header
                return False
            
            # Get consumption (Wh/km)
            try:
                consumption_wh_km = float(row.get('Wh/km', 0))
                if consumption_wh_km == 0:
                    return False
            except (ValueError, TypeError):
                return False
            
            # Convert Wh/km to kWh/100km
            consumption_kwh_100km = consumption_wh_km / 10.0
            
            # Get battery capacity
            try:
                capacity = float(row.get('Capacity', 0))
            except (ValueError, TypeError):
                capacity = None
            
            # Get speed
            try:
                speed = int(row.get('Speed', 0))
            except (ValueError, TypeError):
                speed = None
            
            # Get temperature
            temp = row.get('Temp', '').strip()
            
            # Get season/tires
            season = row.get('Season', '').strip()
            tires = row.get('Tires', '').strip()
            
            # Parse make and model
            # Format examples: "BMW i3s 120 Ah", "Hyundai Ioniq 28 kWh", "Tesla Model 3 Long Range"
            parts = car_name.split(maxsplit=1)
            if len(parts) < 2:
                return False
            
            make = parts[0]
            model_and_config = parts[1]
            
            # Try to split model from configuration
            # Common patterns: "Model 3 Long Range", "i3s 120 Ah", "ID.3 1st 62 kWh"
            model, config = self._split_model_config(model_and_config)
            
            # Build configuration name with test conditions
            config_name = f"{config}"
            if speed:
                config_name += f" ({speed} km/h"
                if temp:
                    config_name += f", {temp}°C"
                if season and season != "Summer":
                    config_name += f", {season}"
                config_name += ")"
            
            # Store in hierarchy
            if make not in self.vehicles:
                self.vehicles[make] = {}
            
            if model not in self.vehicles[make]:
                self.vehicles[make][model] = {}
            
            # Create unique key for this test configuration
            config_key = f"{config} @ {speed}km/h"
            
            self.vehicles[make][model][config_key] = {
                'name': config_name,
                'full_name': car_name,
                'consumption_kwh100km': round(consumption_kwh_100km, 1),
                'battery_kwh': capacity,
                'speed_kmh': speed,
                'temperature_c': temp,
                'season': season,
                'tires': tires,
                'test_conditions': f"{speed}km/h, {temp}°C, {season}, {tires}"
            }
            
            return True
            
        except Exception as e:
            # Silently skip problematic rows
            return False
    
    def _split_model_config(self, model_and_config: str) -> tuple:
        """Split model name from configuration"""
        # Common patterns:
        # "i3s 120 Ah" -> "i3s", "120 Ah"
        # "Ioniq 28 kWh" -> "Ioniq", "28 kWh"
        # "Model 3 Long Range" -> "Model 3", "Long Range"
        # "ID.3 1st 62 kWh" -> "ID.3", "1st 62 kWh"
        # "e-Golf 35.8 kWh" -> "e-Golf", "35.8 kWh"
        
        # Special cases
        if "Model " in model_and_config:  # Tesla Model S/3/X/Y
            idx = model_and_config.index("Model ")
            model_end = model_and_config.find(" ", idx + 7)
            if model_end == -1:
                return model_and_config, "Standard"
            model = model_and_config[:model_end]
            config = model_and_config[model_end:].strip()
            return model, config if config else "Standard"
        
        # Look for battery size pattern (number + kWh)
        import re
        battery_match = re.search(r'(\d+(?:\.\d+)?)\s*kWh', model_and_config)
        if battery_match:
            split_idx = battery_match.start()
            model = model_and_config[:split_idx].strip()
            config = model_and_config[split_idx:].strip()
            return model if model else model_and_config, config if config else "Standard"
        
        # Look for Ah pattern
        ah_match = re.search(r'(\d+)\s*Ah', model_and_config)
        if ah_match:
            split_idx = ah_match.start()
            model = model_and_config[:split_idx].strip()
            config = model_and_config[split_idx:].strip()
            return model if model else model_and_config, config if config else "Standard"
        
        # Default: first word is model, rest is config
        parts = model_and_config.split(maxsplit=1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return model_and_config, "Standard"
    
    def _load_minimal_fallback(self):
        """Load minimal fallback data if nothing else available"""
        print("Loading minimal fallback EV data")
        self.vehicles = {
            "Tesla": {
                "Model 3": {
                    "Standard": {
                        "name": "Standard Range",
                        "full_name": "Tesla Model 3 Standard Range",
                        "consumption_kwh100km": 13.6,
                        "battery_kwh": 60,
                        "speed_kmh": 90,
                        "temperature_c": "15",
                        "season": "Summer",
                        "tires": "Standard",
                        "test_conditions": "Estimated average"
                    }
                }
            },
            "Volkswagen": {
                "ID.3": {
                    "Standard": {
                        "name": "58 kWh",
                        "full_name": "VW ID.3 58 kWh",
                        "consumption_kwh100km": 15.5,
                        "battery_kwh": 58,
                        "speed_kmh": 90,
                        "temperature_c": "15",
                        "season": "Summer",
                        "tires": "Standard",
                        "test_conditions": "Estimated average"
                    }
                }
            }
        }
    
    def get_makes(self) -> List[str]:
        """Get list of available manufacturers"""
        return sorted(self.vehicles.keys())
    
    def get_models(self, make: str) -> List[str]:
        """Get list of models for a manufacturer"""
        if make in self.vehicles:
            return sorted(self.vehicles[make].keys())
        return []
    
    def get_configurations(self, make: str, model: str) -> List[str]:
        """Get list of configurations for a model"""
        if make in self.vehicles and model in self.vehicles[make]:
            # Return configuration names (not keys)
            return [data['name'] for data in self.vehicles[make][model].values()]
        return []
    
    def get_consumption(self, make: str, model: str, configuration: str) -> Optional[float]:
        """Get consumption in kWh/100km for a configuration"""
        if make in self.vehicles and model in self.vehicles[make]:
            # Find configuration by name
            for config_data in self.vehicles[make][model].values():
                if config_data['name'] == configuration:
                    return config_data['consumption_kwh100km']
        return None
    
    def get_configuration_data(self, make: str, model: str, configuration: str) -> Optional[Dict]:
        """Get full configuration data including test conditions"""
        if make in self.vehicles and model in self.vehicles[make]:
            # Find configuration by name
            for config_data in self.vehicles[make][model].values():
                if config_data['name'] == configuration:
                    return config_data
        return None
    
    def get_average_consumption(self, make: str, model: str) -> Optional[float]:
        """Get average consumption across all configurations for a model"""
        if make in self.vehicles and model in self.vehicles[make]:
            consumptions = [
                data['consumption_kwh100km'] 
                for data in self.vehicles[make][model].values()
                if data.get('consumption_kwh100km')
            ]
            if consumptions:
                return round(sum(consumptions) / len(consumptions), 1)
        return None


# Test the database
if __name__ == '__main__':
    print("Testing Google Sheets EV Database...")
    db = GoogleSheetsEVDatabase()
    
    print(f"\nTotal manufacturers: {len(db.get_makes())}")
    print(f"Manufacturers: {', '.join(db.get_makes()[:10])}")
    
    # Test Tesla data
    if "Tesla" in db.get_makes():
        print(f"\nTesla Models: {db.get_models('Tesla')}")
        for model in db.get_models('Tesla')[:3]:
            configs = db.get_configurations('Tesla', model)
            print(f"\n{model} configurations: {len(configs)}")
            for config in configs[:2]:
                data = db.get_configuration_data('Tesla', model, config)
                if data:
                    print(f"  - {config}: {data['consumption_kwh100km']} kWh/100km")
                    print(f"    Test: {data.get('test_conditions', 'N/A')}")

