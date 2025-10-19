# Unified Energy Flow Analysis V2 - Complete Implementation

## Overview

This document describes the implementation of three major components for the PV Calculator:

1. **Battery Flow Calculator** - Simulates hour-by-hour energy storage and discharge
2. **Integrated Energy Graphs** - Comprehensive visualizations combining all energy flows
3. **Unified V2 Tab** - GUI interface integrating all V2 features

## 1. Battery Flow Calculator (`PV_battery_flow.py`)

### Purpose
Simulates realistic battery behavior in a solar + storage system, calculating:
- Charging/discharging patterns
- State of charge (SOC) over time
- Grid import/export after battery
- Self-sufficiency metrics

### Key Features

#### Energy Flow Priority
```
Solar Generation →  1. Household Consumption
                   2. Battery Charging (if excess)
                   3. Grid Export (if still excess)

Consumption Need → 1. Solar Generation
                  2. Battery Discharge
                  3. Grid Import (if needed)
```

#### Battery Parameters
- **Capacity**: Total storage in kWh
- **Efficiency**: Round-trip efficiency (typically 90-95%)
- **Max Charge/Discharge Rate**: Power limits in kW
- **Minimum SOC**: Reserve capacity (typically 10%)

### Class: `BatteryFlowCalculator`

```python
from PV_battery_flow import BatteryFlowCalculator

# Create calculator
battery = BatteryFlowCalculator(
    battery_capacity_kwh=10.0,      # 10 kWh battery
    battery_efficiency=0.95,         # 95% round-trip
    max_charge_rate_kw=5.0,         # Optional power limit
    min_soc_percent=10.0            # Keep 10% reserve
)

# Simulate a day
result = battery.simulate_hourly_flow(
    hourly_consumption=[0.5, 0.4, ...],  # 24 values
    hourly_generation=[0.0, 0.0, 2.5, ...],  # 24 values
    initial_soc=5.0  # Start at 50%
)
```

### Output: `BatteryFlowResult`

Contains hourly arrays and summary metrics:

**Hourly Arrays** (24 or 8760 values):
- `hourly_consumption` - Energy consumed
- `hourly_generation` - Solar produced
- `hourly_battery_soc` - State of charge
- `hourly_battery_charge` - Charging power
- `hourly_battery_discharge` - Discharging power
- `hourly_grid_import` - From grid
- `hourly_grid_export` - To grid
- `hourly_self_consumption` - Locally used solar

**Summary Metrics**:
- `total_consumption` - Total kWh consumed
- `total_generation` - Total kWh generated
- `total_grid_import` - Total kWh from grid
- `total_grid_export` - Total kWh to grid
- `total_self_consumption` - Total kWh self-consumed
- `battery_cycles` - Full charge/discharge cycles
- `self_sufficiency_ratio` - % consumption met without grid (with battery)
- `self_consumption_ratio` - % solar used locally (not exported)
- `battery_throughput` - Total kWh through battery

### Example Output

```
Battery: 10.0 kWh
Daily consumption: 13.1 kWh
Daily generation: 31.6 kWh

RESULTS
-------------------------
Self-consumption: 12.7 kWh (40.3%)
Grid import: 0.4 kWh
Grid export: 18.7 kWh
Self-sufficiency: 97.2%
Battery cycles: 0.72
```

## 2. Integrated Energy Graphs (`PV_integrated_graphs.py`)

### Purpose
Creates comprehensive visualizations combining consumption, solar generation, battery flow, and grid interactions.

### Class: `IntegratedEnergyGraphs`

```python
from PV_integrated_graphs import IntegratedEnergyGraphs
from PV_consumption_generator import ConsumptionPatternGenerator, HouseholdProfile
from PV_solar_generator import SolarGenerationCalculator, SolarSystemProfile, LOCATIONS
from PV_battery_flow import BatteryFlowCalculator

# Create components
consumption_gen = ConsumptionPatternGenerator()
solar_gen = SolarGenerationCalculator()
battery_calc = BatteryFlowCalculator(battery_capacity_kwh=10.0)

household = HouseholdProfile(
    name='My Family',
    annual_consumption_kwh=5000,
    pattern_type='working_family',
    seasonal_strength=0.2,
    peak_evening_hour=19
)

solar_system = SolarSystemProfile(
    name='My System',
    peak_power_kw=6.0,
    location=LOCATIONS['riga_latvia'],
    tilt_angle=35.0,
    system_efficiency=0.85
)

# Create graph generator
graph_gen = IntegratedEnergyGraphs(
    consumption_gen, solar_gen, battery_calc,
    household, solar_system
)
```

### Available Visualizations

#### 1. Daily Energy Flow
```python
fig = graph_gen.plot_daily_energy_flow(month=6, day_of_week=0)
```

Shows 4 subplots:
1. **Consumption vs Generation** - Hourly patterns overlaid
2. **Battery State** - SOC throughout the day
3. **Battery Charge/Discharge** - Power flow in/out
4. **Grid Import/Export** - Grid interaction

Includes daily summary metrics box.

