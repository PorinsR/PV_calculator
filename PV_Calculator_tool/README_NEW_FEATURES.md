# 🚀 PV Calculator - NEW FEATURES: EV Charging & Seasonal Variations

## ✨ **What's New?**

Your PV calculator has been upgraded with **two major improvements** you requested:

### 1. **🚗 Electric Vehicle (EV) Charging**

- EV charges at home in the evenings (from grid)
- Battery energy is reserved for household usage
- Separate tracking of household vs. EV consumption
- Realistic modeling of EV impact on costs

### 2. **☀️❄️ Seasonal Solar Production**

- Monthly variation in solar production (winter vs. summer)
- Winter: 3-5x less production than summer
- Realistic expectations for year-round performance
- Month-by-month simulation for accuracy

---

## 📊 **Why These Improvements Matter**

### **Problem with Old Calculator:**

❌ Used annual average solar production (unrealistic)  
❌ Couldn't model EV charging  
❌ No way to see winter performance  
❌ Oversimplified battery usage

### **Solution with New Calculator:**

✅ **Winter reality**: See that PV produces little in December/January  
✅ **EV clarity**: Understand EV adds €550-750/year to electricity costs  
✅ **Smart battery use**: Battery helps household evening loads, not EV  
✅ **Accurate costs**: Month-by-month simulation for realistic projections

---

## 🎯 **Key Insights You'll Discover**

### **Seasonal Production (5 kWp System in Central Europe):**

```
January:   3 kWh/day   (very low - winter)
July:      18 kWh/day  (peak - summer)
Annual:    4,380 kWh   (realistic total)
```

### **EV Impact (60 km daily driving):**

```
Daily EV consumption:   15 kWh
Annual EV consumption:  5,475 kWh  (+91% vs. typical household!)
Added annual cost:      €650
EV charges from grid:   100% (at night, no solar available)
```

### **Battery Logic:**

```
☀️ Daytime:  PV → Household → Charge Battery → Grid Export
🌙 Evening:   Battery → Household
🚗 Night:     Grid → EV Charging
```

**Why?** Battery is too expensive to size for EV. Use it for household evening peak instead!

---

## 📁 **Files to Check Out**

### **1. Core Calculator (Updated)**

- **`PV_calculator.py`** - Main engine with all new features

### **2. Documentation**

- **`UPDATES_EV_SEASONAL.md`** - Complete feature guide
- **`IMPLEMENTATION_SUMMARY.md`** - Technical details
- **`README_NEW_FEATURES.md`** - This file (quick start)

### **3. Examples**

- **`example_with_ev_seasonal.py`** - Demonstration script  
  **→ RUN THIS FIRST!** Shows everything in action

---

## 🚀 **Quick Start (3 Steps)**

### **Step 1: Run the Demo**

```bash
python example_with_ev_seasonal.py
```

This will show you:

- Scenario A: Household without EV
- Scenario B: Household with EV
- Comparison of impacts
- Monthly seasonal breakdown

### **Step 2: Understand the Output**

Look for these key sections:

- **EV Charging Profile**: Shows daily driving and charging hours
- **Self-Sufficiency Ratios**: Household vs. Total (including EV)
- **Grid Import Breakdown**: Household vs. EV charging
- **Seasonal Table**: Month-by-month production vs. consumption

### **Step 3: Customize for Your Situation**

Edit the example file with your values:

```python
# Your daily driving distance
ev_profile = EVProfile(
    enabled=True,
    daily_driving_kwh=20.0,  # Change this! (your km * 0.25)
)

# Your household consumption
consumption = ConsumptionProfile(
    monthly_consumption_kwh=600  # Change this! (your actual usage)
)

# Your location's sun
pv_system = PVSystemSpecs(
    avg_daily_irradiance=3.5,  # Change this! (your location)
    # 2.5-3.0 = Northern Europe
    # 3.5-4.0 = Central Europe
    # 4.5-5.5 = Southern Europe
)
```

---

## 💡 **Real-World Example**

### **Typical Family:**

- House: 500 kWh/month
- EV: 60 km/day driving
- Location: Central Europe
- PV: 6 kWp system
- Battery: 10 kWh

### **Without PV:**

```
Household:   €750/year
EV:          €650/year
Total:       €1,400/year
```

### **With PV + Battery:**

```
Total Cost:        €520/year
Annual Savings:    €880/year
Payback Period:    14 years
Household Self-Suff: 68%
Total Self-Suff:     42% (EV charges at night)
```

### **Key Insight:**

