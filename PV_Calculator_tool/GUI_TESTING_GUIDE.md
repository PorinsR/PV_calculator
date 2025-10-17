# GUI Testing Guide - All New Features

## 🚀 Quick Start

Launch the GUI with all new features:

```bash
python PV_calculator_gui.py
```

---

## ✨ What's New in the GUI

The GUI now includes **Electric Vehicle (EV) charging parameters**! You can test:

1. **Seasonal solar production** (automatic, built-in)
2. **Seasonal consumption patterns** (automatic, built-in)
3. **EV charging support** (NEW section in GUI!)

---

## 📋 Testing Scenarios

### **Scenario 1: Household WITHOUT EV (Baseline)**

**Setup:**

1. Open GUI: `python PV_calculator_gui.py`
2. Leave "Include EV Charging" **UNCHECKED**
3. Set your parameters:
   - Monthly Consumption: `500` kWh
   - PV System Size: `5.0` kWp
   - Battery: `7.0` kWh (optional, check/uncheck to compare)
4. Click **Calculate**

**What to look for in Results:**

- Only household consumption shown
- Self-sufficiency ratio for household
- No EV-related metrics

---

### **Scenario 2: Household WITH EV**

**Setup:**

1. **CHECK** "Include EV Charging"
2. Set EV parameters:
   - Daily Driving: `60` km (typical commute)
   - Vehicle Efficiency: `25` kWh/100km (typical EV)
   - Charger Power: `7.0` kW (Level 2 home charger)
3. Keep other parameters same as Scenario 1
4. Click **Calculate**

**What to look for in Results:**

```
CURRENT SITUATION (WITHOUT PV)
--------------------------------
Annual Household Consumption: 6,000 kWh
Annual EV Consumption: 5,475 kWh  ← NEW!
Total Annual Consumption: 11,475 kWh

EV Charging Profile:
  Daily Driving: 15.0 kWh (~60 km)
  Charging Hours: 12 hours/day (evening/night)
  Note: EV charges from grid (battery reserved for household use)

SCENARIO 1: PV SYSTEM WITHOUT BATTERY
--------------------------------------
Annual Grid Import: 7,975 kWh
  - Household: 2,500 kWh  ← Shows breakdown
  - EV Charging: 5,475 kWh  ← EV always from grid
Household Self-Sufficiency: 58%
Total Self-Sufficiency (incl. EV): 31%  ← Lower because EV charges at night
```

---

### **Scenario 3: Different EV Usage Patterns**

Test how different driving distances affect costs:

#### Light Use (30 km/day):

- Daily Driving: `30` km
- Expected EV consumption: ~7.5 kWh/day = 2,738 kWh/year

#### Medium Use (60 km/day):

- Daily Driving: `60` km
- Expected EV consumption: ~15 kWh/day = 5,475 kWh/year

#### Heavy Use (100 km/day):

- Daily Driving: `100` km
- Expected EV consumption: ~25 kWh/day = 9,125 kWh/year

**Compare the results!** See how EV usage impacts:

- Total electricity costs
- Grid dependence
- Value of PV system

---

### **Scenario 4: Different EV Efficiencies**

Test different vehicle types:

#### Efficient EV (Tesla Model 3):

- Efficiency: `15` kWh/100km
- Daily Driving: 60 km
- Daily consumption: 9 kWh

#### Average EV (Most EVs):

- Efficiency: `20-25` kWh/100km
- Daily Driving: 60 km
- Daily consumption: 12-15 kWh

#### Less Efficient (SUV/Truck):

- Efficiency: `30` kWh/100km
- Daily Driving: 60 km
- Daily consumption: 18 kWh

---

### **Scenario 5: Battery Value with EV**

Compare PV+Battery vs PV-only **with EV**:

**Test A: PV Only (no battery)**

1. Check "Include EV Charging"
2. **UNCHECK** "Include Battery Storage"
3. Calculate
4. Note the payback period

**Test B: PV + Battery**

1. Keep "Include EV Charging" checked
2. **CHECK** "Include Battery Storage"
3. Calculate
4. Note the payback period

**Key Question:** Does battery significantly improve payback when you have an EV?

**Expected Answer:** Not much! Battery helps household evening loads, but EV charges at night from grid anyway.

---

## 🎯 Key Things to Verify

### ✅ **Check 1: EV Doesn't Use Battery**

Look for this note in the results:

```
Note: EV charges from grid (battery reserved for household use)
```

### ✅ **Check 2: Separate Tracking**

Results should show:

```
Annual Grid Import: X kWh
  - Household: Y kWh
  - EV Charging: Z kWh
```

### ✅ **Check 3: Two Self-Sufficiency Metrics**

```
Household Self-Sufficiency: 58%  ← PV coverage of home
Total Self-Sufficiency (incl. EV): 31%  ← Including EV (lower!)
```

### ✅ **Check 4: Seasonal Effects (Automatic)**

The calculator now uses seasonal data automatically:

- Winter months: Lower PV production
- Summer months: Higher PV production
- This affects the annual cost calculations

