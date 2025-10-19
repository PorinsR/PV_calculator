# EV Consumption GUI - Visual Guide

## What You'll See in the GUI

### Input Parameters Tab - EV Section (Enhanced)

```
┌─────────────────────────────────────────────────────────────────────┐
│ Electric Vehicle Charging (Optional)                                │
├─────────────────────────────────────────────────────────────────────┤
│ ☑ Include EV Charging                                               │
│                                                                       │
│ Car Make:        [Tesla                  ▼]                         │
│ Car Model:       [Model 3                ▼]                         │
│ Year:            [2024                   ▼]                         │
│ Consumption:     [14.4                    ] kWh/100km (auto-filled) │
│ Weekly Distance: [300                     ] (60 km/day × 7 days)    │
│ Home Charger:    [7.0                     ] (typical: 3.7-22 kW)    │
│                                                                       │
│ Charging Days:                                                       │
│ ☑ Mon  ☑ Tue  ☑ Wed  ☑ Thu  ☑ Fri  ☐ Sat  ☐ Sun                   │
│                                                                       │
│ Charging Hours:                                                      │
│ Presets: [Overnight (22-06)] [Daytime Solar (11-15)] [Evening (18-23)]
│                                                                       │
│ ☐00 ☐01 ☐02 ☐03 ☐04 ☐05 ☐06 ☐07 ☐08 ☐09 ☐10 ☐11                  │
│ ☐12 ☐13 ☐14 ☐15 ☐16 ☐17 ☐18 ☐19 ☐20 ☐21 ☑22 ☑23                  │
│                                                                       │
│ 💡 Select your car to auto-fill consumption.                        │
│    Configure charging days and hours for realistic patterns.        │
└─────────────────────────────────────────────────────────────────────┘
```

### Example Configurations

#### Configuration 1: Typical Weekday Commuter

```
☑ Include EV Charging

Car: Tesla Model 3 (2024) → 14.4 kWh/100km
Weekly Distance: 300 km

Charging Days:
☑ Mon  ☑ Tue  ☑ Wed  ☑ Thu  ☑ Fri  ☐ Sat  ☐ Sun

Charging Hours: (Overnight preset)
☑00 ☑01 ☑02 ☑03 ☑04 ☑05 ☑06 ☐07 ☐08 ... ☑22 ☑23

Result:
• 54 kWh per week
• 10.8 kWh per weekday
• 1.2 kWh per hour
• Charges 22:00-06:00 on weekdays
```

#### Configuration 2: Solar Optimizer

```
☑ Include EV Charging

Car: VW ID.4 (2024) → 17.3 kWh/100km
Weekly Distance: 200 km

Charging Days:
☑ Mon  ☑ Tue  ☑ Wed  ☑ Thu  ☑ Fri  ☐ Sat  ☐ Sun

Charging Hours: (Daytime Solar preset)
☐00 ☐01 ... ☐10 ☑11 ☑12 ☑13 ☑14 ☑15 ☐16 ... ☐23

Result:
• 34.6 kWh per week
• 6.92 kWh per weekday
• 1.38 kWh per hour
• Charges 11:00-15:00 (peak solar)
• Maximum self-consumption
```

#### Configuration 3: Weekend Only

```
☑ Include EV Charging

Car: BMW iX (2024) → 19.4 kWh/100km
Weekly Distance: 400 km

Charging Days:
☐ Mon  ☐ Tue  ☐ Wed  ☐ Thu  ☐ Fri  ☑ Sat  ☑ Sun

Charging Hours: (Custom selection)
☐00 ... ☐09 ☑10 ☑11 ☑12 ☑13 ☑14 ☑15 ☑16 ☐17 ... ☐23

Result:
• 77.6 kWh per week
• 38.8 kWh per weekend day
• 5.54 kWh per hour
• Charges 10:00-16:00 on weekends
```

## How to Use

### Step-by-Step Guide

#### Step 1: Enable EV
```
1. Go to "Input Parameters" tab
2. Scroll to "Electric Vehicle Charging (Optional)"
3. Check ☑ "Include EV Charging"
```

#### Step 2: Select Your Car
```
1. Click "Car Make" dropdown
2. Select your EV brand (Tesla, VW, BMW, etc.)
3. Select "Car Model"
4. Select "Year"
5. → Consumption automatically filled
```

Or manually enter:
```
- Enter consumption in kWh/100km
- Typical range: 14-25 kWh/100km
```

#### Step 3: Enter Weekly Distance
```
1. In "Weekly Distance" field
2. Enter your weekly driving (km)
3. Examples:
   - 100-150 km: Light user
   - 200-300 km: Average commuter
   - 400-500 km: Heavy commuter
```

#### Step 4: Select Charging Days
```
Click checkboxes for days you charge:
☑ Mon  ☑ Tue  ☑ Wed  ☑ Thu  ☑ Fri  ☐ Sat  ☐ Sun

Common patterns:
- Weekdays only (Mon-Fri): Regular commute
- Daily: Every day for short-range EVs
- Weekends only: Light usage or free weekend rates
```

#### Step 5: Select Charging Hours

**Option A: Use Presets (Easy)**
```
Click one of the preset buttons:
[Overnight (22-06)]  → 22:00-06:00 (9 hours)
[Daytime Solar (11-15)] → 11:00-15:00 (5 hours)
[Evening (18-23)]    → 18:00-23:00 (6 hours)
```

**Option B: Manual Selection**
```
Click individual hour checkboxes:
☐00 ☐01 ☐02 ... ☑22 ☑23

Tips:
- Select enough hours for your daily consumption
- Avoid household peak hours if possible
- Match solar production hours if available
```

