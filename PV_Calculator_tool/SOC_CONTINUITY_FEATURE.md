# Battery SOC Continuity Feature - October 18, 2025

## Overview

The PV Calculator now tracks battery State of Charge (SOC) **continuously across days**, providing realistic multi-day energy flow simulations. When you select any date in the calendar, the system automatically simulates all previous days from January 1st to determine the correct starting battery charge.

---

## How It Works

### The Problem (Before)
Previously, every day started with the battery at 50% charge, regardless of what happened the day before. This meant:
- ❌ Day 1: Battery ends at 30% → Day 2: Battery starts at 50% (unrealistic!)
- ❌ No way to see how battery charge evolves over weeks/months
- ❌ Couldn't identify if battery would run empty in winter

### The Solution (Now)
Now, the battery SOC carries over from one day to the next:
- ✅ Day 1: Battery ends at 30% → Day 2: Battery starts at 30% (realistic!)
- ✅ Can see realistic battery behavior over time
- ✅ Identifies seasonal patterns and potential issues

---

## How to Use

### 1. Select Any Date
In the **Energy Flow Analysis** tab:
- Click the date picker
- Select any date from **2024 to 2030**
- The calendar shows day of the week

### 2. Generate Daily Flow
- Click **"Generate Daily Energy Flow"**
- The system will:
  1. Check if this day's SOC is already cached
  2. If not, simulate all days from Jan 1 to your selected date
  3. Display the energy flow with the correct starting SOC

### 3. View Results
The graph shows:
- **Battery SOC curve**: Shows the actual battery charge throughout the day
- **Starting SOC**: Reflects the battery state from the previous day
- **Ending SOC**: Will be used as the starting point for the next day

---

## Example Scenarios

### Scenario 1: Winter Week (January)
```
Configuration:
  • 10 kWh battery
  • 10 kW solar system
  • 2400 kWh/year consumption

Results:
  Day 1 (Mon): 5.00 kWh → 1.80 kWh (depleting)
  Day 2 (Tue): 1.80 kWh → 1.00 kWh (depleting)
  Day 3 (Wed): 1.00 kWh → 1.00 kWh (at minimum)
  Day 4 (Thu): 1.00 kWh → 1.00 kWh (stable at minimum)
  Day 5 (Fri): 1.00 kWh → 1.00 kWh (stable at minimum)
  Day 6 (Sat): 1.00 kWh → 1.00 kWh (stable at minimum)
  Day 7 (Sun): 1.00 kWh → 1.00 kWh (stable at minimum)

Observation:
  • Battery depletes quickly in winter
  • Stabilizes at minimum SOC (10% = 1.0 kWh)
  • Requires grid import to meet demand
  • Self-sufficiency drops to 53-60%
```

### Scenario 2: Summer Week (June)
```
Configuration:
  • 10 kWh battery
  • 10 kW solar system
  • 2400 kWh/year consumption

Results:
  Day 1 (Mon): 5.00 kWh → 8.82 kWh (charging)
  Day 2 (Tue): 8.82 kWh → 8.82 kWh (stable near-full)
  Day 3 (Wed): 8.82 kWh → 8.82 kWh (stable near-full)
  Day 4 (Thu): 8.82 kWh → 8.82 kWh (stable near-full)
  Day 5 (Fri): 8.82 kWh → 8.82 kWh (stable near-full)
  Day 6 (Sat): 8.82 kWh → 9.03 kWh (charging slightly)
  Day 7 (Sun): 9.03 kWh → 9.03 kWh (stable near-full)

Observation:
  • Battery charges quickly in summer
  • Stays near-full (88-90% SOC)
  • Exports excess to grid
  • 100% self-sufficiency
```

---

## Technical Implementation

### 1. SOC Cache System
```python
# In PVCalculatorGUI.__init__()
self.battery_soc_cache = {}  # Key: (year, day_of_year), Value: final_soc
```