---

## 📊 Example Test Results

### Without EV:

```
Annual Consumption: 6,000 kWh
Annual Cost (without PV): €950
Annual Cost (with 5kWp PV + battery): €320
Annual Savings: €630
Payback: 12.7 years
Self-Sufficiency: 58%
```

### With EV (60 km/day):

```
Annual Household: 6,000 kWh
Annual EV: 5,475 kWh
Total Consumption: 11,475 kWh

Annual Cost (without PV): €1,650
Annual Cost (with 5kWp PV + battery): €870
Annual Savings: €780
Payback: 13.5 years

Household Self-Sufficiency: 58% (same!)
Total Self-Sufficiency: 31% (much lower)
```

**Key Insight:** EV adds €700/year to costs, but PV only saves an extra €150/year on EV because it charges at night!

---

## 🧪 Advanced Testing

### **Test 1: Impact of System Size**

Run with different PV sizes:

- 3 kWp
- 5 kWp
- 8 kWp

**Question:** Does a bigger system help with EV?
**Answer:** Indirectly yes (more summer surplus to offset EV costs economically), but not directly (EV still charges from grid at night)

### **Test 2: Battery Size Sensitivity**

Try different battery sizes with EV enabled:

- 5 kWh
- 10 kWh
- 15 kWh

**Question:** Does bigger battery help EV?
**Answer:** No! Battery is for household evening loads. EV charges from grid.

### **Test 3: Compare Regions**

Change solar irradiance:

- `2.5` (Northern Europe)
- `3.5` (Central Europe)
- `4.5` (Southern Europe)

**Question:** How does location affect EV impact?
**Answer:** Better solar helps household more, EV benefit is indirect through economic offset.

---

## 💾 Save & Load Configurations

### Save Your Configuration:

1. Set all parameters
2. Click **Save Configuration**
3. Creates `pv_calculator_config.json`

### Load Configuration:

1. Click **Load Configuration**
2. Restores all settings including EV parameters

### Reset to Defaults:

1. Click **Reset to Defaults**
2. Restores factory settings

---

## 📈 Using Graphs

After calculating, go to **Graphs** tab:

### **Break-Even Analysis:**

- Shows when investment pays for itself
- Compares PV-only vs PV+Battery
- NOW accounts for EV costs if enabled!

### **Cost Comparison:**

- Bar chart of annual costs
- Shows savings with PV
- Includes EV consumption if enabled

### **Energy Flow:**

- Visualizes daily energy usage
- Shows household vs grid sources
- EV shown separately in calculations

### **ROI Comparison:**

- Investment breakdown
- Payback period comparison
- Accounts for total consumption

---

## 🎓 Understanding the Numbers

### **Daily Energy Calculation:**

```
Daily kWh = (Daily km × Efficiency) / 100

Example:
60 km × 25 kWh/100km = 15 kWh/day
15 kWh/day × 365 days = 5,475 kWh/year
```

### **Cost Impact:**

```
EV Annual Cost = Daily kWh × 365 × Electricity Rate

Example:
15 kWh/day × 365 × €0.13/kWh = €712/year
```

### **Self-Sufficiency:**

```
Household Self-Sufficiency = PV used / Household consumption
Total Self-Sufficiency = PV used / (Household + EV)

Example with EV:
3,500 kWh (PV used) / 6,000 kWh (household) = 58%
3,500 kWh (PV used) / 11,475 kWh (total) = 31%
```

---

## 🐛 Troubleshooting

### **Problem: Can't see EV section**

**Solution:** Scroll down in the Input Parameters tab. It's below Nord Pool section.

### **Problem: EV consumption seems wrong**

**Solution:** Check your efficiency. Typical EVs: 15-30 kWh/100km

### **Problem: Results don't show EV breakdown**

**Solution:** Make sure "Include EV Charging" is CHECKED before calculating

### **Problem: Battery doesn't help EV**

**Solution:** That's correct! Battery is reserved for household. See the blue note in EV section.

---

## ✅ Quick Test Checklist

- [ ] Launch GUI: `python PV_calculator_gui.py`
- [ ] Test without EV (baseline)
- [ ] Test with EV (60 km/day)
- [ ] Compare results side-by-side
- [ ] Verify EV charges from grid (not battery)
- [ ] Check two self-sufficiency metrics appear
- [ ] Test different driving distances
- [ ] Try with/without battery
- [ ] Save configuration
- [ ] Generate graphs
- [ ] Export results to file

---

## 🎉 You're Ready!

The GUI now fully supports testing:

- ✅ **EV charging** (evening, from grid)
- ✅ **Seasonal variations** (automatic)
- ✅ **Battery prioritization** (household first)
- ✅ **Detailed breakdowns** (household vs EV)
- ✅ **Multiple scenarios** (save/load configs)

**Start testing and see how EV impacts your PV system economics!** 🚗⚡☀️

---

**Pro Tip:** Run calculation twice - once without EV, once with EV - and compare the reports side-by-side to see the exact impact of adding an electric vehicle to your household!