#### 2. Weekly Comparison
```python
fig = graph_gen.plot_weekly_comparison(month=6)
```

Compares Mon-Sun with 3 subplots:
1. **Daily Totals** - Consumption, generation, self-consumption bars
2. **Self-Sufficiency** - Percentage by day
3. **Grid Flows** - Import/export by day

Perfect for understanding weekday vs weekend patterns.

#### 3. Seasonal Comparison
```python
fig = graph_gen.plot_seasonal_comparison(months=[1, 4, 7, 10])
```

Shows 3x2 grid (up to 6 months) with:
- Hourly generation and consumption curves
- Battery SOC overlay
- Key metrics in text boxes

Great for understanding seasonal variations.

#### 4. Annual Summary
```python
fig = graph_gen.plot_annual_summary()
```

Comprehensive 12-month overview with 6 subplots:
1. **Monthly Energy Totals** - Consumption, generation, self-consumption
2. **Self-Sufficiency Ratio** - Monthly % values
3. **Grid Import/Export** - Monthly totals
4. **Energy Balance** - Net generation - consumption
5. **Cumulative Energy Flows** - Year-to-date totals
6. **Annual Summary Metrics** - Text summary with key numbers

Estimates based on representative weekday/weekend simulation.

### Graph Features

All graphs include:
- Professional styling with clear legends
- Color coding (orange=solar, blue=consumption, green=battery/self-suff)
- Metrics annotations
- High-resolution output (150 DPI default)
- Proper date/time formatting
- Grid lines for readability

## 3. Unified V2 Tab (GUI Integration)

### Location
**Tab 7**: "🔋 Unified Energy Flow V2"

### Purpose
Single interface for complete energy system analysis without switching between tabs.

### Configuration Sections

#### A. System Configuration
Informational note that PV and battery specs can be pulled from Tab 1 (future enhancement).

#### B. Household Consumption Profile
- **Pattern Type**: Working family, home office, retired, student, small business
- **Annual Consumption**: Total kWh per year
- **Seasonal Variation**: Strength 0.0-0.5 (default 0.2)
- **Evening Peak Hour**: 0-23 (default 19:00)

#### C. Solar System Configuration
- **System Size**: 1-100 kWp (default 6.0)
- **Location**: 10 European cities with irradiance data
- **Panel Tilt**: 0-90° (default 35°)
- **System Efficiency**: 0.5-1.0 (default 0.85)

#### D. Battery Configuration
- **Battery Capacity**: 0-100 kWh (default 10.0)
- **Round-trip Efficiency**: 0.8-1.0 (default 0.95)
- **Minimum SOC**: 0-50% (default 10%)

### Available Visualizations

5 buttons for different graph types:

1. **Daily Energy Flow** → `show_unified_daily_flow()`
   - Complete 24-hour analysis
   - 4-panel view with all metrics

2. **Weekly Comparison** → `show_unified_weekly_comparison()`
   - Mon-Sun comparison
   - Shows weekday vs weekend differences

3. **Seasonal Comparison** → `show_unified_seasonal_comparison()`
   - Jan, Apr, Jul, Oct by default
   - Understanding annual variation

4. **Annual Summary** → `show_unified_annual_summary()`
   - Comprehensive 12-month overview
   - Takes longer to generate

5. **Generate All Reports** → `show_unified_all_graphs()`
   - Creates all 4 graph types
   - Saves to PNG files with timestamp
   - Shows success message with filenames

### Graph Output

Graphs are:
- Displayed interactively (matplotlib window)
- Can be saved manually from the window
- "Generate All Reports" auto-saves with timestamp

Example filenames:
```
Unified_Daily_Flow_20251018_143022.png
Unified_Weekly_Comparison_20251018_143022.png
Unified_Seasonal_Comparison_20251018_143022.png
Unified_Annual_Summary_20251018_143022.png
```

## Use Cases

### 1. System Sizing
**Question**: What battery size do I need for 80% self-sufficiency?

**Process**:
1. Go to Unified V2 tab
2. Set your consumption pattern and annual kWh
3. Set your planned solar system size
4. Try different battery capacities (5, 10, 15 kWh)
5. Click "Annual Summary" each time
6. Compare "Avg Self-Sufficiency" values

### 2. Location Comparison
**Question**: How much better is solar in Munich vs Stockholm?

**Process**:
1. Set your consumption and battery specs
2. Set solar size
3. Choose "Stockholm" → "Annual Summary"
4. Note total generation and self-sufficiency
5. Choose "Munich" → "Annual Summary"
6. Compare results

### 3. Seasonal Planning
**Question**: Will I need grid power in winter?

**Process**:
1. Configure your actual system
2. Click "Seasonal Comparison"
3. Look at January (month 1) subplot
4. Check "Import" value in metrics box
5. See hourly grid import pattern

### 4. Consumption Pattern Impact
**Question**: How does home office vs office work affect self-sufficiency?

**Process**:
1. Set "Working Family" pattern
2. Click "Weekly Comparison"
3. Note weekday self-sufficiency
4. Change to "Home Office"
5. Click "Weekly Comparison" again
6. Compare - home office typically higher (daytime solar use)

