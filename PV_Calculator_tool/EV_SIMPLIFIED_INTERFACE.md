# EV Charging - Simplified Interface

## Overview

The EV charging interface has been **simplified** to focus on essential parameters. The system now automatically calculates charging duration based on daily consumption needs.

## What Changed

### ❌ Removed Features
- **Charging Days Checkboxes**: No longer need to select specific days
- **Preset Buttons**: Removed overnight, solar, evening presets  
- **Manual Hour Selection**: No 24 checkboxes for individual hours

### ✅ New Simplified Approach
- **Charging Start Time**: Single spinner to select when charging begins (00-23)
- **Automatic Duration**: System calculates how long charging takes
- **Auto-Calculated Hours**: Charging continues until daily needs are met
- **Visual Feedback**: Shows daily consumption, duration, and end time

## User Interface

```
┌─────────────────────────────────────────────────────────────────┐
│ Electric Vehicle Charging (Optional)                            │
├─────────────────────────────────────────────────────────────────┤
│ ☑ Include EV Charging                                           │
│                                                                   │
│ Car Make:        [Tesla                  ▼]                     │
│ Car Model:       [Model 3                ▼]                     │
│ Year:            [2024                   ▼]                     │
│ Consumption:     [14.4          ] kWh/100km (auto-filled)      │
│ Weekly Distance: [300           ] (60 km/day × 7 days)         │
│ Home Charger:    [7.0           ] (typical: 3.7-22 kW)         │
│                                                                   │
│ Charging Start Time: [22:00▼] (charging will continue until    │
│                                 daily consumption is met)       │
│                                                                   │
│ ℹ️ Daily EV consumption: 6.17 kWh | Charging duration: 0h 53min│
│    Charging period: 22:00 - 22:53                               │
│                                                                   │
│ 💡 Select your car to auto-fill consumption. Charging starts   │
│    at selected time and continues until daily needs are met.    │
└─────────────────────────────────────────────────────────────────┘
```

## How It Works

### Step 1: Configure Your EV
```
1. Check ☑ "Include EV Charging"
2. Select car (or enter consumption manually)
3. Enter weekly distance (e.g., 300 km)
4. Enter charger power (e.g., 7 kW)
```

### Step 2: Set Charging Start Time
```
1. Use spinner to select start hour (0-23)
2. Example: 22 = 22:00 (10 PM)
3. System automatically calculates:
   - Daily EV consumption
   - Charging duration
   - End time
```

### Step 3: View Results
```
The info line shows:
- Daily EV consumption: X.XX kWh
- Charging duration: Xh XXmin
- Charging period: HH:MM - HH:MM
```

### Step 4: See in Graphs
```
- Go to Energy Flow Analysis tab
- Click "Daily Energy Flow"
- Purple shaded areas show EV charging hours
- Summary box shows EV charging details
```

## Examples

### Example 1: Light Commuter
```
Car: VW e-Up! (2024) - 15.5 kWh/100km
Weekly Distance: 150 km
Charger Power: 7 kW
Charging Start: 23:00

Calculation:
- Daily: 150/7 × 15.5/100 = 3.32 kWh
- Duration: 3.32 / 7 = 0.47 hours = 28 minutes
- Period: 23:00 - 23:28

Result: Charges for less than 30 minutes!
```

### Example 2: Average Commuter
```
Car: Tesla Model 3 (2024) - 14.4 kWh/100km
Weekly Distance: 300 km
Charger Power: 7 kW
Charging Start: 22:00

Calculation:
- Daily: 300/7 × 14.4/100 = 6.17 kWh
- Duration: 6.17 / 7 = 0.88 hours = 53 minutes
- Period: 22:00 - 22:53

Result: Charges for just under 1 hour
```

### Example 3: Heavy Commuter
```
Car: BMW iX (2024) - 19.4 kWh/100km
Weekly Distance: 500 km
Charger Power: 7 kW
Charging Start: 21:00

Calculation:
- Daily: 500/7 × 19.4/100 = 13.86 kWh
- Duration: 13.86 / 7 = 1.98 hours = 1h 59min
- Period: 21:00 - 22:59

Result: Charges for about 2 hours
```

### Example 4: Slower Charger
```
Car: Nissan Leaf (2024) - 17.1 kWh/100km
Weekly Distance: 250 km
Charger Power: 3.7 kW (slower charger)
Charging Start: 22:00

Calculation:
- Daily: 250/7 × 17.1/100 = 6.11 kWh
- Duration: 6.11 / 3.7 = 1.65 hours = 1h 39min
- Period: 22:00 - 23:39

Result: Takes longer with slower charger
```

## Daily Energy Flow Graph

The daily energy flow graph now shows EV charging:

### Visual Indicators
- **Purple Shaded Areas**: Hours when EV is charging
- **Legend Entry**: "EV Charging" in the legend
- **Summary Box**: Shows EV charging details

