# EV Consumption Feature - Quick Start Guide

## 5-Minute Setup

### Step 1: Import the Classes

```python
from PV_consumption_generator import (
    ConsumptionPatternGenerator, 
    HouseholdProfile,
    EVConsumptionProfile
)
```

### Step 2: Create Your EV Profile

```python
# Example: Average commuter
ev_profile = EVConsumptionProfile(
    enabled=True,
    weekly_distance_km=300,        # How much you drive per week
    consumption_per_100km=18.0,    # Your EV's efficiency
    charging_days=[True, True, True, True, True, False, False],  # Mon-Fri
    charging_hours=[22, 23, 0, 1, 2, 3, 4, 5, 6]  # 22:00-06:00
)
```

### Step 3: Create Household Profile with EV

```python
generator = ConsumptionPatternGenerator()

profile = generator.create_household_profile(
    name="My Home with EV",
    annual_consumption_kwh=6000,
    pattern_type='working_family',
    seasonal_strength=0.6,
    peak_hour=19
)

# Add EV to profile
profile.ev_profile = ev_profile
```

### Step 4: Generate Data

```python
# Generate full year
year_data = generator.generate_year_consumption(profile)
stats = year_data['statistics']

# Print summary
print(f"Total Annual: {stats['total_annual_kwh']:.0f} kWh")
print(f"  Household: {stats['household_annual_kwh']:.0f} kWh")
print(f"  EV: {stats['ev_annual_kwh']:.0f} kWh")
```

## Common Scenarios

### Scenario 1: Typical Daily Commuter
```python
ev_profile = EVConsumptionProfile(
    enabled=True,
    weekly_distance_km=250,
    consumption_per_100km=17.0,
    charging_days=[True] * 7,  # Charge every day
    charging_hours=[23, 0, 1, 2, 3, 4, 5]
)
# Result: ~5.95 kWh/day, ~2,184 kWh/year
```

### Scenario 2: Weekend Road Trips
```python
ev_profile = EVConsumptionProfile(
    enabled=True,
    weekly_distance_km=400,
    consumption_per_100km=19.0,
    charging_days=[False, False, False, False, False, True, True],  # Weekends only
    charging_hours=[10, 11, 12, 13, 14, 15]  # Daytime charging
)
# Result: ~38 kWh per weekend day, ~3,952 kWh/year
```

### Scenario 3: Solar-Optimized Charging
```python
ev_profile = EVConsumptionProfile(
    enabled=True,
    weekly_distance_km=300,
    consumption_per_100km=18.0,
    charging_days=[True, True, True, True, True, False, False],
    charging_hours=[11, 12, 13, 14, 15]  # Midday solar peak
)
# Result: ~10.8 kWh per weekday, ~2,808 kWh/year
```

## Quick Reference

### Find Your Weekly Distance
- **Urban commuter**: 150-250 km/week
- **Suburban commuter**: 250-350 km/week
- **Long-distance commuter**: 400-600 km/week
- **Light user**: 50-150 km/week

### Find Your EV Consumption
Check your EV's display or app for average kWh/100km:
- **Small EV**: 14-16 kWh/100km
- **Mid-size EV**: 16-18 kWh/100km
- **Large EV/SUV**: 20-25 kWh/100km
- **Add 20-30% in winter**

### Quick Calculations
```
Annual EV consumption (kWh) = weekly_distance × consumption_per_100km × 52 / 100

Example: 300 km/week × 18 kWh/100km × 52 / 100 = 2,808 kWh/year
```

## Get Specific Values

```python
# Get specific day consumption
monday_kwh = generator.get_daily_consumption(profile, month=1, is_weekday=True, day_of_week=0)

# Get specific hour consumption
hour_19_kwh = generator.get_hourly_consumption(profile, month=1, day_of_week=0, hour=19)

# Get household only (without EV)
household_only = generator.get_daily_consumption(profile, month=1, is_weekday=True, day_of_week=0, include_ev=False)

# Get EV only
ev_only = generator.get_ev_daily_consumption(profile.ev_profile, day_of_week=0)
```

## Troubleshooting

**Q: My annual total is wrong**  
A: Check your weekly distance and consumption values. Formula: `(weekly_km / 100) × kWh_per_100km × 52`

**Q: Charging rate exceeds my home charger**  
A: Increase number of charging hours or reduce charging days to spread the load

**Q: Want different charging per day**  
A: Adjust `weekly_distance_km` to represent the actual weekly driving, then use `charging_days` to specify which days

**Q: How to disable EV temporarily?**  
A: Set `enabled=False` or use `include_ev=False` in methods

## Next Steps

1. ✅ You've created basic EV profile
2. 📊 View [EV_CONSUMPTION_FEATURE.md](EV_CONSUMPTION_FEATURE.md) for detailed documentation
3. 📈 Integrate with PV system calculator for solar optimization
4. 🔋 Model battery storage for overnight EV charging from solar

---

**Need Help?** See [EV_CONSUMPTION_FEATURE.md](EV_CONSUMPTION_FEATURE.md) for complete API documentation and examples.

