# Weekly Energy Balance Graph Feature

## Overview

A new interactive graph that displays **hourly energy balance** for any week of the year (1-52), showcasing the day-wise consumption profiles and season-aware PV generation patterns.

## What It Shows

The graph has **3 panels** displaying complementary information:

### Panel 1: PV Generation vs Consumption (Hourly)
- **Orange area**: PV solar generation hour-by-hour
- **Red area**: Total household consumption (including EV if enabled)
- **Day labels**: Shows which days are weekdays (black) vs weekends (blue, bold)
- **Vertical lines**: Separate each day

**What to observe**:
- Summer: PV generates from 5 AM to 9 PM
- Winter: PV generates only 8 AM to 4 PM
- Weekdays: Lower midday consumption (people at work)
- Weekends: Higher daytime consumption (people at home)

### Panel 2: Net Energy Balance (Hourly)
- **Green areas**: Excess energy (exported to grid)
- **Red areas**: Energy deficit (imported from grid)
- **Blue dashed line**: Battery state of charge (if battery enabled)
- **Black line**: Net balance

**What to observe**:
- Positive values = exporting to grid
- Negative values = importing from grid
- Battery charges during excess, discharges during deficit
- Shows when you're self-sufficient vs grid-dependent

### Panel 3: Daily Energy Summary (Bar Chart)
- **Orange bars**: PV generated each day
- **Red bars**: Total consumed each day
- **Green bars**: Exported to grid each day
- **Dark red bars**: Imported from grid each day
- **Blue background**: Weekend days highlighted
- **Summary box**: Week totals and self-sufficiency percentage

## Key Insights You Can See

### 1. Weekday vs Weekend Patterns

**Weekday (Monday-Friday)**:
```
Hour 08:00 = 0.850 kW  (morning rush)
Hour 12:00 = 0.420 kW  (people away at work - LOW)
Hour 18:00 = 1.440 kW  (evening peak - HIGHEST)
```

**Weekend (Saturday-Sunday)**:
```
Hour 08:00 = 1.200 kW  (leisurely breakfast)
Hour 12:00 = 0.630 kW  (cooking, activities - HIGHER than weekday)
Hour 18:00 = 1.260 kW  (evening activities)
```

### 2. Summer Week Example (Week 26 - Late June)

**PV Generation**: 22.3 kWh/day
- Starts: ~5:00 AM
- Peak: 12:00 PM (2.5 kW)
- Still generating at 6 PM: 1.0 kW ✅
- Ends: ~9:00 PM

**Result**: When everyone gets home at 6 PM, PV is **still generating**!
- Direct solar power available
- Battery charged from afternoon excess
- Minimal grid import needed

### 3. Winter Week Example (Week 1 or 52 - December/January)

**PV Generation**: 3.7 kWh/day
- Starts: ~8:00 AM
- Peak: 12:00 PM (0.9 kW)
- Already stopped by 6 PM: 0 kW ❌
- Ends: ~4:00 PM

**Result**: When everyone gets home at 6 PM, PV has **stopped**!
- No direct solar power
- Must use battery (if available) or grid
- High grid import during evening peak

### 4. Battery Impact

**Without Battery**:
- All excess PV exported to grid (lower revenue)
- All evening deficit imported from grid (higher cost)

**With Battery** (e.g., 7 kWh):
- Afternoon: Charges from excess PV
- Evening: Discharges to cover consumption
- Reduces grid import by ~30-40%
- Better ROI in scenarios with clear day/evening split

## How to Use

### In GUI

1. **Run a calculation** first (Input Parameters → Calculate)
2. Go to **Graphs** tab
3. **Select Week** using the spinner (1-52)
   - Week 1 = January 1-7
   - Week 13 = Late March
   - Week 26 = Late June (peak summer)
   - Week 39 = Late September
   - Week 52 = Late December
4. Click **"Weekly Energy Balance"** button
5. Graph will display showing that specific week

### In Python Code

```python
from PV_calculator import *
from PV_calculator_graphs import PVGraphGenerator

# Setup your calculator
calculator = PVFeasibilityCalculator(
    tariff=tariff,
    consumption=consumption,
    pv_system=pv_system,
    battery=battery,
    # ...
)

# Create graph generator
graph_gen = PVGraphGenerator(calculator)

# Generate weekly graph for any week
graph_gen.plot_weekly_energy_balance(
    week_number=26,      # Late June (summer)
    with_battery=True,   # Include battery simulation
    show=True,           # Display interactively
    save_path="week_26_june.png"  # Optional: save to file
)
```

### Recommended Weeks to Compare

| Week | Month | Season | Why Compare |
|------|-------|--------|-------------|
| 1 | Early January | Winter | Shortest days, highest consumption |
| 13 | Late March | Spring | Transition period, DST starts |
| 26 | Late June | Summer | Longest days, peak PV generation |
| 39 | Late September | Fall | Transition period, DST ends |
| 52 | Late December | Winter | Shortest days, holiday consumption |

