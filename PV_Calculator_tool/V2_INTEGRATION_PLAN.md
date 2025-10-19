# V2 Integration Plan - Consolidated Analysis

## Changes Made

### 1. First Tab (Input Parameters) - Enhanced ✅
Added V2-specific inputs to the first tab so they're available for all analysis:

**Consumption Section:**
- ✅ Pattern Type dropdown (Working Family, Home Office, Retired, Student, Commercial)
- ✅ Seasonal Variation slider (0.0-0.5, default 0.2)  
- ✅ Updated description to explain V2 features

**PV System Section:**
- ✅ Location dropdown (10 European cities with auto-irradiance)
- ✅ Manual irradiance field (for backward compatibility)
- ✅ Panel Tilt Angle (0-90°, default 35°)

### 2. Consolidated V2 Tab - "Integrated Energy Analysis"
Replace the two separate V2 tabs with ONE unified tab:

**Name:** "⭐ Integrated Energy Analysis V2"

**Features:**
1. **Uses inputs from Tab 1** (no duplicate fields!)
2. **Consumption Analysis**
   - Generate consumption patterns
   - Show hourly/daily/monthly graphs

3. **Solar Generation Analysis**  
   - Calculate generation based on location
   - Show hourly/daily/monthly curves

4. **Battery Charging Analysis** (NEW!)
   - Hour-by-hour energy flow
   - Excess solar → Battery charging
   - Battery → Household (evening/night)
   - Grid import/export calculation

5. **Unified Visualizations:**
   - Daily: Consumption vs Generation vs Battery flow
   - Monthly: Energy balance with battery
   - Annual: Full year with self-sufficiency metrics
   - Excess/Deficit: Battery sizing recommendations

## Battery Charging Logic

### Hourly Energy Flow (Priority Order)

**During Solar Production (Day):**
1. Solar → Household consumption (direct use)
2. Excess solar → Battery charging (up to capacity)
3. Remaining excess → Grid export

**During No Solar (Night):**
1. Battery → Household (if battery has charge)
2. Grid → Household (if battery depleted)

**Calculation:**
```python
for each hour:
    generation = solar_pattern[hour]
    consumption = household_pattern[hour]
    
    if generation > consumption:
        # Surplus period
        self_use = consumption
        excess = generation - consumption
        
        # Charge battery
        if battery_soc < battery_capacity:
            charge = min(excess, battery_capacity - battery_soc)
            battery_soc += charge * battery_efficiency
            excess -= charge
        
        # Export to grid
        grid_export = excess
        grid_import = 0
        
    else:
        # Deficit period
        self_use = generation
        deficit = consumption - generation
        
        # Discharge battery
        if battery_soc > 0:
            discharge = min(deficit, battery_soc)
            battery_soc -= discharge / battery_efficiency
            deficit -= discharge
        
        # Import from grid
        grid_import = deficit
        grid_export = 0
```

### Battery Metrics
- **State of Charge (SoC)**: Track kWh in battery each hour
- **Charge cycles**: Count full charge/discharge cycles
- **Self-sufficiency**: % of consumption covered by solar + battery
- **Grid independence**: Hours per day without grid

## Implementation Steps

### Phase 1: Update First Tab ✅ DONE
- ✅ Add consumption pattern selector
- ✅ Add seasonal strength slider  
- ✅ Add location dropdown
- ✅ Add panel tilt angle

### Phase 2: Create Unified V2 Tab
- Replace `setup_consumption_v2_tab()` 
- Replace `setup_solar_v2_tab()`
- With: `setup_integrated_v2_tab()`

### Phase 3: Battery Flow Calculator
- Create `BatteryFlowCalculator` class
- Input: hourly generation, hourly consumption, battery specs
- Output: hourly battery SoC, grid flow, self-sufficiency

### Phase 4: New Visualizations
- Daily energy flow with battery
- Battery state of charge curve
- Grid dependency heatmap
- Monthly balance with battery

## Benefits

### User Experience
✅ **Single location** for all inputs (Tab 1)
✅ **Unified analysis** (one V2 tab instead of two)
✅ **Battery integration** (see how battery helps)
✅ **Complete picture** (consumption + solar + battery + grid)

### Technical
✅ **No duplicate fields** (DRY principle)
✅ **Consistent data** (all tools use same inputs)
✅ **Modular** (easy to add new analysis)
✅ **Maintainable** (one source of truth)

## User Workflow

1. **Configure in Tab 1:**
   - Consumption: 500 kWh/month, Working Family, 0.2 seasonal
   - PV: 5 kWp, Riga location, 35° tilt
   - Battery: 10 kWh capacity

2. **Analyze in V2 Tab:**
   - Click "Daily Energy Flow" → See hourly breakdown
   - Click "Battery Performance" → See SoC curves
   - Click "Monthly Balance" → See seasonal performance
   - Click "Annual Summary" → Get full year metrics

3. **Results:**
   - Self-sufficiency: 78% (up from 45% without battery!)
   - Battery cycles: 250/year
   - Grid export: 850 kWh/year
   - Grid import: 1320 kWh/year
   - Recommended battery size: 10-12 kWh ✓

## Next Steps

1. ✅ Add V2 inputs to Tab 1
2. ⏳ Create `BatteryFlowCalculator` class
3. ⏳ Build unified V2 tab interface
4. ⏳ Implement battery flow graphs
5. ⏳ Test with real scenarios

---

**Status**: Phase 1 Complete ✅  
**Next**: Implement battery flow calculator

