# EV Consumption Feature - Documentation

## Overview

The PV Consumption Pattern Generator now includes **Electric Vehicle (EV) consumption tracking** based on weekly distance driven and EV efficiency (kWh per 100km). This feature allows you to model realistic EV charging patterns alongside household consumption.

## Key Features

### 1. User-Friendly Parameters
- **Weekly Distance**: Enter how many kilometers you drive per week
- **Consumption per 100km**: EV efficiency (typically 15-25 kWh/100km)
- **Charging Days**: Choose which days of the week to charge
- **Charging Hours**: Define when charging occurs (e.g., overnight)

### 2. Flexible Charging Schedules
- Charge on specific days (e.g., weekdays only, daily, or custom schedule)
- Define charging time windows (e.g., 22:00-06:00 for overnight charging)
- Energy is distributed evenly across charging hours

### 3. Separate Tracking
- Household and EV consumption tracked separately
- Can analyze with or without EV consumption
- Detailed hourly breakdown of household vs EV energy use

## Data Classes

### EVConsumptionProfile

```python
@dataclass
class EVConsumptionProfile:
    enabled: bool = False
    weekly_distance_km: float = 300.0  # Weekly distance driven
    consumption_per_100km: float = 18.0  # kWh per 100km
    
    # Charging schedule (which days to charge)
    # Default: Monday-Friday (True, True, True, True, True, False, False)
    charging_days: List[bool] = [True, True, True, True, True, False, False]
    
    # Charging hours (when charging happens)
    # Default: 22:00-06:00 (overnight charging)
    charging_hours: List[int] = [22, 23, 0, 1, 2, 3, 4, 5, 6]
```

### HouseholdProfile (Updated)

```python
@dataclass
class HouseholdProfile:
    name: str
    annual_consumption_kwh: float
    pattern_type: str = 'working_family'
    seasonal_strength: float = 0.5
    peak_evening_hour: int = 19
    weekend_increase: float = 0.15
    
    # NEW: Optional EV profile
    ev_profile: Optional[EVConsumptionProfile] = None
```

## Usage Examples

### Example 1: Basic EV Profile

```python
from PV_consumption_generator import ConsumptionPatternGenerator, EVConsumptionProfile

generator = ConsumptionPatternGenerator()

# Create EV profile
ev_profile = EVConsumptionProfile(
    enabled=True,
    weekly_distance_km=300,  # 300 km per week
    consumption_per_100km=18.0,  # 18 kWh/100km (typical mid-size EV)
    charging_days=[True, True, True, True, True, False, False],  # Mon-Fri
    charging_hours=[22, 23, 0, 1, 2, 3, 4, 5, 6]  # 22:00-06:00
)

# Create household profile with EV
profile = generator.create_household_profile(
    name="Family with EV",
    annual_consumption_kwh=6000,
    pattern_type='working_family',
    seasonal_strength=0.6,
    peak_hour=19
)
profile.ev_profile = ev_profile

# Generate full year data
year_data = generator.generate_year_consumption(profile)
stats = year_data['statistics']

print(f"Total Annual: {stats['total_annual_kwh']:.0f} kWh")
print(f"  - Household: {stats['household_annual_kwh']:.0f} kWh")
print(f"  - EV: {stats['ev_annual_kwh']:.0f} kWh")
```

### Example 2: Weekend Charging Only

```python
# Charge only on weekends (e.g., for low-mileage users or free weekend rates)
ev_profile = EVConsumptionProfile(
    enabled=True,
    weekly_distance_km=150,  # Lower weekly distance
    consumption_per_100km=16.0,
    charging_days=[False, False, False, False, False, True, True],  # Sat-Sun only
    charging_hours=[10, 11, 12, 13, 14, 15]  # Daytime weekend charging
)
```

### Example 3: Daily Charging (Small Amounts)

```python
# Charge a little every day (e.g., plug-in hybrid or short commute)
ev_profile = EVConsumptionProfile(
    enabled=True,
    weekly_distance_km=200,
    consumption_per_100km=20.0,
    charging_days=[True, True, True, True, True, True, True],  # Every day
    charging_hours=[23, 0, 1, 2, 3]  # Shorter charging window
)
```

### Example 4: Long-Distance Commuter

```python
# High weekly mileage, efficient EV
ev_profile = EVConsumptionProfile(
    enabled=True,
    weekly_distance_km=500,  # 500 km/week (~71 km/day average)
    consumption_per_100km=17.0,  # Efficient EV
    charging_days=[True, True, True, True, True, False, False],
    charging_hours=[22, 23, 0, 1, 2, 3, 4, 5, 6, 7]  # Longer charging window
)
# This would result in:
# - Weekly consumption: 85 kWh
# - Per charging day: 17 kWh
# - Annual: ~4,420 kWh
```

