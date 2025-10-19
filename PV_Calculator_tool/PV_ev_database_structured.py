"""
Structured EV Database for Cascading Dropdown Selection
Data from ev-database.org (2024/2025)

Comprehensive database with 33+ manufacturers and 200+ vehicle configurations
"""

from typing import List, Dict, Optional


class StructuredEVDatabase:
    """
    Hierarchical EV database supporting Make → Model → Configuration selection
    
    Database includes:
    - 33 manufacturers
    - 95 models
    - 206+ configurations
    - Real-world consumption data from ev-database.org (2024/2025)
    """
    
    def __init__(self):
        self.database = self._load_database()
    
    def _load_database(self) -> Dict:
        """
        Load comprehensive EV database in hierarchical structure:
        Make → Model → Configuration → specs
        
        Uses the comprehensive database module
        """
        try:
            from PV_ev_database_comprehensive import get_comprehensive_database
            return get_comprehensive_database()
        except ImportError:
            # Fallback to basic database if comprehensive not available
            print("Warning: Comprehensive database not found, using basic database")
            return self._get_basic_database()
    
    def _get_basic_database(self) -> Dict:
        """Basic fallback database (should not normally be used)"""
        return {
            "Tesla": {
                "Model 3": {
                    "RWD (2024, 60 kWh)": {
                        "battery_kwh": 60,
                        "drivetrain": "RWD",
                        "year": 2024,
                        "consumption_kwh100km": 13.6,
                        "source": "ev-database.org 2024"
                    },
                    "Long Range AWD (2024, 75 kWh)": {
                        "battery_kwh": 75,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 14.2,
                        "source": "ev-database.org 2024"
                    },
                    "Performance AWD (2024, 75 kWh)": {
                        "battery_kwh": 75,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 15.2,
                        "source": "ev-database.org 2024"
                    },
                },
                "Model Y": {
                    "RWD (2024, 60 kWh)": {
                        "battery_kwh": 60,
                        "drivetrain": "RWD",
                        "year": 2024,
                        "consumption_kwh100km": 16.1,
                        "source": "ev-database.org 2024"
                    },
                    "Long Range AWD (2024, 75 kWh)": {
                        "battery_kwh": 75,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 16.5,
                        "source": "ev-database.org 2024"
                    },
                    "Performance AWD (2024, 75 kWh)": {
                        "battery_kwh": 75,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 17.0,
                        "source": "ev-database.org 2024"
                    },
                },
                "Model S": {
                    "Long Range AWD (2024, 100 kWh)": {
                        "battery_kwh": 100,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 18.1,
                        "source": "ev-database.org 2024"
                    },
                    "Plaid AWD (2024, 100 kWh)": {
                        "battery_kwh": 100,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 19.5,
                        "source": "ev-database.org 2024"
                    },
                },
                "Model X": {
                    "Long Range AWD (2024, 100 kWh)": {
                        "battery_kwh": 100,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 20.2,
                        "source": "ev-database.org 2024"
                    },
                    "Plaid AWD (2024, 100 kWh)": {
                        "battery_kwh": 100,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 21.0,
                        "source": "ev-database.org 2024"
                    },
                },
            },
            "BMW": {
                "i3": {
                    "RWD (2022, 42 kWh)": {
                        "battery_kwh": 42,
                        "drivetrain": "RWD",
                        "year": 2022,
                        "consumption_kwh100km": 15.8,
                        "source": "ev-database.org"
                    },
                },
                "i4": {
                    "eDrive40 RWD (2024, 81 kWh)": {
                        "battery_kwh": 81,
                        "drivetrain": "RWD",
                        "year": 2024,
                        "consumption_kwh100km": 16.1,
                        "source": "ev-database.org"
                    },
                    "M50 AWD (2024, 81 kWh)": {
                        "battery_kwh": 81,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 18.0,
                        "source": "ev-database.org"
                    },
                },
                "iX": {
                    "xDrive40 AWD (2024, 76 kWh)": {
                        "battery_kwh": 76,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 19.4,
                        "source": "ev-database.org"
                    },
                    "xDrive50 AWD (2024, 106 kWh)": {
                        "battery_kwh": 106,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 21.4,
                        "source": "ev-database.org"
                    },
                },
            },
            "Volkswagen": {
                "ID.3": {
                    "Pro (2024, 58 kWh)": {
                        "battery_kwh": 58,
                        "drivetrain": "RWD",
                        "year": 2024,
                        "consumption_kwh100km": 15.4,
                        "source": "ev-database.org"
                    },
                    "Pro S (2024, 77 kWh)": {
                        "battery_kwh": 77,
                        "drivetrain": "RWD",
                        "year": 2024,
                        "consumption_kwh100km": 15.9,
                        "source": "ev-database.org"
                    },
                },
                "ID.4": {
                    "Pro RWD (2024, 77 kWh)": {
                        "battery_kwh": 77,
                        "drivetrain": "RWD",
                        "year": 2024,
                        "consumption_kwh100km": 16.9,
                        "source": "ev-database.org"
                    },
                    "Pro AWD (2024, 77 kWh)": {
                        "battery_kwh": 77,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 17.5,
                        "source": "ev-database.org"
                    },
                },
                "ID.5": {
                    "Pro AWD (2024, 77 kWh)": {
                        "battery_kwh": 77,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 18.0,
                        "source": "ev-database.org"
                    },
                },
                "ID.Buzz": {
                    "Pro RWD (2024, 77 kWh)": {
                        "battery_kwh": 77,
                        "drivetrain": "RWD",
                        "year": 2024,
                        "consumption_kwh100km": 20.0,
                        "source": "ev-database.org"
                    },
                },
            },
            "Hyundai": {
                "Kona Electric": {
                    "Standard (2024, 48 kWh)": {
                        "battery_kwh": 48,
                        "drivetrain": "FWD",
                        "year": 2024,
                        "consumption_kwh100km": 14.7,
                        "source": "ev-database.org"
                    },
                    "Long Range (2024, 65 kWh)": {
                        "battery_kwh": 65,
                        "drivetrain": "FWD",
                        "year": 2024,
                        "consumption_kwh100km": 15.2,
                        "source": "ev-database.org"
                    },
                },
                "IONIQ 5": {
                    "RWD (2024, 72 kWh)": {
                        "battery_kwh": 72,
                        "drivetrain": "RWD",
                        "year": 2024,
                        "consumption_kwh100km": 16.8,
                        "source": "ev-database.org"
                    },
                    "AWD (2024, 72 kWh)": {
                        "battery_kwh": 72,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 17.5,
                        "source": "ev-database.org"
                    },
                },
                "IONIQ 6": {
                    "RWD (2024, 77 kWh)": {
                        "battery_kwh": 77,
                        "drivetrain": "RWD",
                        "year": 2024,
                        "consumption_kwh100km": 14.9,
                        "source": "ev-database.org"
                    },
                    "AWD (2024, 77 kWh)": {
                        "battery_kwh": 77,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 16.2,
                        "source": "ev-database.org"
                    },
                },
            },
            "Kia": {
                "Niro EV": {
                    "Standard (2024, 64 kWh)": {
                        "battery_kwh": 64,
                        "drivetrain": "FWD",
                        "year": 2024,
                        "consumption_kwh100km": 15.9,
                        "source": "ev-database.org"
                    },
                },
                "EV6": {
                    "RWD (2024, 77 kWh)": {
                        "battery_kwh": 77,
                        "drivetrain": "RWD",
                        "year": 2024,
                        "consumption_kwh100km": 16.5,
                        "source": "ev-database.org"
                    },
                    "AWD (2024, 77 kWh)": {
                        "battery_kwh": 77,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 17.2,
                        "source": "ev-database.org"
                    },
                    "GT AWD (2024, 77 kWh)": {
                        "battery_kwh": 77,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 18.0,
                        "source": "ev-database.org"
                    },
                },
            },
            "Mercedes-Benz": {
                "EQA": {
                    "250 FWD (2024, 66 kWh)": {
                        "battery_kwh": 66,
                        "drivetrain": "FWD",
                        "year": 2024,
                        "consumption_kwh100km": 16.9,
                        "source": "ev-database.org"
                    },
                },
                "EQE": {
                    "350 RWD (2024, 90 kWh)": {
                        "battery_kwh": 90,
                        "drivetrain": "RWD",
                        "year": 2024,
                        "consumption_kwh100km": 17.3,
                        "source": "ev-database.org"
                    },
                },
                "EQS": {
                    "450+ RWD (2024, 108 kWh)": {
                        "battery_kwh": 108,
                        "drivetrain": "RWD",
                        "year": 2024,
                        "consumption_kwh100km": 19.1,
                        "source": "ev-database.org"
                    },
                },
            },
            "Audi": {
                "Q4 e-tron": {
                    "40 RWD (2024, 77 kWh)": {
                        "battery_kwh": 77,
                        "drivetrain": "RWD",
                        "year": 2024,
                        "consumption_kwh100km": 17.0,
                        "source": "ev-database.org"
                    },
                    "50 quattro AWD (2024, 77 kWh)": {
                        "battery_kwh": 77,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 18.2,
                        "source": "ev-database.org"
                    },
                },
                "e-tron GT": {
                    "quattro AWD (2024, 93 kWh)": {
                        "battery_kwh": 93,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 19.6,
                        "source": "ev-database.org"
                    },
                },
            },
            "Polestar": {
                "2": {
                    "Standard Range RWD (2024, 69 kWh)": {
                        "battery_kwh": 69,
                        "drivetrain": "RWD",
                        "year": 2024,
                        "consumption_kwh100km": 16.5,
                        "source": "ev-database.org"
                    },
                    "Long Range AWD (2024, 78 kWh)": {
                        "battery_kwh": 78,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 17.8,
                        "source": "ev-database.org"
                    },
                },
                "3": {
                    "Long Range AWD (2024, 111 kWh)": {
                        "battery_kwh": 111,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 19.0,
                        "source": "ev-database.org"
                    },
                },
            },
            "Nissan": {
                "Leaf": {
                    "Standard (2024, 40 kWh)": {
                        "battery_kwh": 40,
                        "drivetrain": "FWD",
                        "year": 2024,
                        "consumption_kwh100km": 17.0,
                        "source": "ev-database.org"
                    },
                    "e+ (2024, 62 kWh)": {
                        "battery_kwh": 62,
                        "drivetrain": "FWD",
                        "year": 2024,
                        "consumption_kwh100km": 16.5,
                        "source": "ev-database.org"
                    },
                },
                "Ariya": {
                    "63kWh FWD (2024, 63 kWh)": {
                        "battery_kwh": 63,
                        "drivetrain": "FWD",
                        "year": 2024,
                        "consumption_kwh100km": 18.0,
                        "source": "ev-database.org"
                    },
                    "87kWh AWD (2024, 87 kWh)": {
                        "battery_kwh": 87,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 19.5,
                        "source": "ev-database.org"
                    },
                },
            },
            "Renault": {
                "Zoe": {
                    "R135 (2024, 52 kWh)": {
                        "battery_kwh": 52,
                        "drivetrain": "FWD",
                        "year": 2024,
                        "consumption_kwh100km": 17.2,
                        "source": "ev-database.org"
                    },
                },
                "Megane E-Tech": {
                    "EV40 (2024, 40 kWh)": {
                        "battery_kwh": 40,
                        "drivetrain": "FWD",
                        "year": 2024,
                        "consumption_kwh100km": 15.2,
                        "source": "ev-database.org"
                    },
                    "EV60 (2024, 60 kWh)": {
                        "battery_kwh": 60,
                        "drivetrain": "FWD",
                        "year": 2024,
                        "consumption_kwh100km": 15.8,
                        "source": "ev-database.org"
                    },
                },
            },
            "Ford": {
                "Mustang Mach-E": {
                    "RWD (2024, 76 kWh)": {
                        "battery_kwh": 76,
                        "drivetrain": "RWD",
                        "year": 2024,
                        "consumption_kwh100km": 18.5,
                        "source": "ev-database.org"
                    },
                    "AWD (2024, 91 kWh)": {
                        "battery_kwh": 91,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 19.8,
                        "source": "ev-database.org"
                    },
                },
            },
            "Volvo": {
                "XC40 Recharge": {
                    "Twin AWD (2024, 78 kWh)": {
                        "battery_kwh": 78,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 19.3,
                        "source": "ev-database.org"
                    },
                },
                "C40 Recharge": {
                    "Twin AWD (2024, 78 kWh)": {
                        "battery_kwh": 78,
                        "drivetrain": "AWD",
                        "year": 2024,
                        "consumption_kwh100km": 19.0,
                        "source": "ev-database.org"
                    },
                },
            },
        }
    
    def get_makes(self) -> List[str]:
        """Get list of all EV makes"""
        return sorted(self.database.keys())
    
    def get_models(self, make: str) -> List[str]:
        """Get list of models for a specific make"""
        if make in self.database:
            return sorted(self.database[make].keys())
        return []
    
    def get_configurations(self, make: str, model: str) -> List[str]:
        """Get list of configurations for a specific make and model"""
        if make in self.database and model in self.database[make]:
            return sorted(self.database[make][model].keys())
        return []
    
    def get_configuration_data(self, make: str, model: str, configuration: str) -> Optional[Dict]:
        """Get detailed data for a specific configuration"""
        if (make in self.database and 
            model in self.database[make] and 
            configuration in self.database[make][model]):
            return self.database[make][model][configuration]
        return None
    
    def get_consumption(self, make: str, model: str, configuration: str) -> Optional[float]:
        """Get consumption in kWh/100km for a specific configuration"""
        data = self.get_configuration_data(make, model, configuration)
        if data:
            return data.get('consumption_kwh100km')
        return None


if __name__ == "__main__":
    # Test the structured database
    db = StructuredEVDatabase()
    
    print("EV Database Test")
    print("=" * 60)
    
    # Get all makes
    makes = db.get_makes()
    print(f"\nAvailable Makes ({len(makes)}):")
    print(", ".join(makes))
    
    # Get models for Tesla
    models = db.get_models("Tesla")
    print(f"\nTesla Models ({len(models)}):")
    for model in models:
        print(f"  - {model}")
    
    # Get configurations for Tesla Model 3
    configs = db.get_configurations("Tesla", "Model 3")
    print(f"\nTesla Model 3 Configurations ({len(configs)}):")
    for config in configs:
        data = db.get_configuration_data("Tesla", "Model 3", config)
        print(f"  - {config}")
        print(f"    Battery: {data['battery_kwh']} kWh")
        print(f"    Drivetrain: {data['drivetrain']}")
        print(f"    Consumption: {data['consumption_kwh100km']} kWh/100km")
    
    # Get specific consumption
    consumption = db.get_consumption("Tesla", "Model 3", "RWD (2024, 60 kWh)")
    print(f"\nTesla Model 3 RWD consumption: {consumption} kWh/100km")

