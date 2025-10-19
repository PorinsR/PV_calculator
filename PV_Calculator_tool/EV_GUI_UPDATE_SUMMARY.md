# EV Consumption GUI Feature - Update Summary

## Overview

**Update Date**: October 18, 2025  
**Feature**: EV consumption with charging schedule added to GUI  
**Integration**: Uses consumption data from Input Parameters tab

## What Was Added to GUI

### 1. Enhanced EV Section in Input Parameters Tab

#### New UI Elements

**Charging Days Selection** (Line ~393-406)
- 7 checkboxes for days of the week (Mon-Sun)
- Default: Monday-Friday checked
- Visual: Horizontal layout with day abbreviations

**Charging Hours Selection** (Line ~408-461)
- 24 checkboxes for each hour (00-23)
- Organized in 2 rows for better visibility
- Default: Overnight charging (22:00-06:00)

**Preset Buttons** (Line ~416-435)
- "Overnight (22-06)": 22:00-06:00 charging
- "Daytime Solar (11-15)": 11:00-15:00 charging (maximize solar)
- "Evening (18-23)": 18:00-23:00 charging

### 2. Backend Integration

#### New Imports (Line ~33)
```python
from PV_consumption_generator import EVConsumptionProfile
```

#### New Instance Variables (Line ~87)
```python
self.current_ev_consumption_profile = None
```

#### New Helper Method (Line ~604-621)
```python
def set_charging_hours_preset(self, preset):
    """Set charging hours based on preset buttons"""
```

#### Enhanced get_inputs() Method (Line ~1894-1922)
Creates `EVConsumptionProfile` with:
- Weekly distance (km)
- Consumption per 100km (kWh/100km)
- Charging days (list of booleans)
- Charging hours (list of integers)

#### Updated Configuration Methods
- **save_configuration()**: Saves charging days and hours (Line ~2010-2011)
- **load_configuration()**: Restores charging days and hours (Line ~2095-2111)

#### Enhanced get_v2_profile() Method (Line ~955-957)
Automatically adds EV profile to household profile when generating consumption patterns.

### 3. User Workflow

```
1. Input Parameters Tab
   ├── Enable EV Charging checkbox
   ├── Select car make/model (auto-fills consumption)
   ├── Enter weekly distance
   ├── Select charging days (Mon-Sun)
   └── Select charging hours (00-23) or use presets
   
2. Click "Calculate"
   ├── Creates EVConsumptionProfile
   ├── Attaches to household profile
   └── Used in all consumption graphs
   
3. Energy Flow Analysis Tab
   └── Consumption patterns include EV charging
```

## Features

### ✅ Flexible Charging Schedules

**Example 1: Overnight Charging (Default)**
- Days: Mon-Fri
- Hours: 22:00-06:00
- Use case: Cheap nighttime rates

**Example 2: Solar Optimized**
- Days: Any
- Hours: 11:00-15:00
- Use case: Maximize solar self-consumption

**Example 3: Weekend Only**
- Days: Sat-Sun
- Hours: 10:00-16:00
- Use case: Light weekly usage

### ✅ Integration with Consumption V2

The EV profile is automatically:
- Added to household profiles
- Included in all consumption graphs
- Tracked separately (household vs EV)
- Used in annual calculations

### ✅ Persistent Configuration

Charging days and hours are:
- Saved to `pv_calculator_config.json`
- Restored on application startup
- Preserved across sessions

## Technical Details

### Data Flow

```
GUI Input Fields
    ↓
EVConsumptionProfile (V2)
    ↓
HouseholdProfile.ev_profile
    ↓
ConsumptionPatternGenerator
    ↓
Consumption Graphs & Analysis
```

### EV Profile Creation (Line ~1916-1922)

```python
ev_consumption_profile = EVConsumptionProfile(
    enabled=True,
    weekly_distance_km=weekly_km,
    consumption_per_100km=efficiency,
    charging_days=charging_days,      # from checkboxes
    charging_hours=charging_hours     # from checkboxes
)
```

### Integration Point (Line ~955-957)

```python
# In get_v2_profile()
if hasattr(self, 'current_ev_consumption_profile') and self.current_ev_consumption_profile:
    profile.ev_profile = self.current_ev_consumption_profile
```

## Usage Examples

### Example 1: Weekday Commuter

**Setup:**
1. Enable EV Charging ✓
2. Select car: Tesla Model 3 (2024) → 14.4 kWh/100km
3. Weekly distance: 300 km
4. Charging days: Mon, Tue, Wed, Thu, Fri ✓
5. Charging hours: Click "Overnight (22-06)" button

**Result:**
- 54 kWh per week
- 10.8 kWh per charging day (Mon-Fri)
- 1.2 kWh per hour during charging
- 2,808 kWh per year

### Example 2: Solar Optimizer

**Setup:**
1. Enable EV Charging ✓
2. Select car: VW ID.4 (2024) → 17.3 kWh/100km
3. Weekly distance: 200 km
4. Charging days: Mon, Tue, Wed, Thu, Fri ✓
5. Charging hours: Click "Daytime Solar (11-15)" button