#### Step 6: Calculate
```
1. Click [Calculate] button
2. View results in main output
3. Go to "Energy Flow Analysis" tab
4. Click graph buttons to see EV consumption
```

## Visual Indicators

### When EV is Included

**Consumption Graphs Show:**
```
Daily Pattern:
  Hour | Household | EV   | Total
  00:00| 0.5 kWh   | 1.2  | 1.7 kWh ⚡
  01:00| 0.5 kWh   | 1.2  | 1.7 kWh ⚡
  ...
  19:00| 2.1 kWh   | 0.0  | 2.1 kWh
  22:00| 1.0 kWh   | 1.2  | 2.2 kWh ⚡
  23:00| 0.9 kWh   | 1.2  | 2.1 kWh ⚡
  
⚡ = EV charging active
```

**Annual Statistics:**
```
Total Annual: 8,808 kWh
  - Household: 6,000 kWh
  - EV: 2,808 kWh
  
Average Daily: 24.13 kWh
  - Household: 16.44 kWh
  - EV: 7.69 kWh
```

## Quick Reference

### Preset Charging Schedules

| Preset | Hours | Total Hours | Best For |
|--------|-------|-------------|----------|
| **Overnight** | 22:00-06:00 | 9 hours | Most common, cheap rates |
| **Daytime Solar** | 11:00-15:00 | 5 hours | Solar self-consumption |
| **Evening** | 18:00-23:00 | 6 hours | After work, before bed |

### Weekly Distance Guide

| User Type | Weekly km | Annual km | Daily Avg |
|-----------|-----------|-----------|-----------|
| Light user | 100-150 | 5,200-7,800 | 14-21 km |
| Average | 200-300 | 10,400-15,600 | 29-43 km |
| Heavy commuter | 400-500 | 20,800-26,000 | 57-71 km |
| Very high | 600+ | 31,200+ | 86+ km |

### Consumption by Vehicle

| Vehicle Type | kWh/100km |
|--------------|-----------|
| Small EV (e.g., VW e-Up!) | 14-16 |
| Mid-size (e.g., Tesla Model 3) | 16-18 |
| Large (e.g., Tesla Model S) | 18-22 |
| SUV (e.g., BMW iX) | 22-26 |
| Add 20-30% in winter | |

## Tips & Tricks

### Tip 1: Quick Setup
```
1. Select car make/model (auto-fills consumption)
2. Enter your weekly driving
3. Click "Overnight (22-06)" preset
4. Done! Click Calculate
```

### Tip 2: Optimize for Solar
```
If you have solar panels:
1. Use "Daytime Solar (11-15)" preset
2. Charge Mon-Fri when home
3. Maximize free solar energy
4. Reduce grid usage
```

### Tip 3: Check Charging Rate
```
Your hourly rate = Daily consumption / Charging hours

Example:
- Daily: 10.8 kWh
- Hours: 9 hours
- Rate: 1.2 kWh/hour

Ensure this is < your charger power (typically 7 kW)
```

### Tip 4: Weekend Strategy
```
For light usage (<150 km/week):
- Charge only weekends
- Select Sat-Sun
- Use daytime hours (10:00-16:00)
- Benefit from weekend solar
```

### Tip 5: Save Your Config
```
After setting up:
1. Click [Save Configuration]
2. Settings saved to pv_calculator_config.json
3. Auto-loads next time
```

## Troubleshooting

### Problem: "Consumption not showing in graphs"

**Solution:**
1. ✓ Check "Include EV Charging" is enabled
2. ✓ Enter weekly distance > 0
3. ✓ Select at least one charging day
4. ✓ Select at least one charging hour
5. ✓ Click [Calculate] button
6. ✓ Go to Energy Flow Analysis tab

### Problem: "Preset buttons don't change hours"

**Check:**
- Ensure checkboxes are visible
- Try clicking preset again
- Manually check/uncheck to verify responsiveness

### Problem: "Numbers don't add up"

**Verify:**
```
Weekly consumption = (weekly_km / 100) × kWh_per_100km

Example:
300 km / 100 × 18 kWh/100km = 54 kWh/week ✓
```

### Problem: "Configuration not saving"

**Try:**
1. Check file permissions
2. Look for `pv_calculator_config.json` in app directory
3. Try "Save Configuration" again
4. Restart app and check if loaded

## Benefits Summary

### For Daily Use

✅ **Easy Configuration**
- Point-and-click interface
- No complex calculations
- Visual selection of days/hours
- Quick presets for common scenarios

✅ **Realistic Modeling**
- Based on actual driving patterns
- Flexible scheduling
- Separate tracking
- Accurate projections

### For Analysis

✅ **Detailed Insights**
- See when EV charges
- Household vs EV breakdown
- Hourly detail
- Annual projections

✅ **Solar Optimization**
- Model daytime charging
- Maximize self-consumption
- Reduce grid dependency
- Calculate savings

✅ **Cost Analysis**
- Compare charging scenarios
- Grid vs solar costs
- Time-of-use optimization
- ROI calculations

## Next Steps

1. **Configure Your EV** - Use this guide to set up your charging schedule
2. **Run Calculations** - Click Calculate to see results
3. **View Graphs** - Check Energy Flow Analysis for visual insights
4. **Optimize** - Try different schedules to find the best option
5. **Save** - Save your configuration for future use

---

**Questions?** See the full documentation:
- `README_EV_FEATURE.md` - Overview
- `EV_CONSUMPTION_FEATURE.md` - Complete API docs
- `EV_CONSUMPTION_QUICKSTART.md` - Quick start guide

**Ready to start?** Open the GUI and follow Step 1 above!