### Summary Box Information
```
Daily Totals:
Consumption: 23.4 kWh
Generation: 18.2 kWh
Self-sufficiency: 77.8%
Grid Import: 5.2 kWh
Grid Export: 0.0 kWh
Battery Cycles: 0.42

EV Charging:
Daily: 6.17 kWh
Period: 22:00-23:00
Hours: 1h
```

### What You See
1. **Top Panel**: Consumption vs Generation
   - Purple bands show when EV charges
   - Total consumption includes EV
   
2. **Summary**: Right corner shows
   - EV daily consumption
   - Charging time period
   - Duration in hours

## Calculation Details

### Formula
```python
# Daily consumption
daily_km = weekly_km / 7
daily_kwh = (daily_km / 100) × consumption_per_100km

# Charging duration
duration_hours = daily_kwh / charger_power_kw

# Charging hours
start_hour = user_selected
end_hour = start_hour + duration_hours
charging_hours = [all hours from start to end]
```

### Example Walkthrough
```
Input:
- Weekly: 300 km
- Efficiency: 18 kWh/100km
- Charger: 7 kW
- Start: 22:00

Step 1: Daily consumption
300 / 7 = 42.86 km/day
42.86 / 100 × 18 = 7.71 kWh/day

Step 2: Duration
7.71 / 7 = 1.10 hours = 1h 6min

Step 3: End time
22:00 + 1:10 = 23:06

Step 4: Charging hours
[22, 23] (rounds up to include partial hours)

Result:
- Daily: 7.71 kWh
- Duration: 1h 6min
- Period: 22:00-23:06
- Charges every day
```

## Benefits

### ✅ Simpler Configuration
- **3 seconds** instead of 30+ clicks
- Just set start time
- System does the math

### ✅ Realistic Behavior
- Based on actual daily needs
- Accounts for charger power
- Shows exact end time

### ✅ Clear Feedback
- See daily consumption
- See charging duration
- See time period

### ✅ Visual Indication
- Purple bands in graphs
- Summary box details
- Easy to understand

## Tips

### Tip 1: Choose Start Time Wisely
```
Consider:
- Off-peak electricity rates (usually 22:00-06:00)
- When car will be parked
- Avoid household peak hours (18:00-21:00)
```

### Tip 2: Check Duration
```
If duration > 8 hours:
- Consider faster charger
- Or reduce weekly distance
- Or check car efficiency
```

### Tip 3: Solar Optimization
```
For daytime solar charging:
- Set start time: 11:00 or 12:00
- Charging during peak solar
- Maximize self-consumption
```

### Tip 4: Charger Power Matters
```
3.7 kW:  Good for overnight (8+ hours available)
7 kW:    Standard home charger (3-4 hours needed)
11 kW:   Fast home charger (2 hours needed)
22 kW:   Very fast (1 hour needed)
```

## Troubleshooting

### Issue: Duration too long

**Check:**
- Is charger power correct? (not daily consumption)
- Is weekly distance realistic?
- Is car consumption accurate?

**Solution:**
- Increase charger power, or
- Reduce weekly distance, or
- Select more efficient car

### Issue: Charging wraps past midnight

**This is normal!**
```
Example:
- Start: 23:00
- Duration: 3 hours
- End: 02:00 (next day)
- Charging hours: [23, 0, 1, 2]
```

### Issue: Info line not updating

**Solution:**
- Enter all values first (distance, charger power)
- Select car to auto-fill consumption
- Change start time to trigger update

### Issue: Not showing in graph

**Solution:**
1. Click "Calculate" button
2. Go to "Energy Flow Analysis" tab
3. Click "Daily Energy Flow" button
4. Check that EV is enabled

## Technical Notes

### Charging Algorithm
```
1. Calculate daily needs
2. Divide by charger power = duration
3. Add 1 hour buffer for safety
4. Generate list of hours from start
5. Wraps around midnight if needed
```

### Charging Days
```
Now charges every day by default (simplified)
- Realistic: people charge daily
- Simplifies interface
- Average daily consumption used
```

### Integration
```
- Automatically creates EVConsumptionProfile
- Adds to HouseholdProfile
- Used in all consumption calculations
- Shown in graphs with visual indicators
```

## Summary

The simplified interface makes EV configuration **faster and easier**:

1. ✅ **Set start time** (one spinner)
2. ✅ **System calculates duration** (automatic)
3. ✅ **View in graphs** (purple indicators)
4. ✅ **Done!** (3 seconds vs 30+ clicks)

**Before**: 7 day checkboxes + 24 hour checkboxes + 3 preset buttons = Complex  
**After**: 1 time spinner + auto-calculation = Simple ✨

---

**Ready to try it?** Open the GUI and set your charging start time!

**Questions?** The info line shows all the details you need.