## API Reference

### EVConsumptionProfile Methods

#### `get_daily_ev_consumption() -> float`
Returns average daily EV consumption in kWh (weekly consumption / 7).

#### `get_charging_day_consumption() -> float`
Returns consumption per charging day (weekly consumption / number of charging days).

### ConsumptionPatternGenerator Methods

#### `get_ev_daily_consumption(ev_profile, day_of_week) -> float`
Get EV consumption for a specific day. Returns 0 if not a charging day.

**Parameters:**
- `ev_profile`: EVConsumptionProfile object
- `day_of_week`: 0=Monday, 6=Sunday

#### `get_ev_hourly_consumption(ev_profile, day_of_week, hour) -> float`
Get EV consumption for a specific hour. Returns 0 if not a charging hour.

**Parameters:**
- `ev_profile`: EVConsumptionProfile object
- `day_of_week`: 0=Monday, 6=Sunday
- `hour`: 0-23

#### `get_daily_consumption(profile, month, is_weekday, day_of_week, include_ev=True) -> float`
Get total daily consumption (household + EV if enabled).

**Parameters:**
- `include_ev`: Set to False to get household consumption only

#### `get_hourly_consumption(profile, month, day_of_week, hour, include_ev=True) -> float`
Get total hourly consumption (household + EV if enabled).

**Parameters:**
- `include_ev`: Set to False to get household consumption only

### Year Data Statistics (Updated)

The `generate_year_consumption()` method now returns additional statistics:

```python
{
    'statistics': {
        'total_annual_kwh': float,           # Total household + EV
        'household_annual_kwh': float,       # Household only
        'ev_annual_kwh': float,              # EV only
        'average_daily_kwh': float,          # Total daily average
        'average_daily_household_kwh': float,# Household daily average
        'average_daily_ev_kwh': float,       # EV daily average
        'monthly_totals': dict,              # Total per month
        'monthly_household': dict,           # Household per month
        'monthly_ev': dict,                  # EV per month
        'peak_month': int,
        'low_month': int
    }
}
```

### Hourly Data (Updated)

Each hourly data point now includes:

```python
{
    'date': datetime,
    'hour': int,
    'consumption_kwh': float,    # Total consumption
    'household_kwh': float,       # Household only
    'ev_kwh': float               # EV only
}
```

### Daily Data (Updated)

Each daily data point now includes:

```python
{
    'date': datetime,
    'month': int,
    'day_of_week': int,
    'is_weekday': bool,
    'daily_consumption_kwh': float,      # Total
    'household_consumption_kwh': float,  # Household only
    'ev_consumption_kwh': float,         # EV only
    'hourly_consumption': List[float],   # Total hourly
    'hourly_household': List[float],     # Household hourly
    'hourly_ev': List[float]            # EV hourly
}
```

## Typical EV Parameters

### Weekly Distance by User Type

| User Type | Weekly Distance (km) | Annual Distance (km) |
|-----------|---------------------|---------------------|
| Light user | 100-150 | 5,200-7,800 |
| Average commuter | 200-300 | 10,400-15,600 |
| Heavy commuter | 400-500 | 20,800-26,000 |
| Very high mileage | 600+ | 31,200+ |

### EV Consumption by Vehicle Type

| Vehicle Type | Consumption (kWh/100km) |
|--------------|------------------------|
| Small EV (e.g., VW e-Up!, Renault Zoe) | 14-16 |
| Mid-size EV (e.g., Tesla Model 3, Nissan Leaf) | 16-18 |
| Large EV (e.g., Tesla Model S, Audi e-tron) | 18-22 |
| SUV/Truck (e.g., Tesla Model X, Ford F-150 Lightning) | 22-28 |
| Winter conditions | +20-30% of above values |

### Charging Schedules

#### Overnight Charging (Most Common)
```python
charging_hours=[22, 23, 0, 1, 2, 3, 4, 5, 6]  # 22:00-06:00 (9 hours)
```

#### Late Night Only (Cheaper Rates)
```python
charging_hours=[23, 0, 1, 2, 3, 4, 5]  # 23:00-05:00 (7 hours)
```

#### Daytime Charging (Solar-Optimized)
```python
charging_hours=[10, 11, 12, 13, 14, 15, 16]  # 10:00-16:00 (7 hours)
```

#### Weekend Daytime
```python
charging_days=[False, False, False, False, False, True, True]  # Sat-Sun
charging_hours=[9, 10, 11, 12, 13, 14, 15, 16]  # 09:00-16:00
```

## Calculation Examples

### Example 1: Typical Family EV

**Parameters:**
- Weekly distance: 300 km
- Consumption: 18 kWh/100km
- Charging: Monday-Friday, 22:00-06:00

