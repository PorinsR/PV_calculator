# EV Consumption Feature

## 🎯 Quick Overview

The PV Consumption Pattern Generator now supports **Electric Vehicle (EV) charging simulation** based on:
- ⚡ **Weekly distance driven** (km)
- 🔋 **EV consumption** (kWh per 100km)
- 📅 **Flexible charging schedules** (which days and hours)

## 📚 Documentation Files

| File | Purpose | Read Time |
|------|---------|-----------|
| **EV_CONSUMPTION_QUICKSTART.md** | Get started in 5 minutes | ⚡ 5 min |
| **EV_CONSUMPTION_FEATURE.md** | Complete API documentation | 📖 15 min |
| **EV_UPDATE_SUMMARY.md** | Change log and migration guide | 📋 10 min |
| **example_ev_usage.py** | Working code examples | 💻 5 min |

## ⚡ Quick Start (30 seconds)

```python
from PV_consumption_generator import ConsumptionPatternGenerator, EVConsumptionProfile

# 1. Create EV profile
ev = EVConsumptionProfile(
    enabled=True,
    weekly_distance_km=300,      # Your weekly driving
    consumption_per_100km=18.0   # Your EV's efficiency
)

# 2. Create household profile
generator = ConsumptionPatternGenerator()
profile = generator.create_household_profile(
    name="My Home",
    annual_consumption_kwh=6000,
    pattern_type='working_family'
)
profile.ev_profile = ev

# 3. Generate data
year_data = generator.generate_year_consumption(profile)
print(f"Total: {year_data['statistics']['total_annual_kwh']:.0f} kWh/year")
print(f"EV: {year_data['statistics']['ev_annual_kwh']:.0f} kWh/year")
```

## 🎓 What You Get

### Automatic Calculations
- ✅ Daily EV consumption from weekly distance
- ✅ Hourly charging distribution
- ✅ Separate household and EV tracking
- ✅ Annual projections with monthly breakdowns

### Flexible Schedules
- 📅 Charge any days of the week
- ⏰ Charge any hours of the day
- 🌙 Default: Overnight charging (22:00-06:00, Mon-Fri)
- ☀️ Alternative: Daytime solar charging (11:00-15:00)

### Detailed Output
```python
statistics = {
    'total_annual_kwh': 8808,        # Household + EV
    'household_annual_kwh': 6000,    # Household only
    'ev_annual_kwh': 2808,           # EV only
    'monthly_household': {...},      # Monthly breakdown
    'monthly_ev': {...},             # Monthly breakdown
    ...
}
```

## 📊 Example Results

### Typical Family (300 km/week, 18 kWh/100km)
- **Weekly EV**: 54 kWh
- **Annual EV**: 2,808 kWh
- **Daily average**: 7.71 kWh
- **Per charging day**: 10.8 kWh

### High-Mileage Commuter (500 km/week, 20 kWh/100km)
- **Weekly EV**: 100 kWh
- **Annual EV**: 5,200 kWh
- **Daily average**: 14.29 kWh
- **Per charging day**: 20 kWh

## 🔧 Key Features

| Feature | Description |
|---------|-------------|
| **User-Friendly** | Input weekly distance and efficiency - no complex math |
| **Realistic** | Charging only during specified days and hours |
| **Flexible** | Any charging schedule (daily, weekdays, custom) |
| **Integrated** | Works with all existing consumption patterns |
| **Detailed** | Hourly, daily, and annual breakdowns |
| **Optional** | EV is completely optional - existing code still works |

## 🚗 Common Use Cases

### 1. Solar System Sizing
Include EV load to size your PV system correctly:
```python
# Without EV: 6,000 kWh/year → 5 kWp system
# With EV: 8,808 kWh/year → 7-8 kWp system
```

### 2. Cost Analysis
Compare grid vs solar charging costs:
```python
# EV cost from grid: 2,808 kWh × €0.30 = €842/year
# EV cost from solar: Mostly free (after system payback)
```

