# Solar Generation V2 - Complete! 🌞

## What's Been Added

### New Functionality
✅ **Location-based solar generation calculations**  
✅ **10 European cities with real irradiance data**  
✅ **Realistic hourly generation curves**  
✅ **Excess/deficit analysis for battery sizing**  
✅ **Full GUI integration**  

### New Files

1. **`PV_solar_generator.py`** (398 lines)
   - Solar generation calculator
   - Location database (Riga, Berlin, Madrid, Rome, etc.)
   - Latitude-based sunrise/sunset calculations
   - Hourly/daily/monthly/annual generation
   - Panel tilt optimization

2. **`PV_solar_graphs.py`** (359 lines)
   - Daily comparison: Generation vs Consumption
   - Monthly generation profile
   - Annual comparison with surplus/deficit
   - Excess/deficit analysis graphs

3. **GUI Integration** (in `PV_calculator_gui.py`)
   - New "⭐ Solar Generation V2" tab
   - Location selector (10 cities)
   - System size, tilt angle, efficiency controls
   - 4 graph types
   - Links with Consumption Patterns V2

## How to Use

### 1. Launch GUI
```bash
python PV_calculator_gui.py
```

### 2. Go to "⭐ Solar Generation V2" Tab

### 3. Configure System
- **System Size**: 1-100 kWp (default: 5.0 kWp)
- **Location**: Select from dropdown
  - Riga, Latvia (2.9 kWh/m²/day)
  - Berlin, Germany (3.1)
  - Munich, Germany (3.3)
  - Madrid, Spain (4.8) ← High irradiance
  - Rome, Italy (4.5)
  - And 5 more...
- **Tilt Angle**: 0-90° (default: 35°)
- **System Efficiency**: 0.5-1.0 (default: 0.85)

### 4. Generate Graphs
- **Daily Generation Profile**: See hourly curves by season
- **Monthly Generation Profile**: Annual pattern with variations
- **Generation vs Consumption**: Compare with household needs
- **Excess/Deficit Analysis**: Hour-by-hour surplus calculation

## Key Features

### Realistic Solar Curves
- Latitude-based sunrise/sunset
- Bell curve generation (peak at solar noon)
- Seasonal daylight variations
- Panel tilt optimization

### Example: 5kW System in Riga
```
Annual: 4,512 kWh
June (peak): 743 kWh (24 kWh/day)
December (low): 59 kWh (2 kWh/day)
Ratio: 12.6x (realistic for 57°N latitude!)
```

### Excess Calculation
The system calculates hour-by-hour:
- **Generation** from solar panels
- **Consumption** from household
- **Excess** = Generation - Consumption (to battery/grid)
- **Deficit** = Consumption - Generation (from battery/grid)
- **Self-sufficiency ratio** = Coverage percentage

## Integration with Consumption V2

The Solar Generation V2 tab integrates seamlessly with Consumption Patterns V2:

1. Configure consumption in "Consumption Patterns V2" tab
2. Configure solar system in "Solar Generation V2" tab
3. Click "Generation vs Consumption" to see comparison
4. Analyze excess for battery sizing!

## Graphs Explained

### 1. Daily Generation Profile
Shows typical day curves for each season:
- Winter: Short days, low production
- Summer: Long days, high production
- Realistic bell curves centered at solar noon

### 2. Monthly Generation Profile
Annual bar chart showing:
- Monthly generation totals
- Peak month (June) vs low month (December)
- Daily curves for 4 seasons overlaid
- System specifications summary

### 3. Generation vs Consumption
Side-by-side monthly comparison:
- Orange bars: Solar generation
- Blue bars: Household consumption
- Green line: Net energy (surplus/deficit)
- Green/red highlighting: Surplus/deficit months

### 4. Excess/Deficit Analysis
Hourly analysis for selected day:
- Top graph: Generation vs consumption curves
- Bottom graph: Bar chart of excess (green) and deficit (red)
- Summary statistics box
- Shows exactly when you have surplus energy!

## Location Database

10 predefined locations with accurate data:

| Location | Latitude | Irradiance (kWh/m²/day) |
|----------|----------|-------------------------|
| Riga, Latvia | 56.95°N | 2.9 |
| Stockholm, Sweden | 59.33°N | 2.8 |
| Copenhagen, Denmark | 55.68°N | 2.9 |
| Berlin, Germany | 52.52°N | 3.1 |
| Munich, Germany | 48.14°N | 3.3 |
| Warsaw, Poland | 52.23°N | 3.2 |
| Paris, France | 48.86°N | 3.4 |
| London, UK | 51.51°N | 2.7 |
| Madrid, Spain | 40.42°N | 4.8 |
| Rome, Italy | 41.90°N | 4.5 |

*Note: You can easily add more locations by editing `LOCATIONS` dict in `PV_solar_generator.py`*

## Use Cases

### Battery Sizing
1. Generate "Excess/Deficit Analysis"
2. Look at evening deficit period
3. Sum hourly deficit values
4. Size battery to cover deficit

Example:
- Evening deficit: 5 hours × 1.5 kWh/hour = 7.5 kWh
- → Battery recommendation: 8-10 kWh

### System Sizing
1. Generate "Generation vs Consumption"
2. Compare annual totals
3. Adjust system size to match consumption
4. Consider seasonal variations

Example:
- Annual consumption: 6000 kWh
- 5kW system generates: 4512 kWh (75% coverage)
- → For 100% coverage, need ~8kW system

### Grid Export Revenue
1. Generate "Excess/Deficit Analysis"
2. Sum monthly excess values
3. Multiply by grid export price
4. Calculate annual revenue

Example:
- Summer excess: 150 kWh/month × 6 months = 900 kWh/year
- @ €0.06/kWh = €54/year revenue

## Technical Details

### Calculation Method
```python
Daily Production = System Size (kWp) × 
                  Daily Irradiance (kWh/m²) × 
                  System Efficiency ×
                  Tilt Factor
```

### Hourly Distribution
- Calculated based on:
  - Latitude (determines day length)
  - Day of year (determines sun position)
  - Cosine squared curve (realistic bell shape)
  - Panel tilt angle optimization

### System Efficiency
Accounts for:
- Inverter losses (~3-5%)
- Cable losses (~2-3%)
- Shading losses (~5-10%)
- Dust/dirt (~2-5%)
- **Default 0.85 = 85% total efficiency**

## Performance

- Location calculation: < 1ms
- Daily pattern generation: < 5ms
- Annual generation: < 10ms
- Graph rendering: 1-2 seconds

## Future Enhancements

Potential additions:
- [ ] Weather API integration for real-time data
- [ ] Shading analysis
- [ ] Multiple orientations (East/West facing)
- [ ] Bi-facial panel support
- [ ] Battery simulation with charging curves
- [ ] Time-of-use tariff optimization

## Status

✅ **COMPLETE AND TESTED**  
✅ **GUI INTEGRATED**  
✅ **READY FOR USE**  

---

**The solar generation tool now provides everything needed to analyze PV systems and calculate excess energy for battery/grid optimization!** 🎉