## Real-World Scenario Analysis

### Example: Your Use Case

**System**: 5 kWp PV + 7 kWh Battery + EV charging

**Week 26 (Summer)** - Wednesday 6 PM:
- PV generating: 1.0 kW ✅
- Household demand: 1.4 kW
- Battery state: 6.5 kWh (charged)
- Result: PV (1.0 kW) + Battery (0.4 kW) = **No grid import**

**Week 1 (Winter)** - Wednesday 6 PM:
- PV generating: 0 kW ❌
- Household demand: 1.4 kW
- Battery state: 2.0 kWh (limited daytime charging)
- Result: Battery (1.4 kW until depleted) → **Grid import needed**

## Understanding the Patterns

### Why Lower Daytime Consumption on Weekdays?

Realistic assumption: People are away at work/school during the day
- Lights off
- Heating/cooling reduced
- Only fridges, standby devices running
- Multiplier: 0.70x normal (9 AM - 3 PM)

### Why Higher Evening Consumption?

Everyone home simultaneously:
- Cooking dinner
- Lights on
- TV, entertainment
- Heating/cooling at comfort level
- EV charging starts (if enabled)
- Multiplier: 1.20x normal (6-7 PM)

### Why Higher Weekend Daytime Consumption?

People at home doing activities:
- Extended meal preparation
- Laundry, cleaning
- DIY projects
- Entertainment systems
- Multiplier: 1.05-1.20x normal (daytime)

## Technical Details

### Calculation Method

1. **Week Mapping**: Week number → Calendar dates
   - Week 1 = Jan 1-7
   - Week 2 = Jan 8-14
   - Etc.

2. **Day-of-Week Tracking**: Each day assigned Monday (0) through Sunday (6)
   - Determines which consumption profile to use

3. **Hourly Simulation** (168 hours per week):
   - PV generation based on month's daylight pattern
   - Consumption based on day-of-week + hour + month
   - Battery state tracked hour-by-hour
   - Net balance calculated: PV - Consumption ± Battery

4. **Season-Aware PV**:
   - June: 16.5 hours daylight (5 AM - 9:30 PM)
   - December: 8 hours daylight (8 AM - 4 PM)
   - Bell curve distribution centered at solar noon

### Graph Components

- **Figure Size**: 16×10 inches (high resolution)
- **Panels**: 3 synchronized panels sharing X-axis
- **X-axis**: Hours 0-168 (full week)
- **Day Labels**: Positioned at hour 12, 36, 60, etc. (noon each day)
- **Weekend Highlighting**: Blue shading on daily summary
- **Summary Statistics**: Calculated from hourly data

## Benefits

1. **Visual Validation** of day-wise profiles
   - See the weekday/weekend differences clearly
   - Verify patterns match your lifestyle

2. **Seasonal Understanding**
   - Compare summer vs winter performance
   - Understand when self-sufficiency is highest/lowest

3. **Battery Sizing Insight**
   - See how battery charges/discharges
   - Determine if capacity is adequate
   - Identify if oversized or undersized

4. **Investment Decision Support**
   - Understand when you import from grid
   - See value of battery in evening peaks
   - Compare different system sizes

5. **Realistic Expectations**
   - Not averaged or idealized
   - Shows actual hourly behavior
   - Accounts for human activity patterns

## Limitations & Notes

1. **Weather Not Modeled**: Assumes clear sky conditions
   - Actual cloudy days will have lower PV generation
   - Results represent "typical clear day" for that season

2. **Battery State Reset**: Battery starts each day empty
   - Simplification for clarity
   - Real battery would carry state day-to-day

3. **EV Charging**: If enabled, charges at night (19:00-06:00)
   - Evenly distributed across charging hours
   - Cannot directly use PV (time mismatch)

4. **January 1 = Monday**: Assumption for consistency
   - Real week starts may vary by year
   - Pattern relationships remain valid

## Next Steps

After analyzing weekly patterns:

1. **Optimize System Size**:
   - Too much excess in summer? → Reduce PV size
   - Too much import in winter? → Increase PV size

2. **Adjust Battery Capacity**:
   - Battery always full? → Too large
   - Battery depleted by evening? → Too small

3. **Consider EV Charging Strategy**:
   - Time-of-use tariffs → Shift to night
   - Battery available → Use stored PV energy

4. **Lifestyle Adjustments**:
   - Run appliances during PV generation
   - Use timer-delayed devices for midday
   - Maximize self-consumption

## Conclusion

The Weekly Energy Balance graph transforms abstract numbers into **visual understanding**. You can now:

✅ **See** when your PV generates vs when you consume
✅ **Understand** why summer has better ROI than winter
✅ **Validate** that weekday/weekend patterns match reality
✅ **Optimize** system sizing based on actual patterns
✅ **Make informed** decisions about battery investment

This is the **most realistic** analysis tool in the PV Calculator suite!