### 3. Charging Optimization
Find the best charging schedule:
```python
# Overnight: Cheap grid rates
# Daytime: Free solar power
# Weekend: Lower household demand
```

## 📈 Typical Values

### Weekly Distance by User Type
- **Light user**: 100-150 km/week
- **Average commuter**: 200-300 km/week
- **Heavy commuter**: 400-500 km/week

### EV Consumption by Vehicle
- **Small EV**: 14-16 kWh/100km (e.g., VW e-Up!)
- **Mid-size EV**: 16-18 kWh/100km (e.g., Tesla Model 3)
- **Large EV**: 20-25 kWh/100km (e.g., Tesla Model X)

## 🎯 Next Steps

### For Quick Start
1. ⚡ Read [EV_CONSUMPTION_QUICKSTART.md](EV_CONSUMPTION_QUICKSTART.md)
2. 💻 Run `python3 example_ev_usage.py`
3. 🚀 Adapt example to your needs

### For Deep Dive
1. 📖 Read [EV_CONSUMPTION_FEATURE.md](EV_CONSUMPTION_FEATURE.md)
2. 🔍 Review API reference
3. 💡 Explore advanced examples

### For Migration
1. 📋 Read [EV_UPDATE_SUMMARY.md](EV_UPDATE_SUMMARY.md)
2. ✅ Check breaking changes (minimal)
3. 🔧 Update your code if needed

## 💡 Pro Tips

### Tip 1: Find Your Weekly Distance
Track your driving for 2-4 weeks and calculate the average.

### Tip 2: Check Your EV's Efficiency
Look at your EV's dashboard or app for actual kWh/100km.

### Tip 3: Winter Adjustment
Add 20-30% to consumption in winter (heating, cold battery).

### Tip 4: Optimize for Solar
If you have PV panels, consider daytime charging (11:00-15:00).

### Tip 5: Battery Sizing
If you want to charge from solar at night, size your battery to cover EV charging.

## ❓ FAQ

**Q: Does this replace the old EV feature in PV_calculator.py?**  
A: No, this adds EV to consumption patterns. The calculator still has its own EV profile.

**Q: Can I use both features together?**  
A: Yes! Use consumption generator for pattern analysis, calculator for financial analysis.

**Q: What if I don't have an EV?**  
A: Just don't add an EV profile. Everything works as before.

**Q: Can I model multiple vehicles?**  
A: Currently one EV per household. For multiple, increase weekly_distance_km accordingly.

**Q: Is this accurate for my specific EV?**  
A: It's a model based on your inputs. Real consumption varies by driving style, weather, etc.

## 🛠️ Support

- 📖 **Documentation**: See files listed above
- 💻 **Examples**: Run `example_ev_usage.py`
- 🐛 **Issues**: Submit on GitHub
- 💬 **Questions**: Check the FAQ in documentation files

## 📊 Statistics

- **Lines of code**: ~150 added
- **New classes**: 1 (EVConsumptionProfile)
- **New methods**: 2 (get_ev_daily_consumption, get_ev_hourly_consumption)
- **Updated methods**: 3 (get_daily_consumption, get_hourly_consumption, generate_year_consumption)
- **Documentation**: 800+ lines
- **Examples**: 4 complete scenarios

## 🎉 Summary

You can now model EV charging in your consumption patterns using simple, user-friendly parameters:
- ✅ Weekly distance driven (km)
- ✅ EV consumption per 100km (kWh/100km)
- ✅ Flexible charging schedule
- ✅ Separate household and EV tracking
- ✅ Complete annual projections

Perfect for solar system planning, cost analysis, and charging optimization!

---

**Ready to start?** → [EV_CONSUMPTION_QUICKSTART.md](EV_CONSUMPTION_QUICKSTART.md)

**Want details?** → [EV_CONSUMPTION_FEATURE.md](EV_CONSUMPTION_FEATURE.md)

**Have questions?** → Check the FAQ in the documentation

