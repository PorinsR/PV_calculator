"""
Enhanced EV Data Fetcher
Fetches real-world EV consumption data from ev-database.org
"""

import urllib.request
import urllib.parse
import json
import re
from typing import Optional, Dict, List


class EVDatabaseFetcher:
    """Fetch EV consumption data from various sources"""
    
    def __init__(self):
        self.cache = {}
        self.base_database = self._load_base_database()
    
    def _load_base_database(self) -> Dict:
        """
        Load comprehensive built-in EV database
        Uses the same 33-manufacturer database as the dropdown selections
        Data sourced from ev-database.org (as of 2024/2025)
        """
        try:
            from PV_ev_database_comprehensive import get_comprehensive_database
            return get_comprehensive_database()
        except ImportError:
            print("Warning: Could not load comprehensive database, using fallback")
            return self._get_fallback_database()
    
    def _get_fallback_database(self) -> Dict:
        """Fallback database if comprehensive not available"""
        return {
            "Tesla": {
                "Model 3": {
                    "RWD (2024)": {"battery_kwh": 60, "drivetrain": "RWD", "year": 2024, "consumption_whkm": 136, "consumption_kwh100km": 13.6, "source": "ev-database.org 2024"},
                    "Long Range AWD (2024)": {"battery_kwh": 75, "drivetrain": "AWD", "year": 2024, "consumption_whkm": 142, "consumption_kwh100km": 14.2, "source": "ev-database.org 2024"},
                    "Performance AWD (2024)": {"battery_kwh": 75, "drivetrain": "AWD", "year": 2024, "consumption_whkm": 152, "consumption_kwh100km": 15.2, "source": "ev-database.org 2024"},
                },
                "Model Y": {
                    "RWD (2024)": {"battery_kwh": 60, "drivetrain": "RWD", "year": 2024, "consumption_whkm": 161, "consumption_kwh100km": 16.1, "source": "ev-database.org 2024"},
                    "Long Range AWD (2024)": {"battery_kwh": 75, "drivetrain": "AWD", "year": 2024, "consumption_whkm": 165, "consumption_kwh100km": 16.5, "source": "ev-database.org 2024"},
                    "Performance AWD (2024)": {"battery_kwh": 75, "drivetrain": "AWD", "year": 2024, "consumption_whkm": 170, "consumption_kwh100km": 17.0, "source": "ev-database.org 2024"},
                },
                "Model S": {
                    "Long Range AWD (2024)": {"battery_kwh": 100, "drivetrain": "AWD", "year": 2024, "consumption_whkm": 181, "consumption_kwh100km": 18.1, "source": "ev-database.org 2024"},
                    "Plaid AWD (2024)": {"battery_kwh": 100, "drivetrain": "AWD", "year": 2024, "consumption_whkm": 195, "consumption_kwh100km": 19.5, "source": "ev-database.org 2024"},
                },
                "Model X": {
                    "Long Range AWD (2024)": {"battery_kwh": 100, "drivetrain": "AWD", "year": 2024, "consumption_whkm": 202, "consumption_kwh100km": 20.2, "source": "ev-database.org 2024"},
                    "Plaid AWD (2024)": {"battery_kwh": 100, "drivetrain": "AWD", "year": 2024, "consumption_whkm": 210, "consumption_kwh100km": 21.0, "source": "ev-database.org 2024"},
                },
            },
            "tesla model y": {"consumption_whkm": 161, "consumption_kwh100km": 16.1, "source": "ev-database.org 2024"},
            "tesla model y long range": {"consumption_whkm": 165, "consumption_kwh100km": 16.5, "source": "ev-database.org 2024"},
            "tesla model s": {"consumption_whkm": 181, "consumption_kwh100km": 18.1, "source": "ev-database.org 2024"},
            "tesla model x": {"consumption_whkm": 202, "consumption_kwh100km": 20.2, "source": "ev-database.org 2024"},
            
            # BMW
            "bmw i3": {"consumption_whkm": 158, "consumption_kwh100km": 15.8, "source": "ev-database.org"},
            "bmw i4 edrive40": {"consumption_whkm": 161, "consumption_kwh100km": 16.1, "source": "ev-database.org"},
            "bmw i4 m50": {"consumption_whkm": 180, "consumption_kwh100km": 18.0, "source": "ev-database.org"},
            "bmw ix xdrive40": {"consumption_whkm": 194, "consumption_kwh100km": 19.4, "source": "ev-database.org"},
            "bmw ix xdrive50": {"consumption_whkm": 214, "consumption_kwh100km": 21.4, "source": "ev-database.org"},
            
            # Volkswagen
            "volkswagen id.3": {"consumption_whkm": 154, "consumption_kwh100km": 15.4, "source": "ev-database.org"},
            "volkswagen id.3 pro": {"consumption_whkm": 159, "consumption_kwh100km": 15.9, "source": "ev-database.org"},
            "volkswagen id.4": {"consumption_whkm": 169, "consumption_kwh100km": 16.9, "source": "ev-database.org"},
            "volkswagen id.5": {"consumption_whkm": 180, "consumption_kwh100km": 18.0, "source": "ev-database.org"},
            "volkswagen id.buzz": {"consumption_whkm": 200, "consumption_kwh100km": 20.0, "source": "ev-database.org"},
            
            # Audi
            "audi e-tron": {"consumption_whkm": 224, "consumption_kwh100km": 22.4, "source": "ev-database.org"},
            "audi e-tron gt": {"consumption_whkm": 196, "consumption_kwh100km": 19.6, "source": "ev-database.org"},
            "audi q4 e-tron": {"consumption_whkm": 170, "consumption_kwh100km": 17.0, "source": "ev-database.org"},
            
            # Mercedes
            "mercedes eqc": {"consumption_whkm": 213, "consumption_kwh100km": 21.3, "source": "ev-database.org"},
            "mercedes eqs": {"consumption_whkm": 191, "consumption_kwh100km": 19.1, "source": "ev-database.org"},
            "mercedes eqe": {"consumption_whkm": 173, "consumption_kwh100km": 17.3, "source": "ev-database.org"},
            "mercedes eqa": {"consumption_whkm": 169, "consumption_kwh100km": 16.9, "source": "ev-database.org"},
            "mercedes cla": {"consumption_whkm": 145, "consumption_kwh100km": 14.5, "source": "ev-database.org 2024"},
            
            # Hyundai
            "hyundai kona": {"consumption_whkm": 147, "consumption_kwh100km": 14.7, "source": "ev-database.org"},
            "hyundai kona electric": {"consumption_whkm": 147, "consumption_kwh100km": 14.7, "source": "ev-database.org"},
            "hyundai ioniq 5": {"consumption_whkm": 168, "consumption_kwh100km": 16.8, "source": "ev-database.org"},
            "hyundai ioniq 6": {"consumption_whkm": 149, "consumption_kwh100km": 14.9, "source": "ev-database.org"},
            "hyundai inster": {"consumption_whkm": 153, "consumption_kwh100km": 15.3, "source": "ev-database.org 2024"},
            
            # Kia
            "kia niro ev": {"consumption_whkm": 159, "consumption_kwh100km": 15.9, "source": "ev-database.org"},
            "kia ev6": {"consumption_whkm": 165, "consumption_kwh100km": 16.5, "source": "ev-database.org"},
            "kia ev6 gt": {"consumption_whkm": 180, "consumption_kwh100km": 18.0, "source": "ev-database.org"},
            
            # Polestar
            "polestar 2": {"consumption_whkm": 165, "consumption_kwh100km": 16.5, "source": "ev-database.org"},
            "polestar 3": {"consumption_whkm": 190, "consumption_kwh100km": 19.0, "source": "ev-database.org"},
            
            # Others
            "nissan leaf": {"consumption_whkm": 170, "consumption_kwh100km": 17.0, "source": "ev-database.org"},
            "nissan ariya": {"consumption_whkm": 180, "consumption_kwh100km": 18.0, "source": "ev-database.org"},
            "renault zoe": {"consumption_whkm": 172, "consumption_kwh100km": 17.2, "source": "ev-database.org"},
            "renault megane e-tech": {"consumption_whkm": 152, "consumption_kwh100km": 15.2, "source": "ev-database.org"},
            "porsche taycan": {"consumption_whkm": 208, "consumption_kwh100km": 20.8, "source": "ev-database.org"},
            "jaguar i-pace": {"consumption_whkm": 220, "consumption_kwh100km": 22.0, "source": "ev-database.org"},
            "mini cooper e": {"consumption_whkm": 146, "consumption_kwh100km": 14.6, "source": "ev-database.org 2024"},
            "mini cooper se": {"consumption_whkm": 149, "consumption_kwh100km": 14.9, "source": "ev-database.org 2024"},
            "fiat 500e": {"consumption_whkm": 130, "consumption_kwh100km": 13.0, "source": "ev-database.org"},
            "skoda enyaq": {"consumption_whkm": 167, "consumption_kwh100km": 16.7, "source": "ev-database.org"},
            "mg4": {"consumption_whkm": 155, "consumption_kwh100km": 15.5, "source": "ev-database.org"},
            "mg zs ev": {"consumption_whkm": 173, "consumption_kwh100km": 17.3, "source": "ev-database.org"},
            "byd atto 3": {"consumption_whkm": 160, "consumption_kwh100km": 16.0, "source": "ev-database.org"},
            "peugeot e-208": {"consumption_whkm": 152, "consumption_kwh100km": 15.2, "source": "ev-database.org"},
            "opel corsa-e": {"consumption_whkm": 152, "consumption_kwh100km": 15.2, "source": "ev-database.org"},
            "citroën ë-c4": {"consumption_whkm": 163, "consumption_kwh100km": 16.3, "source": "ev-database.org"},
            "ford mustang mach-e": {"consumption_whkm": 185, "consumption_kwh100km": 18.5, "source": "ev-database.org"},
            "volvo xc40 recharge": {"consumption_whkm": 193, "consumption_kwh100km": 19.3, "source": "ev-database.org"},
            "volvo c40 recharge": {"consumption_whkm": 190, "consumption_kwh100km": 19.0, "source": "ev-database.org"},
            "lucid air": {"consumption_whkm": 152, "consumption_kwh100km": 15.2, "source": "ev-database.org"},
            "rivian r1t": {"consumption_whkm": 240, "consumption_kwh100km": 24.0, "source": "ev-database.org est"},
            "chevrolet bolt": {"consumption_whkm": 169, "consumption_kwh100km": 16.9, "source": "ev-database.org"},
        }
    
    def search_ev(self, make: str, model: str) -> Optional[Dict]:
        """
        Search for EV in database
        
        Args:
            make: Vehicle make (e.g., "Tesla")
            model: Vehicle model (e.g., "Model 3")
        
        Returns:
            Dictionary with consumption data or None
        """
        # Normalize search term
        search_term = f"{make} {model}".lower().strip()
        
        # Try exact match first
        if search_term in self.base_database:
            data = self.base_database[search_term].copy()
            data['matched_name'] = search_term
            return data
        
        # Try partial matching
        make_lower = make.lower()
        model_lower = model.lower().replace(" ", "")
        
        best_match = None
        best_score = 0
        
        for key, data in self.base_database.items():
            key_no_spaces = key.replace(" ", "")
            
            if make_lower in key and model_lower in key_no_spaces:
                # Calculate match quality
                score = len(model_lower) / len(key_no_spaces)
                if score > best_score:
                    best_score = score
                    best_match = data.copy()
                    best_match['matched_name'] = key
        
        return best_match
    
    def get_all_makes(self) -> List[str]:
        """Get list of all available makes"""
        makes = sorted(set(k.split()[0] for k in self.base_database.keys()))
        return makes
    
    def get_models_by_make(self, make: str) -> List[str]:
        """Get all models for a specific make"""
        make_lower = make.lower()
        models = []
        for key in self.base_database.keys():
            if key.startswith(make_lower):
                # Extract model name (everything after make)
                model = key[len(make_lower):].strip()
                models.append(model)
        return sorted(set(models))
    
    def get_consumption_kwh100km(self, make: str, model: str) -> Optional[float]:
        """
        Get consumption in kWh/100km format
        
        Args:
            make: Vehicle make
            model: Vehicle model
        
        Returns:
            Consumption in kWh/100km or None
        """
        result = self.search_ev(make, model)
        if result:
            return result.get('consumption_kwh100km')
        return None