The cache stores the final SOC for each simulated day, so:
- If you view Jan 15, it simulates days 1-14 and caches them
- If you then view Jan 20, it only simulates days 15-19 (reuses cache)
- If you then view Jan 10, it uses the cached value instantly

### 2. Smart Simulation
```python
def get_battery_soc_for_date(year, day_of_year, ...):
    # Day 1: Start at 50%
    if day_of_year == 1:
        return battery_capacity * 0.5
    
    # Check cache
    if (year, day_of_year) in cache:
        return cache[(year, day_of_year)]
    
    # Find last cached day
    last_cached_day = find_last_cached_before(day_of_year)
    
    # Simulate from last cached to target
    for day in range(last_cached_day + 1, day_of_year):
        result = simulate_day(day)
        cache[(year, day)] = result.final_soc
    
    return cache[(year, day_of_year - 1)]  # Previous day's final SOC
```

### 3. Cache Invalidation
The cache is automatically cleared when:
- Configuration changes (battery size, solar size, consumption pattern)
- User clicks "Refresh Configuration"

This ensures the simulation always uses current settings.

---

## Performance Optimization

### Fast Access
- **Cached day**: Instant (< 1ms)
- **Adjacent day**: ~50ms (simulate 1 day)
- **Far day**: ~50ms × days (e.g., day 100 = ~5 seconds first time, instant after)

### Smart Caching
The system intelligently caches intermediate results:
```
View Jan 15: Simulates days 1-14, caches all
View Jan 20: Simulates days 15-19, caches all (reuses 1-14)
View Jan 10: Instant (already cached)
View Feb 1:  Simulates days 21-31, caches all (reuses 1-20)
```

### Memory Usage
- Each cached day: ~16 bytes (year, day, SOC)
- Full year: ~6 KB (365 days)
- Negligible memory footprint

---

## Use Cases

### 1. Battery Sizing Analysis
**Question**: "Is 10 kWh enough for winter?"

**Process**:
1. Set up system with 10 kWh battery
2. View several days in January
3. Observe battery SOC trend

**Answer**:
- If SOC drops to minimum and stays there → Battery too small
- If SOC fluctuates 30-70% → Battery well-sized
- If SOC stays near-full → Battery oversized (or excellent solar/consumption match)

### 2. Seasonal Performance
**Question**: "How does my system perform across seasons?"

**Process**:
1. View a day in January (winter)
2. View a day in April (spring)
3. View a day in July (summer)
4. View a day in October (autumn)

**Insights**:
- See how battery SOC evolves differently each season
- Identify worst-case months for grid dependency
- Understand when excess solar is available

### 3. Multi-Day Events
**Question**: "What happens during a week of cloudy weather?"

**Process**:
1. Manually reduce solar generation (future feature: weather data)
2. View consecutive days
3. Watch battery deplete over the week

**Insights**:
- Understand system resilience
- Plan for backup power needs
- Size battery for worst-case scenarios

### 4. Long-Term Trends
**Question**: "Does my battery reach equilibrium?"

**Process**:
1. View day 1, day 30, day 60, day 90
2. Observe SOC starting points

**Insights**:
- See if battery settles into a stable pattern
- Identify if system is balanced or imbalanced
- Understand seasonal cycles

---

## Advanced Features

### 1. Year-to-Year Comparison
Since the date picker allows 2024-2030:
- Compare the same day across different years
- Account for solar panel degradation (0.5%/year)
- Plan for future system performance

### 2. Configuration Experiments
Try different configurations:
- **Small battery** (5 kWh): See how often it hits minimum
- **Large battery** (20 kWh): See if it's worth the cost
- **Oversized solar** (15 kW): See excess export potential
- **Undersized solar** (5 kW): See grid dependency

### 3. Pattern Analysis
Compare different household patterns:
- **Working family**: Weekday vs weekend differences
- **Home office**: More consistent daily usage
- **Retired**: Different peak times
- **Student**: Irregular patterns