### 5. Complete Analysis Report
**Question**: I need a full report for my installer/bank.

**Process**:
1. Configure your exact system specs
2. Click "Generate All Reports"
3. Wait for completion (1-2 minutes)
4. Get 4 professional PNG files
5. Include in your documentation

## Technical Details

### Performance
- **Daily simulation**: < 1 second
- **Weekly simulation**: ~1 second (7 days)
- **Seasonal comparison**: ~2 seconds (4-6 months)
- **Annual summary**: ~5-10 seconds (12 months × weekday/weekend)

### Accuracy
- Hourly granularity for all calculations
- Realistic battery efficiency losses
- Seasonal solar variation based on location data
- Consumption patterns validated against real data

### Dependencies
```
numpy          # Numerical operations
matplotlib     # Visualization
PyQt5          # GUI framework
```

All included in existing `requirements.txt`.

## File Structure

```
PV_Calculator_tool/
├── PV_battery_flow.py           # Battery simulation engine
├── PV_integrated_graphs.py      # Visualization generator
├── PV_calculator_gui.py         # GUI with unified tab (updated)
├── PV_consumption_generator.py  # Consumption patterns (existing)
├── PV_solar_generator.py        # Solar generation (existing)
└── ...
```

## Module Availability

The GUI checks for module availability:
- If `PV_battery_flow.py` missing → Tab shows warning
- If `PV_integrated_graphs.py` missing → Tab shows warning
- If both present → Full functionality enabled

Check `INTEGRATED_V2_AVAILABLE` flag at GUI startup.

## Example Session

```python
# Console test (without GUI)
from PV_battery_flow import BatteryFlowCalculator
from PV_integrated_graphs import IntegratedEnergyGraphs
from PV_consumption_generator import ConsumptionPatternGenerator, HouseholdProfile
from PV_solar_generator import SolarGenerationCalculator, SolarSystemProfile, LOCATIONS

# Setup
consumption_gen = ConsumptionPatternGenerator()
solar_gen = SolarGenerationCalculator()
battery_calc = BatteryFlowCalculator(battery_capacity_kwh=10.0)

household = HouseholdProfile(
    name='Test', annual_consumption_kwh=5000,
    pattern_type='working_family', seasonal_strength=0.2,
    peak_evening_hour=19
)

solar_system = SolarSystemProfile(
    name='Test', peak_power_kw=6.0,
    location=LOCATIONS['riga_latvia'],
    tilt_angle=35.0, system_efficiency=0.85
)

# Generate
graph_gen = IntegratedEnergyGraphs(
    consumption_gen, solar_gen, battery_calc,
    household, solar_system
)

# Show daily flow for June Monday
fig = graph_gen.plot_daily_energy_flow(month=6, day_of_week=0)
fig.savefig('my_energy_flow.png', dpi=150, bbox_inches='tight')
fig.show()
```

## Future Enhancements

### Possible Additions
1. **Cost Analysis Integration**
   - Pull tariffs from Tab 1
   - Calculate grid cost savings
   - Show ROI metrics

2. **EV Charging Integration**
   - Add EV consumption to household
   - Smart charging optimization
   - Peak shaving analysis

3. **Grid Tariff Optimization**
   - Time-of-use rate comparison
   - Best charging/discharging times
   - Dynamic pricing scenarios

4. **Real Data Import**
   - Load actual consumption data
   - Compare with patterns
   - Calibrate models

5. **Export Features**
   - PDF report generation
   - Excel data export
   - CSV hourly data

6. **Advanced Battery Models**
   - Degradation over time
   - Temperature effects
   - Different battery chemistries

## Troubleshooting

### "Module not available" warning
**Cause**: File missing or import error
**Solution**: 
1. Check files exist in `PV_Calculator_tool/`
2. Run: `python PV_battery_flow.py` to test
3. Run: `python PV_integrated_graphs.py` to test
4. Check for syntax errors

### Graphs not showing
**Cause**: matplotlib backend issue
**Solution**:
1. Check matplotlib installed: `pip install matplotlib`
2. Try interactive mode: `plt.ion()` before showing
3. Use `fig.savefig()` as alternative

### Slow annual summary
**Cause**: Simulating 24 representative days
**Solution**: 
- This is normal, 5-10 seconds expected
- Consider caching results for same config
- Use other graphs for quick checks

### Battery never fully charges
**Cause**: Generation < consumption + losses
**Solution**:
- Increase solar system size
- Reduce consumption
- Check seasonal month (winter has less sun)
- Verify system efficiency setting

## Summary

The Unified Energy Flow Analysis V2 brings together:
- ✅ Realistic battery simulation
- ✅ Comprehensive visualizations
- ✅ Easy-to-use GUI interface
- ✅ Professional-grade graphs
- ✅ Complete system analysis

All accessible from a single tab with intuitive controls and instant visual feedback.

---

**Implementation Date**: October 18, 2025
**Version**: 2.0
**Status**: Complete and tested