**Result:**
- 34.6 kWh per week
- 6.92 kWh per weekday
- 1.38 kWh per hour (11:00-15:00)
- Charges during peak solar production
- Maximum self-consumption

### Example 3: Weekend Road Tripper

**Setup:**
1. Enable EV Charging ✓
2. Select car: BMW iX (2024) → 19.4 kWh/100km
3. Weekly distance: 400 km (weekend trips)
4. Charging days: Sat, Sun ✓
5. Charging hours: 10-16 (select hours 10-16)

**Result:**
- 77.6 kWh per week
- 38.8 kWh per weekend day
- 5.54 kWh per hour (10:00-16:00)
- Weekend-focused charging

## Benefits

### For Users

✅ **Intuitive Interface**: Visual selection of charging days and hours  
✅ **Quick Presets**: One-click common charging patterns  
✅ **Realistic Modeling**: Accurate representation of actual charging behavior  
✅ **Flexible Scheduling**: Any combination of days and hours  
✅ **Persistent Settings**: Configuration saved automatically

### For Analysis

✅ **Separate Tracking**: Household vs EV consumption  
✅ **Hourly Detail**: See exactly when EV charges  
✅ **Solar Optimization**: Model charging during solar production  
✅ **Battery Sizing**: Calculate battery needs including EV  
✅ **Cost Analysis**: Compare grid vs solar charging costs

## Files Modified

### PV_calculator_gui.py

**Lines Added/Modified**: ~150 lines

**Key Sections:**
1. Import statement (Line ~33)
2. UI elements for charging days/hours (Line ~392-467)
3. Preset button method (Line ~604-621)
4. EV profile creation in get_inputs() (Line ~1894-1922)
5. Profile integration in get_v2_profile() (Line ~955-957)
6. Configuration save/load (Line ~2010-2011, ~2095-2111)
7. Initialization (Line ~87)

## Testing

### Manual Test Steps

1. **Start Application**
   ```bash
   python3 PV_calculator_gui.py
   ```

2. **Configure EV**
   - Go to "Input Parameters" tab
   - Check "Include EV Charging"
   - Select a car or enter consumption
   - Enter weekly distance (e.g., 300 km)
   - Select charging days (e.g., Mon-Fri)
   - Click "Overnight (22-06)" preset

3. **View Results**
   - Go to "Energy Flow Analysis" tab
   - Click any graph button
   - Observe EV consumption in graphs
   - Check statistics include EV totals

4. **Test Persistence**
   - Click "Save Configuration"
   - Close application
   - Restart application
   - Verify EV settings restored

### Expected Behavior

✅ Charging days checkboxes respond correctly  
✅ Charging hours checkboxes respond correctly  
✅ Preset buttons update hour checkboxes  
✅ EV consumption appears in graphs  
✅ Statistics show household + EV breakdown  
✅ Configuration saves and loads properly

## Known Limitations

1. **Uniform Distribution**: EV energy distributed evenly across selected hours
   - Real chargers may have variable charging curves
   - Future: Support for charging power profiles

2. **Same Schedule Daily**: All selected days use same hours
   - Real users may charge at different times different days
   - Workaround: Use average schedule

3. **No Charge Interruption**: Assumes continuous charging during selected hours
   - Real charging may be interrupted
   - Future: Model partial charging sessions

## Troubleshooting

### Issue: Preset buttons don't work

**Solution**: Ensure checkboxes are initialized. Check `self.ev_charging_hours` exists.

### Issue: EV not appearing in graphs

**Solution**:
1. Ensure "Include EV Charging" is checked
2. Click "Calculate" button first
3. Check that consumption V2 is available
4. Verify weekly distance > 0

### Issue: Configuration not saving charging hours

**Solution**: Check file permissions for `pv_calculator_config.json`

### Issue: No charging hours selected

**System behavior**: Defaults to overnight charging (22:00-06:00)

## Future Enhancements

Planned for next versions:

- [ ] Visual time range slider for charging hours
- [ ] Different charging schedules per day
- [ ] Smart charging optimization algorithm
- [ ] Time-of-use rate visualization
- [ ] Vehicle-to-Grid (V2G) support
- [ ] Multiple vehicles per household
- [ ] Charging session history tracking

## Documentation

Related documentation files:

- **README_EV_FEATURE.md**: Main overview
- **EV_CONSUMPTION_QUICKSTART.md**: Quick start guide  
- **EV_CONSUMPTION_FEATURE.md**: Complete API documentation
- **EV_UPDATE_SUMMARY.md**: Backend changes
- **example_ev_usage.py**: Code examples

## Summary

The GUI now provides a complete, user-friendly interface for configuring EV charging patterns. Users can:

1. ✅ Select charging days (which days to charge)
2. ✅ Select charging hours (when to charge)
3. ✅ Use quick presets for common scenarios
4. ✅ See EV consumption in all graphs
5. ✅ Save and load configurations
6. ✅ Get accurate annual projections

All features integrate seamlessly with the existing consumption pattern generator, providing realistic EV charging simulation based on actual user behavior.

---

**Ready to use?** Open the GUI and configure your EV charging schedule in the Input Parameters tab!

**Need help?** See the documentation files listed above for detailed guides and examples.