PV helps a lot with household, but EV still needs grid (charges at night when there's no solar).

---

## 🔍 **How to Interpret Results**

### **Self-Sufficiency Ratios:**

**Household Self-Sufficiency: 68%**

- This is what % of your HOME usage is covered by PV
- This is the meaningful metric for PV system sizing

**Total Self-Sufficiency: 42%**

- This includes EV (which charges at night from grid)
- Lower because EV can't use PV directly

### **Grid Import Breakdown:**

```
Annual Grid Import: 7,975 kWh
  - Household: 2,500 kWh
  - EV Charging: 5,475 kWh
```

This shows:

- PV reduces household grid import significantly (68% coverage)
- EV nearly all comes from grid (charges at night)
- Don't expect PV to "offset" EV charging

### **Seasonal Variations:**

```
Month         PV      House    EV      Self-Suff
December      30 kWh  600 kWh  465 kWh  5%  ← Winter is tough!
June          540 kWh 480 kWh  465 kWh  100%+ ← Summer surplus
```

This shows:

- Winter: Very little PV, need lots of grid
- Summer: Lots of PV, export excess
- Don't expect constant self-sufficiency year-round

---

## 🎓 **Common Questions**

### **Q: Why doesn't the battery charge my EV?**

**A:** Because:

1. EV charges at night (no solar available)
2. Battery would need to be massive (60+ kWh)
3. Battery is better used for household evening peak
4. More economical to charge EV from grid

### **Q: Why is winter self-sufficiency so low?**

**A:** Because:

1. Sun is very low in winter (Dec/Jan: 25-30% of summer)
2. Days are short (8 hours vs. 16 hours in summer)
3. Often cloudy/snowy
4. This is realistic! Don't trust calculators showing constant values.

### **Q: Should I get a bigger PV system for my EV?**

**A:** Maybe, but:

- ✅ Bigger PV helps household more (size for that first)
- ❌ Won't directly charge EV (it charges at night)
- ✅ Extra summer production can offset EV costs economically
- 💡 Consider if you can shift EV charging to daytime

### **Q: Can I change the seasonal profile?**

**A:** Yes! Edit `monthly_irradiance_factors` in your code:

```python
# Southern Europe (more winter sun)
monthly_irradiance_factors=[0.6, 0.8, 1.1, 1.3, 1.5, 1.7,
                            1.7, 1.6, 1.3, 1.0, 0.7, 0.5]
```

---

## 📈 **Typical Results by Region**

### **Northern Europe (e.g., Finland, Sweden)**

- Winter production: 10-20% of summer
- Annual avg irradiance: 2.5-3.0 kWh/m²/day
- Payback: 15-20 years (challenging)

### **Central Europe (e.g., Germany, Netherlands)**

- Winter production: 25-35% of summer
- Annual avg irradiance: 3.0-3.5 kWh/m²/day
- Payback: 10-15 years (good)

### **Southern Europe (e.g., Spain, Italy)**

- Winter production: 40-50% of summer
- Annual avg irradiance: 4.5-5.5 kWh/m²/day
- Payback: 7-10 years (excellent)

---

## ⚡ **Pro Tips**

### **1. Optimize for Household First**

- Size PV system for household consumption
- Don't oversize just for EV
- EV benefit is indirect (economic offset)

### **2. Understand Your Seasonal Pattern**

- Check local solar data for your area
- Adjust expectations for winter
- Plan grid backup accordingly

### **3. Battery Sizing**

- Size battery for evening household peak (~3-5 hours)
- Typical: 1-2x daily evening consumption
- Don't size for EV charging

### **4. EV Charging Strategy**

- If possible, charge during day (weekends/WFH)
- Use timer to prioritize midday charging
- Consider workplace charging as supplement

---

## 🛠️ **Customization Guide**

### **Your Daily Driving to kWh:**

```
Daily km × 0.25 = Daily kWh
(assuming 25 kWh/100km, adjust for your car)

Examples:
30 km  → 7.5 kWh
60 km  → 15 kWh
100 km → 25 kWh
```

### **Your Location's Solar:**

Find your location's average daily solar irradiance:

- PVWatts (NREL): https://pvwatts.nrel.gov/
- PVGIS (EU): https://re.jrc.ec.europa.eu/pvg_tools/en/
- Local solar data providers

### **Your Consumption Pattern:**

If your winter/summer consumption is different:

```python
consumption = ConsumptionProfile(
    monthly_consumption_kwh=500,
    monthly_factors=[
        1.3,  # Jan - high heating
        1.2,  # Feb
        1.1,  # Mar
        0.95, # Apr
        0.85, # May
        0.8,  # Jun - low usage
        0.8,  # Jul
        0.85, # Aug
        0.9,  # Sep
        0.95, # Oct
        1.1,  # Nov
        1.3   # Dec - high heating
    ]
)
```

---

## 🎯 **What You Should Do Now**

1. **✅ Run the demo**: `python example_with_ev_seasonal.py`
2. **✅ Read the output**: Understand the seasonal breakdown
3. **✅ Customize with your data**: Edit the example file
4. **✅ Compare scenarios**: Try with/without EV, different system sizes
5. **✅ Read full docs**: Check `UPDATES_EV_SEASONAL.md` for details
6. **✅ Make informed decisions**: Use realistic seasonal data for planning

---

## 📞 **Getting Help**

### **Understanding Results:**

- Read `UPDATES_EV_SEASONAL.md` (comprehensive guide)
- Check `IMPLEMENTATION_SUMMARY.md` (technical details)
- Review example code comments

### **Customizing:**

- All parameters are documented in code
- Sensible defaults provided
- Examples show common scenarios

---

## 🎉 **Summary**

### **✅ What's Been Added:**

1. EV charging support (evening charging pattern)
2. Seasonal solar production (realistic winter/summer)
3. Seasonal consumption patterns
4. Battery prioritization (household over EV)
5. Detailed reporting with breakdowns
6. Month-by-month simulation

### **✅ What You Get:**

1. **More accurate** cost projections
2. **Realistic expectations** for winter performance
3. **EV impact clarity** on electricity costs
4. **Better decisions** on system sizing
5. **Smart battery** usage modeling

### **✅ Backward Compatible:**

- Old code still works
- New features are optional
- Sensible defaults provided

---

**🎊 You now have a professional-grade PV feasibility calculator with realistic EV charging and seasonal modeling!**

Start with the demo, customize for your situation, and make informed decisions about your solar investment.

---

**Version**: 2.0  
**Last Updated**: October 2025  
**Status**: ✅ Ready to use!
