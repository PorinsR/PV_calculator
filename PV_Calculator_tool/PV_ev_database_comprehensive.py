"""
Comprehensive EV Database - 30+ Manufacturers, 200+ Vehicles
Data compiled from ev-database.org (2024/2025)

This database includes real-world consumption data for electric vehicles
available in Europe and North America.
"""

from typing import Dict


def get_comprehensive_database() -> Dict:
    """
    Returns comprehensive EV database with 30+ manufacturers and 200+ vehicles
    
    Structure: Make → Model → Configuration → {consumption, battery, drivetrain, year}
    Data source: ev-database.org (2024/2025)
    """
    return {
        # TESLA - Complete lineup
        "Tesla": {
            "Model 3": {
                "RWD (2024, 60 kWh)": {"battery_kwh": 60, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 13.6},
                "Long Range AWD (2024, 75 kWh)": {"battery_kwh": 75, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 14.2},
                "Performance AWD (2024, 75 kWh)": {"battery_kwh": 75, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 15.2},
                "RWD (2023, 60 kWh)": {"battery_kwh": 60, "drivetrain": "RWD", "year": 2023, "consumption_kwh100km": 13.8},
                "Long Range AWD (2023, 75 kWh)": {"battery_kwh": 75, "drivetrain": "AWD", "year": 2023, "consumption_kwh100km": 14.5},
            },
            "Model Y": {
                "RWD (2024, 60 kWh)": {"battery_kwh": 60, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.1},
                "Long Range AWD (2024, 75 kWh)": {"battery_kwh": 75, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 16.5},
                "Performance AWD (2024, 75 kWh)": {"battery_kwh": 75, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 17.0},
                "RWD (2023, 60 kWh)": {"battery_kwh": 60, "drivetrain": "RWD", "year": 2023, "consumption_kwh100km": 16.3},
            },
            "Model S": {
                "Long Range AWD (2024, 100 kWh)": {"battery_kwh": 100, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.1},
                "Plaid AWD (2024, 100 kWh)": {"battery_kwh": 100, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 19.5},
            },
            "Model X": {
                "Long Range AWD (2024, 100 kWh)": {"battery_kwh": 100, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 20.2},
                "Plaid AWD (2024, 100 kWh)": {"battery_kwh": 100, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 21.0},
            },
        },
        
        # BMW - Full i-series
        "BMW": {
            "i3": {
                "120Ah RWD (2022, 42 kWh)": {"battery_kwh": 42, "drivetrain": "RWD", "year": 2022, "consumption_kwh100km": 15.8},
                "120Ah RWD (2021, 42 kWh)": {"battery_kwh": 42, "drivetrain": "RWD", "year": 2021, "consumption_kwh100km": 16.0},
            },
            "i4": {
                "eDrive35 RWD (2024, 70 kWh)": {"battery_kwh": 70, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 15.5},
                "eDrive40 RWD (2024, 81 kWh)": {"battery_kwh": 81, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.1},
                "M50 AWD (2024, 81 kWh)": {"battery_kwh": 81, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.0},
                "eDrive40 RWD (2023, 81 kWh)": {"battery_kwh": 81, "drivetrain": "RWD", "year": 2023, "consumption_kwh100km": 16.3},
            },
            "i5": {
                "eDrive40 RWD (2024, 81 kWh)": {"battery_kwh": 81, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.7},
                "M60 AWD (2024, 81 kWh)": {"battery_kwh": 81, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.5},
            },
            "i7": {
                "xDrive60 AWD (2024, 102 kWh)": {"battery_kwh": 102, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 19.6},
                "M70 AWD (2024, 102 kWh)": {"battery_kwh": 102, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 20.8},
            },
            "iX": {
                "xDrive40 AWD (2024, 76 kWh)": {"battery_kwh": 76, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 19.4},
                "xDrive50 AWD (2024, 106 kWh)": {"battery_kwh": 106, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 21.4},
                "M60 AWD (2024, 106 kWh)": {"battery_kwh": 106, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 22.5},
            },
            "iX1": {
                "xDrive30 AWD (2024, 64 kWh)": {"battery_kwh": 64, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 17.3},
            },
            "iX3": {
                "RWD (2024, 80 kWh)": {"battery_kwh": 80, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 17.8},
            },
        },
        
        # VOLKSWAGEN - ID series
        "Volkswagen": {
            "ID.3": {
                "Pure (2024, 58 kWh)": {"battery_kwh": 58, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 14.9},
                "Pro (2024, 58 kWh)": {"battery_kwh": 58, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 15.4},
                "Pro S (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 15.9},
                "GTX (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 16.5},
            },
            "ID.4": {
                "Pure RWD (2024, 52 kWh)": {"battery_kwh": 52, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.2},
                "Pro RWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.9},
                "Pro AWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 17.5},
                "GTX AWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.0},
            },
            "ID.5": {
                "Pro RWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 17.3},
                "Pro AWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.0},
                "GTX AWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.5},
            },
            "ID.7": {
                "Pro RWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.5},
                "GTX AWD (2024, 86 kWh)": {"battery_kwh": 86, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 17.8},
            },
            "ID.Buzz": {
                "Pro RWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 20.0},
                "Pro LWB (2024, 86 kWh)": {"battery_kwh": 86, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 20.5},
            },
        },
        
        # HYUNDAI - IONIQ lineup
        "Hyundai": {
            "Kona Electric": {
                "Standard Range (2024, 48 kWh)": {"battery_kwh": 48, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 14.7},
                "Long Range (2024, 65 kWh)": {"battery_kwh": 65, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 15.2},
                "Standard Range (2023, 39 kWh)": {"battery_kwh": 39, "drivetrain": "FWD", "year": 2023, "consumption_kwh100km": 14.5},
            },
            "IONIQ 5": {
                "Standard Range RWD (2024, 58 kWh)": {"battery_kwh": 58, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.2},
                "Long Range RWD (2024, 72 kWh)": {"battery_kwh": 72, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.8},
                "Long Range AWD (2024, 72 kWh)": {"battery_kwh": 72, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 17.5},
                "N AWD (2024, 84 kWh)": {"battery_kwh": 84, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 19.0},
            },
            "IONIQ 6": {
                "Long Range RWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 14.3},
                "Long Range AWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 15.8},
                "Standard Range RWD (2024, 53 kWh)": {"battery_kwh": 53, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 14.0},
            },
            "Inster": {
                "Standard (2025, 42 kWh)": {"battery_kwh": 42, "drivetrain": "FWD", "year": 2025, "consumption_kwh100km": 15.3},
                "Long Range (2025, 49 kWh)": {"battery_kwh": 49, "drivetrain": "FWD", "year": 2025, "consumption_kwh100km": 15.8},
            },
        },
        
        # KIA - EV lineup
        "Kia": {
            "Niro EV": {
                "Standard (2024, 64 kWh)": {"battery_kwh": 64, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 15.9},
                "Long Range (2023, 64 kWh)": {"battery_kwh": 64, "drivetrain": "FWD", "year": 2023, "consumption_kwh100km": 16.2},
            },
            "EV6": {
                "Standard Range RWD (2024, 58 kWh)": {"battery_kwh": 58, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.0},
                "Long Range RWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.5},
                "Long Range AWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 17.2},
                "GT AWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.0},
            },
            "EV9": {
                "Standard Range AWD (2024, 76 kWh)": {"battery_kwh": 76, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 22.5},
                "Long Range AWD (2024, 99 kWh)": {"battery_kwh": 99, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 23.5},
                "GT-Line AWD (2024, 99 kWh)": {"battery_kwh": 99, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 24.0},
            },
        },
        
        # MERCEDES-BENZ - EQ lineup
        "Mercedes-Benz": {
            "EQA": {
                "250 FWD (2024, 66 kWh)": {"battery_kwh": 66, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 16.9},
                "250+ FWD (2024, 70 kWh)": {"battery_kwh": 70, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 17.2},
                "300 AWD (2024, 70 kWh)": {"battery_kwh": 70, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.0},
            },
            "EQB": {
                "250+ FWD (2024, 70 kWh)": {"battery_kwh": 70, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 18.5},
                "300 AWD (2024, 70 kWh)": {"battery_kwh": 70, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 19.2},
            },
            "EQE": {
                "300 RWD (2024, 90 kWh)": {"battery_kwh": 90, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.8},
                "350 RWD (2024, 90 kWh)": {"battery_kwh": 90, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 17.3},
                "350+ AWD (2024, 96 kWh)": {"battery_kwh": 96, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.2},
                "500 AWD (2024, 96 kWh)": {"battery_kwh": 96, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 19.0},
            },
            "EQE SUV": {
                "350 AWD (2024, 96 kWh)": {"battery_kwh": 96, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 19.5},
                "500 AWD (2024, 96 kWh)": {"battery_kwh": 96, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 20.2},
            },
            "EQS": {
                "450+ RWD (2024, 108 kWh)": {"battery_kwh": 108, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 17.5},
                "500 AWD (2024, 108 kWh)": {"battery_kwh": 108, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.8},
                "580 AWD (2024, 118 kWh)": {"battery_kwh": 118, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 19.8},
            },
            "EQS SUV": {
                "450+ AWD (2024, 118 kWh)": {"battery_kwh": 118, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 20.5},
                "580 AWD (2024, 118 kWh)": {"battery_kwh": 118, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 21.8},
            },
            "EQV": {
                "300 Long FWD (2024, 90 kWh)": {"battery_kwh": 90, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 26.3},
            },
        },
        
        # AUDI - e-tron lineup
        "Audi": {
            "Q4 e-tron": {
                "35 RWD (2024, 52 kWh)": {"battery_kwh": 52, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.5},
                "40 RWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 17.0},
                "45 quattro AWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.2},
                "50 quattro AWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.8},
            },
            "Q4 Sportback e-tron": {
                "40 RWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.7},
                "50 quattro AWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.5},
            },
            "Q6 e-tron": {
                "RWD (2024, 83 kWh)": {"battery_kwh": 83, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 17.5},
                "quattro AWD (2024, 100 kWh)": {"battery_kwh": 100, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.8},
                "SQ6 quattro AWD (2024, 100 kWh)": {"battery_kwh": 100, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 19.5},
            },
            "Q8 e-tron": {
                "50 quattro AWD (2024, 95 kWh)": {"battery_kwh": 95, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 21.5},
                "55 quattro AWD (2024, 106 kWh)": {"battery_kwh": 106, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 22.4},
                "SQ8 quattro AWD (2024, 106 kWh)": {"battery_kwh": 106, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 23.8},
            },
            "e-tron GT": {
                "quattro AWD (2024, 93 kWh)": {"battery_kwh": 93, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 19.2},
                "RS quattro AWD (2024, 93 kWh)": {"battery_kwh": 93, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 20.5},
            },
        },
        
        # POLESTAR
        "Polestar": {
            "2": {
                "Standard Range RWD (2024, 69 kWh)": {"battery_kwh": 69, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.1},
                "Long Range RWD (2024, 78 kWh)": {"battery_kwh": 78, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.5},
                "Long Range AWD (2024, 78 kWh)": {"battery_kwh": 78, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 17.8},
            },
            "3": {
                "Long Range RWD (2024, 78 kWh)": {"battery_kwh": 78, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 17.5},
                "Long Range AWD (2024, 111 kWh)": {"battery_kwh": 111, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 19.0},
            },
            "4": {
                "Long Range AWD (2025, 100 kWh)": {"battery_kwh": 100, "drivetrain": "AWD", "year": 2025, "consumption_kwh100km": 18.5},
            },
        },
        
        # NISSAN
        "Nissan": {
            "Leaf": {
                "Standard (2024, 40 kWh)": {"battery_kwh": 40, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 17.0},
                "e+ (2024, 62 kWh)": {"battery_kwh": 62, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 16.5},
                "Standard (2023, 40 kWh)": {"battery_kwh": 40, "drivetrain": "FWD", "year": 2023, "consumption_kwh100km": 17.1},
            },
            "Ariya": {
                "63kWh FWD (2024, 63 kWh)": {"battery_kwh": 63, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 17.8},
                "87kWh FWD (2024, 87 kWh)": {"battery_kwh": 87, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 18.0},
                "87kWh AWD (2024, 87 kWh)": {"battery_kwh": 87, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 19.5},
                "Nismo AWD (2024, 91 kWh)": {"battery_kwh": 91, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 20.0},
            },
        },
        
        # RENAULT
        "Renault": {
            "Zoe": {
                "R110 (2024, 52 kWh)": {"battery_kwh": 52, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 16.8},
                "R135 (2024, 52 kWh)": {"battery_kwh": 52, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 17.2},
            },
            "Megane E-Tech": {
                "EV40 (2024, 40 kWh)": {"battery_kwh": 40, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 15.2},
                "EV60 (2024, 60 kWh)": {"battery_kwh": 60, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 15.8},
                "EV60 Performance (2024, 60 kWh)": {"battery_kwh": 60, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 16.5},
            },
            "Scenic E-Tech": {
                "Comfort Range (2024, 60 kWh)": {"battery_kwh": 60, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 16.5},
                "Long Range (2024, 87 kWh)": {"battery_kwh": 87, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 17.2},
            },
            "5 E-Tech": {
                "Comfort Range (2025, 52 kWh)": {"battery_kwh": 52, "drivetrain": "FWD", "year": 2025, "consumption_kwh100km": 14.9},
                "Long Range (2025, 87 kWh)": {"battery_kwh": 87, "drivetrain": "FWD", "year": 2025, "consumption_kwh100km": 15.5},
            },
        },
        
        # FORD
        "Ford": {
            "Mustang Mach-E": {
                "Standard Range RWD (2024, 70 kWh)": {"battery_kwh": 70, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 17.8},
                "Long Range RWD (2024, 91 kWh)": {"battery_kwh": 91, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 18.5},
                "Long Range AWD (2024, 91 kWh)": {"battery_kwh": 91, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 19.8},
                "GT AWD (2024, 91 kWh)": {"battery_kwh": 91, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 21.0},
            },
            "Explorer": {
                "Standard Range RWD (2024, 52 kWh)": {"battery_kwh": 52, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.8},
                "Extended Range RWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 17.5},
                "Extended Range AWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.5},
            },
        },
        
        # VOLVO
        "Volvo": {
            "XC40 Recharge": {
                "Single Motor RWD (2024, 69 kWh)": {"battery_kwh": 69, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 18.0},
                "Twin Motor AWD (2024, 78 kWh)": {"battery_kwh": 78, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 19.3},
            },
            "C40 Recharge": {
                "Single Motor RWD (2024, 69 kWh)": {"battery_kwh": 69, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 17.5},
                "Twin Motor AWD (2024, 78 kWh)": {"battery_kwh": 78, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 19.0},
            },
            "EX30": {
                "Single Motor RWD (2024, 51 kWh)": {"battery_kwh": 51, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.2},
                "Single Motor Extended Range (2024, 69 kWh)": {"battery_kwh": 69, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.8},
                "Twin Motor AWD (2024, 69 kWh)": {"battery_kwh": 69, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 17.5},
            },
            "EX90": {
                "Twin Motor AWD (2025, 111 kWh)": {"battery_kwh": 111, "drivetrain": "AWD", "year": 2025, "consumption_kwh100km": 22.0},
            },
        },
        
        # PORSCHE
        "Porsche": {
            "Taycan": {
                "RWD (2024, 89 kWh)": {"battery_kwh": 89, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 19.6},
                "4S AWD (2024, 89 kWh)": {"battery_kwh": 89, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 20.8},
                "Turbo AWD (2024, 105 kWh)": {"battery_kwh": 105, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 22.0},
                "Turbo S AWD (2024, 105 kWh)": {"battery_kwh": 105, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 23.4},
            },
            "Taycan Cross Turismo": {
                "4S AWD (2024, 89 kWh)": {"battery_kwh": 89, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 21.5},
                "Turbo AWD (2024, 105 kWh)": {"battery_kwh": 105, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 22.8},
            },
            "Macan Electric": {
                "4 AWD (2025, 100 kWh)": {"battery_kwh": 100, "drivetrain": "AWD", "year": 2025, "consumption_kwh100km": 19.8},
                "Turbo AWD (2025, 100 kWh)": {"battery_kwh": 100, "drivetrain": "AWD", "year": 2025, "consumption_kwh100km": 21.5},
            },
        },
        
        # MINI
        "Mini": {
            "Cooper E": {
                "Standard (2024, 40 kWh)": {"battery_kwh": 40, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 14.6},
                "Long Range (2024, 54 kWh)": {"battery_kwh": 54, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 15.2},
            },
            "Cooper SE": {
                "Standard (2023, 32 kWh)": {"battery_kwh": 32, "drivetrain": "FWD", "year": 2023, "consumption_kwh100km": 14.9},
            },
            "Countryman E": {
                "ALL4 AWD (2025, 66 kWh)": {"battery_kwh": 66, "drivetrain": "AWD", "year": 2025, "consumption_kwh100km": 17.5},
            },
        },
        
        # FIAT
        "Fiat": {
            "500e": {
                "Hatchback (2024, 42 kWh)": {"battery_kwh": 42, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 13.0},
                "Cabrio (2024, 42 kWh)": {"battery_kwh": 42, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 13.5},
                "3+1 (2024, 42 kWh)": {"battery_kwh": 42, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 13.2},
            },
            "600e": {
                "Standard (2024, 54 kWh)": {"battery_kwh": 54, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 15.5},
            },
        },
        
        # SKODA
        "Skoda": {
            "Enyaq": {
                "60 RWD (2024, 62 kWh)": {"battery_kwh": 62, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.2},
                "80 RWD (2024, 82 kWh)": {"battery_kwh": 82, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.7},
                "80x AWD (2024, 82 kWh)": {"battery_kwh": 82, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 17.8},
                "RS AWD (2024, 82 kWh)": {"battery_kwh": 82, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.5},
            },
            "Enyaq Coupe": {
                "80 RWD (2024, 82 kWh)": {"battery_kwh": 82, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.3},
                "RS AWD (2024, 82 kWh)": {"battery_kwh": 82, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.2},
            },
            "Elroq": {
                "50 RWD (2025, 55 kWh)": {"battery_kwh": 55, "drivetrain": "RWD", "year": 2025, "consumption_kwh100km": 15.8},
                "85 RWD (2025, 82 kWh)": {"battery_kwh": 82, "drivetrain": "RWD", "year": 2025, "consumption_kwh100km": 16.5},
            },
        },
        
        # CUPRA
        "Cupra": {
            "Born": {
                "45 RWD (2024, 58 kWh)": {"battery_kwh": 58, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 15.6},
                "58 RWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.2},
                "e-Boost RWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.8},
            },
            "Tavascan": {
                "Endurance RWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.8},
                "VZ AWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.0},
            },
        },
        
        # MG
        "MG": {
            "4": {
                "Standard Range (2024, 51 kWh)": {"battery_kwh": 51, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 15.5},
                "Long Range (2024, 64 kWh)": {"battery_kwh": 64, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.0},
            },
            "5": {
                "Standard Range RWD (2024, 61 kWh)": {"battery_kwh": 61, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.8},
                "Long Range AWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 17.8},
            },
            "ZS EV": {
                "Standard (2024, 72 kWh)": {"battery_kwh": 72, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 17.3},
                "Long Range (2023, 72 kWh)": {"battery_kwh": 72, "drivetrain": "FWD", "year": 2023, "consumption_kwh100km": 17.5},
            },
        },
        
        # BYD
        "BYD": {
            "Atto 3": {
                "Standard (2024, 60 kWh)": {"battery_kwh": 60, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 16.0},
            },
            "Dolphin": {
                "Active (2024, 45 kWh)": {"battery_kwh": 45, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 14.2},
                "Boost (2024, 60 kWh)": {"battery_kwh": 60, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 14.8},
            },
            "Seal": {
                "RWD (2024, 82 kWh)": {"battery_kwh": 82, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.5},
                "AWD (2024, 82 kWh)": {"battery_kwh": 82, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 17.5},
            },
            "Tang": {
                "AWD (2024, 108 kWh)": {"battery_kwh": 108, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 22.5},
            },
        },
        
        # PEUGEOT
        "Peugeot": {
            "e-208": {
                "Standard (2024, 50 kWh)": {"battery_kwh": 50, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 15.2},
                "GT (2024, 50 kWh)": {"battery_kwh": 50, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 15.5},
            },
            "e-2008": {
                "Standard (2024, 50 kWh)": {"battery_kwh": 50, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 16.5},
                "GT (2024, 54 kWh)": {"battery_kwh": 54, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 17.0},
            },
            "e-3008": {
                "Long Range (2024, 73 kWh)": {"battery_kwh": 73, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 17.5},
                "Dual Motor AWD (2024, 73 kWh)": {"battery_kwh": 73, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.5},
            },
        },
        
        # OPEL
        "Opel": {
            "Corsa-e": {
                "Standard (2024, 50 kWh)": {"battery_kwh": 50, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 15.2},
            },
            "Mokka-e": {
                "Standard (2024, 50 kWh)": {"battery_kwh": 50, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 16.5},
            },
            "Astra-e": {
                "Standard (2024, 54 kWh)": {"battery_kwh": 54, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 15.8},
            },
        },
        
        # CITROEN
        "Citroen": {
            "e-C4": {
                "Standard (2024, 50 kWh)": {"battery_kwh": 50, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 16.3},
            },
            "e-Berlingo": {
                "Standard (2024, 50 kWh)": {"battery_kwh": 50, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 18.5},
            },
            "e-C3": {
                "Standard (2024, 44 kWh)": {"battery_kwh": 44, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 14.8},
            },
        },
        
        # DS AUTOMOBILES
        "DS Automobiles": {
            "3 E-Tense": {
                "Standard (2024, 50 kWh)": {"battery_kwh": 50, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 15.5},
            },
            "4 E-Tense": {
                "Standard (2024, 50 kWh)": {"battery_kwh": 50, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 16.5},
            },
        },
        
        # JAGUAR
        "Jaguar": {
            "I-PACE": {
                "EV400 AWD (2024, 90 kWh)": {"battery_kwh": 90, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 22.0},
                "EV400 AWD (2023, 90 kWh)": {"battery_kwh": 90, "drivetrain": "AWD", "year": 2023, "consumption_kwh100km": 22.2},
            },
        },
        
        # LEXUS
        "Lexus": {
            "RZ": {
                "450e AWD (2024, 71 kWh)": {"battery_kwh": 71, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.0},
            },
        },
        
        # MAZDA
        "Mazda": {
            "MX-30": {
                "e-Skyactiv (2024, 35 kWh)": {"battery_kwh": 35, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 16.5},
                "R-EV (2024, 17.8 kWh)": {"battery_kwh": 17.8, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 15.0},
            },
        },
        
        # HONDA
        "Honda": {
            "e": {
                "Advance (2023, 35 kWh)": {"battery_kwh": 35, "drivetrain": "RWD", "year": 2023, "consumption_kwh100km": 17.2},
            },
            "e:Ny1": {
                "Standard (2024, 68 kWh)": {"battery_kwh": 68, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 17.5},
            },
        },
        
        # SUBARU
        "Subaru": {
            "Solterra": {
                "AWD (2024, 71 kWh)": {"battery_kwh": 71, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.2},
            },
        },
        
        # TOYOTA
        "Toyota": {
            "bZ4X": {
                "FWD (2024, 71 kWh)": {"battery_kwh": 71, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 17.0},
                "AWD (2024, 71 kWh)": {"battery_kwh": 71, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.0},
            },
        },
        
        # GENESIS
        "Genesis": {
            "GV60": {
                "Sport AWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 18.5},
                "Sport Plus AWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 19.2},
            },
            "GV70 Electrified": {
                "AWD (2024, 77 kWh)": {"battery_kwh": 77, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 19.8},
            },
            "G80 Electrified": {
                "AWD (2024, 87 kWh)": {"battery_kwh": 87, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 20.5},
            },
        },
        
        # SMART
        "Smart": {
            "#1": {
                "Pro+ RWD (2024, 66 kWh)": {"battery_kwh": 66, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 16.5},
                "Brabus AWD (2024, 66 kWh)": {"battery_kwh": 66, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 17.8},
            },
            "#3": {
                "Pro+ RWD (2024, 66 kWh)": {"battery_kwh": 66, "drivetrain": "RWD", "year": 2024, "consumption_kwh100km": 17.0},
            },
        },
        
        # ALFA ROMEO
        "Alfa Romeo": {
            "Tonale PHEV": {
                "Q4 AWD (2024, 15.5 kWh)": {"battery_kwh": 15.5, "drivetrain": "AWD", "year": 2024, "consumption_kwh100km": 12.5},
            },
        },
        
        # JEEP
        "Jeep": {
            "Avenger": {
                "Electric (2024, 54 kWh)": {"battery_kwh": 54, "drivetrain": "FWD", "year": 2024, "consumption_kwh100km": 16.0},
            },
        },
    }


if __name__ == "__main__":
    # Test the database
    db = get_comprehensive_database()
    
    manufacturers = sorted(db.keys())
    total_models = sum(len(models) for models in db.values())
    total_configs = sum(
        len(configs) 
        for models in db.values() 
        for configs in models.values()
    )
    
    print("=" * 70)
    print("COMPREHENSIVE EV DATABASE")
    print("=" * 70)
    print(f"\n📊 Database Statistics:")
    print(f"   Manufacturers: {len(manufacturers)}")
    print(f"   Models: {total_models}")
    print(f"   Configurations: {total_configs}")
    
    print(f"\n🏭 Manufacturers ({len(manufacturers)}):")
    for i, make in enumerate(manufacturers, 1):
        model_count = len(db[make])
        config_count = sum(len(configs) for configs in db[make].values())
        print(f"   {i:2}. {make:20} - {model_count:2} models, {config_count:3} configurations")
    
    print(f"\n✅ Database Status: READY")
    print(f"   Source: ev-database.org (2024/2025)")
    print(f"   All consumption values in kWh/100km")
    print("=" * 70)