**Calculations:**
```
Weekly consumption = 300 km × 18 kWh/100km = 54 kWh
Daily average = 54 kWh / 7 days = 7.71 kWh/day
Per charging day = 54 kWh / 5 days = 10.8 kWh
Annual consumption = 54 kWh × 52 weeks = 2,808 kWh
Hourly charging rate = 10.8 kWh / 9 hours = 1.2 kWh/hour
```

### Example 2: Long-Distance Commuter

**Parameters:**
- Weekly distance: 500 km
- Consumption: 20 kWh/100km
- Charging: Monday-Friday, 21:00-07:00

**Calculations:**
```
Weekly consumption = 500 km × 20 kWh/100km = 100 kWh
Daily average = 100 kWh / 7 days = 14.29 kWh/day
Per charging day = 100 kWh / 5 days = 20 kWh
Annual consumption = 100 kWh × 52 weeks = 5,200 kWh
Hourly charging rate = 20 kWh / 10 hours = 2.0 kWh/hour
```

## Integration with PV Calculator

The EV consumption feature integrates seamlessly with the PV system calculator:

1. **Battery Sizing**: EV consumption is included in total energy needs
2. **Self-Sufficiency**: Calculate how much EV charging can be covered by solar
3. **Overnight Charging**: Model battery discharge to power EV at night
4. **Solar-Optimized Charging**: Adjust charging hours to match solar production

## Best Practices

### 1. Accurate Distance Estimation
- Track your actual weekly driving for 2-4 weeks
- Include regular commute, errands, and occasional longer trips
- Add 10-15% buffer for unexpected trips

### 2. Consumption Values
- Check your EV's actual consumption from the dashboard
- Winter consumption is 20-30% higher (heating, cold battery)
- Highway driving typically 15-20% higher than city driving

### 3. Charging Schedule
- **Cost-optimized**: Charge during off-peak hours (typically 22:00-06:00)
- **Solar-optimized**: Charge during peak solar hours (10:00-16:00) if home
- **Battery-friendly**: Avoid charging during household peak hours (18:00-21:00)

### 4. Charging Days
- If you drive daily short distances: Charge every 2-3 days
- If you drive longer distances less frequently: Charge after each use
- Weekend-only charging: Suitable for <100 km/week users

### 5. PV System Planning
- EV adds significant load: 2,000-5,000 kWh/year typical
- Consider larger battery if charging from solar during day
- Overnight charging from grid might be more economical than large battery

## Troubleshooting

### Issue: Annual EV consumption doesn't match expectations

**Solution:**
- Check weekly_distance_km and consumption_per_100km values
- Verify: Annual = (weekly_distance / 100) × consumption × 52
- Remember this is average; actual varies by season, driving style, etc.

### Issue: Charging rate too high/low

**Solution:**
- Adjust number of charging_hours
- Typical home charger: 3-7 kW (3-7 kWh/hour)
- Ensure: (weekly consumption / charging days) / hours ≤ charger power

### Issue: Want different charging per day

**Current limitation:**
- Currently distributes weekly consumption equally across charging days
- For custom patterns, consider adjusting weekly_distance_km accordingly
- Future versions may support day-specific patterns

## Future Enhancements

Planned features:
- Variable charging by day of week
- Smart charging optimization (charge when solar is available)
- Time-of-use electricity rates integration
- Vehicle-to-Grid (V2G) discharge modeling
- Battery degradation over time
- Fast charging sessions (DC charging)

## Example Output

```
Example: Working Family with EV
Household Annual Consumption: 6000 kWh
EV Weekly Distance: 300 km
EV Consumption: 18.0 kWh/100km
EV Daily Average: 7.71 kWh/day
EV Annual: 2808 kWh/year

January Weekday (with EV): 35.21 kWh/day
January Weekend (no EV charging): 25.83 kWh/day

Hourly Pattern (January Monday - with EV charging):
00:00 | 0.753 kWh (H:0.553 EV:0.200) ███ ⚡
01:00 | 0.720 kWh (H:0.520 EV:0.200) ███ ⚡
...
22:00 | 1.651 kWh (H:1.451 EV:0.200) ███████ ⚡
23:00 | 1.251 kWh (H:1.051 EV:0.200) █████ ⚡

Statistics:
Total Annual: 8808 kWh
  - Household: 6000 kWh
  - EV: 2808 kWh
```

## See Also

- [CONSUMPTION_V2_USER_GUIDE.md](CONSUMPTION_V2_USER_GUIDE.md) - Main consumption pattern documentation
- [PV_calculator.py](PV_calculator.py) - Integration with PV system calculator
- [QUICKSTART_SOC_CONTINUITY.md](QUICKSTART_SOC_CONTINUITY.md) - Battery flow modeling

---

**Version**: 2.1  
**Last Updated**: October 2025  
**Author**: PV Calculator Team