---

## Limitations & Future Enhancements

### Current Limitations
1. **Weather**: Uses average solar irradiance, not actual weather
2. **EV Charging**: Fixed daily pattern, not variable
3. **Appliances**: No modeling of specific large loads
4. **Grid Outages**: No simulation of backup power scenarios

### Planned Enhancements
1. **Weather Integration**: Import actual/forecast weather data
2. **Multi-Day View**: Show battery SOC curve over a week/month
3. **Equilibrium Analysis**: Calculate long-term average SOC
4. **Critical Days**: Identify worst-case days automatically
5. **Battery Health**: Model degradation over time
6. **Optimization**: Suggest optimal battery size based on SOC patterns

---

## Troubleshooting

### Issue: "Calculation takes a long time"
**Cause**: Viewing a day late in the year (e.g., December 31) for the first time

**Solution**: 
- The system must simulate all 365 days
- This takes ~15-20 seconds
- After the first time, it's instant (cached)
- View earlier days first to build cache gradually

### Issue: "Battery SOC seems wrong"
**Cause**: Configuration changed but cache not cleared

**Solution**:
- Click "Refresh Configuration" button
- This clears the cache and recalculates
- Or change any input parameter (auto-clears cache)

### Issue: "Different results than before"
**Cause**: SOC continuity now enabled (was always 50% before)

**Solution**:
- This is expected and more realistic
- To see "isolated day" behavior, view January 1st
- Or manually note the starting SOC in the graph

---

## Technical Details

### Battery Flow Algorithm
The simulation uses a priority-based energy flow:

**Surplus (Solar > Consumption)**:
1. Solar → Household (self-consumption)
2. Excess → Battery (until full)
3. Remaining → Grid (export)

**Deficit (Consumption > Solar)**:
1. Solar → Household (partial)
2. Battery → Household (until empty or demand met)
3. Grid → Household (remaining deficit)

### SOC Tracking
- **Initial SOC**: From previous day's final SOC
- **Hourly SOC**: Calculated after each hour's energy flow
- **Final SOC**: SOC at end of hour 23 (11:00 PM)
- **Next Day Initial**: Previous day's final SOC

### Efficiency Losses
Battery efficiency (95%) applies to:
- **Charging**: 5% loss when storing energy
- **Discharging**: 5% loss when retrieving energy
- **Round-trip**: ~90% (0.95 × 0.95)

These losses are properly accounted for in the SOC calculations.

---

## Validation

### Test Results
The SOC continuity feature has been validated with:

**Test 1: Winter Week**
- ✅ Battery depletes from 5.0 to 1.0 kWh
- ✅ Stabilizes at minimum SOC
- ✅ Grid import increases as battery depletes
- ✅ Self-sufficiency drops to 53-60%

**Test 2: Summer Week**
- ✅ Battery charges from 5.0 to 8.8 kWh
- ✅ Stays near-full throughout week
- ✅ Consistent grid export
- ✅ 100% self-sufficiency maintained

**Test 3: Cache Performance**
- ✅ First view of day 100: ~5 seconds
- ✅ Second view of day 100: < 1ms
- ✅ View of day 101: ~50ms (1 new day)
- ✅ View of day 50: < 1ms (cached)

---

## Conclusion

The Battery SOC Continuity feature transforms the PV Calculator from a single-day simulator into a realistic multi-day energy flow analyzer. This enables:

1. **Realistic Simulations**: Battery behavior matches real-world systems
2. **Better Planning**: Identify seasonal issues before installation
3. **Optimal Sizing**: Choose battery capacity based on actual usage patterns
4. **Long-term Analysis**: Understand system performance over weeks/months

The intelligent caching system ensures fast performance even when simulating hundreds of days, while automatic cache invalidation keeps results accurate when configuration changes.

---

**Version**: 2.7
**Date**: October 18, 2025
**Status**: Complete and tested ✅
**Test File**: `test_soc_continuity.py`