def fetch_ev_consumption(make: str, model: str) -> Dict:
    """
    Fetch EV consumption data
    
    Args:
        make: Vehicle make
        model: Vehicle model
    
    Returns:
        Dictionary with consumption data and metadata
    """
    fetcher = EVDatabaseFetcher()
    result = fetcher.search_ev(make, model)
    
    if result:
        return {
            'found': True,
            'consumption_kwh100km': result['consumption_kwh100km'],
            'consumption_whkm': result['consumption_whkm'],
            'source': result['source'],
            'matched_name': result['matched_name'].title(),
            'note': 'Real-world consumption varies ±20-30% based on driving conditions, weather, and driving style'
        }
    else:
        available_makes = fetcher.get_all_makes()
        return {
            'found': False,
            'error': f"Vehicle '{make} {model}' not found in database",
            'available_makes': available_makes,
            'suggestion': 'Check spelling or try without trim level'
        }


if __name__ == "__main__":
    print("Enhanced EV Database Fetcher")
    print("=" * 60)
    print("Data source: ev-database.org (2024/2025)\n")
    
    # Test searches
    test_cases = [
        ("Tesla", "Model 3"),
        ("BMW", "i4"),
        ("Volkswagen", "ID.4"),
        ("Hyundai", "Ioniq 6"),
        ("Unknown", "Car"),
    ]
    
    fetcher = EVDatabaseFetcher()
    
    for make, model in test_cases:
        print(f"\nSearching: {make} {model}")
        result = fetch_ev_consumption(make, model)
        
        if result['found']:
            print(f"  ✓ Found: {result['matched_name']}")
            print(f"    Consumption: {result['consumption_kwh100km']:.1f} kWh/100km")
            print(f"    Source: {result['source']}")
        else:
            print(f"  ✗ {result['error']}")
    
    print(f"\n\nTotal vehicles in database: {len(fetcher.base_database)}")
    print(f"Available makes: {', '.join(fetcher.get_all_makes()[:10])}... and more")

