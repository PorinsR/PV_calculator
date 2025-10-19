# Consumption Pattern Generator V2 - User Guide

## Overview

The **Consumption Pattern Generator V2** is a powerful tool integrated into the PV Calculator that generates and visualizes realistic daily power consumption patterns. It helps you understand how different household types consume electricity throughout the day, week, and year.

## Key Features

### 1. Gaussian Seasonal Distribution
- Models higher consumption in autumn/winter months
- Peak consumption in January (winter heating)
- Lowest consumption in July (summer)
- Realistic 3-4x variation between peak and low months

### 2. Realistic Daily Patterns
- **Workday patterns**: Low during day (people away), peak in evening
- **Weekend patterns**: Higher daytime consumption (more at-home activities)
- **Time-of-day variation**: Night baseline, morning rush, evening peak

### 3. Multiple Household Types

#### Working Family
- Adults working outside home during day
- Peak consumption in evening (18:00-21:00)
- Low daytime consumption (away at work)
- Best for: Traditional family households

#### Home Office
- One or more adults working from home
- Consistent daytime consumption
- Moderate evening peak
- Best for: Remote workers, freelancers

#### Retired Couple
- At home most of the day
- Steady consumption throughout day
- Lower evening peak
- Best for: Retired households

#### Student Apartment
- Irregular schedule
- Lower overall consumption
- Evening peak
- Best for: Young adults, students

#### Small Commercial
- Daytime operation (06:00-18:00)
- Low overnight consumption
- More consistent year-round
- Best for: Small businesses, shops

## How to Use

### Step 1: Access the Feature
1. Run the PV Calculator GUI: `python PV_calculator_gui.py`
2. Navigate to the **"⭐ Consumption Patterns V2"** tab

### Step 2: Configure Pattern
1. **Select Pattern Type**: Choose from dropdown menu
2. **Set Annual Consumption**: Enter total yearly consumption in kWh
3. **Adjust Seasonal Strength**: 
   - 0.0 = Flat (no seasonal variation)
   - 0.5 = Moderate variation
   - 1.0 = Strong variation (winter 3x summer)
4. **Set Peak Evening Hour**: Typical is 19:00 (7 PM)
5. **Choose Heatmap Month**: For weekly visualization

### Step 3: Generate Visualizations

#### Available Graphs:

##### 1. Daily Pattern Comparison
- Compares weekday vs weekend patterns
- Shows winter (January) and summer (July) side by side
- Identifies evening peak hours
- Highlights time periods (night, morning, evening)

##### 2. Seasonal Variation
- Monthly total consumption with Gaussian curve overlay
- Daily average consumption (weekday vs weekend)
- Highlights winter months
- Shows seasonal multipliers

##### 3. Weekly Heatmap
- 24 hours × 7 days consumption heatmap
- Color-coded intensity (yellow to red)
- Highlights weekends
- Shows exact hourly values

##### 4. Pattern Type Comparison
- Compares multiple household types side by side
- Shows weekday, weekend, summer patterns
- Monthly consumption comparison
- Helps choose the right pattern

##### 5. Annual Overview
- Comprehensive year analysis
- Monthly totals with peak/low highlighting
- Daily consumption over 365 days
- Statistics summary
- Day-of-week averages

##### 6. Generate All V2 Graphs
- Creates all graphs at once
- Saves as PNG files with timestamp
- Shows the final graph
- Perfect for reports and presentations

## Technical Details

### Gaussian Curve Implementation
The seasonal variation uses a Gaussian (normal) distribution centered on January (winter peak):

```
Seasonal Multiplier = min + (max - min) × Gaussian(distance_from_peak)
```

- **Peak**: January (1.6x average)
- **Minimum**: July (0.4x average)  
- **Sigma**: 2.5 months (realistic spread)

### Daily Pattern Calculation
```
Hourly Consumption = Base Daily × Hourly Fraction × Seasonal Factor × Day-of-Week Factor
```

Where:
- **Base Daily**: Annual consumption / 365
- **Hourly Fraction**: Pre-defined 24-hour pattern (sums to 1.0)
- **Seasonal Factor**: Monthly Gaussian multiplier
- **Day-of-Week Factor**: Weekend typically 1.15x weekday

### Weekend Adjustment
Weekend patterns automatically adjust:
- Morning consumption shifted later by 1-2 hours
- Midday consumption increased by 30%
- Evening peak slightly reduced
- Reflects typical at-home weekend behavior

## Example Use Cases

### Use Case 1: Solar System Sizing
1. Select "Working Family" pattern
2. Set annual consumption to your yearly usage
3. Generate "Daily Pattern Comparison" graph
4. Identify when you consume most (evening)
5. Compare against PV production curves
6. Size system to match consumption

### Use Case 2: Battery Sizing
1. Generate "Weekly Heatmap" for winter (January)
2. Identify evening peak consumption period
3. Calculate battery capacity needed to cover evening deficit
4. Compare summer vs winter requirements
5. Choose optimal battery size

### Use Case 3: Tariff Optimization
1. Generate "Annual Overview"
2. Identify high-consumption months
3. Plan for time-of-use tariffs
4. Optimize charging strategies
5. Estimate savings potential

### Use Case 4: Behavioral Analysis
1. Compare your pattern against different types
2. Generate "Pattern Type Comparison"
3. Identify if you match typical profiles
4. Find optimization opportunities
5. Plan consumption shifts

## Integration with PV Calculator V1

The V2 consumption patterns are **standalone** but can inform your V1 calculations:

1. Use V2 to understand your consumption profile
2. Set V1 monthly consumption based on V2 annual total
3. V1 already includes day-wise patterns (weekday/weekend)
4. V2 provides deeper insights for decision-making
5. Both tools work together seamlessly

## File Outputs

When you generate graphs, files are saved with timestamps:
```
Consumption_V2_daily_comparison_20251018_143022.png
Consumption_V2_seasonal_20251018_143022.png
Consumption_V2_heatmap_20251018_143022.png
Consumption_V2_pattern_comparison_20251018_143022.png
Consumption_V2_annual_overview_20251018_143022.png
```

- **High resolution**: 300 DPI for print quality
- **PNG format**: Universal compatibility
- **Timestamped**: Never overwrite previous analyses
- **Professional**: Ready for reports and presentations

## Tips and Best Practices

### 1. Accurate Annual Consumption
- Use your actual yearly electricity bills
- Include all consumption (heating, cooling, appliances)
- For new homes, estimate based on size and appliances

### 2. Choosing Pattern Type
- **Working Family**: Both adults work outside, kids at school
- **Home Office**: At least one person home during day
- **Retired**: Home most of the time
- **Student**: Irregular schedule, lower usage
- **Commercial**: Business hours operation

### 3. Seasonal Strength
- **0.4-0.6**: Electric heating or cooling
- **0.3-0.4**: Moderate seasonal variation
- **0.1-0.2**: Well-insulated, minimal HVAC
- **0.0**: No seasonal variation (very rare)

### 4. Peak Hour Adjustment
- **18:00-20:00**: Typical for most households
- **Later (21:00-22:00)**: Younger households
- **Earlier (17:00-18:00)**: Families with young children

### 5. Combining with EV Charging
- V2 shows household consumption only
- Use V1 to analyze combined household + EV
- V2 helps identify optimal EV charging times
- Plan to charge during low-consumption hours

## Troubleshooting

### Issue: Graphs not displaying
**Solution**: Ensure matplotlib and numpy are installed:
```bash
pip install matplotlib numpy
```

### Issue: Pattern doesn't match my usage
**Solution**: 
- Try different pattern types
- Adjust seasonal strength
- Modify peak evening hour
- Consider creating custom pattern in code

### Issue: Annual total doesn't match input
**Solution**: Small variations are normal due to:
- Weekend/weekday distribution (not exactly 52 weeks)
- Day-of-week factors
- Rounding in calculations
- Typically within 2-3% of target

### Issue: Peak/low month ratio too extreme
**Solution**:
- Reduce seasonal strength slider
- Typical realistic range: 2x to 4x
- If you have electric heating: 3x-5x
- Well-insulated homes: 1.5x-2x

## Advanced Features

### Programmatic Access

You can use the generator directly in Python:

```python
from PV_consumption_generator import ConsumptionPatternGenerator

generator = ConsumptionPatternGenerator()

profile = generator.create_household_profile(
    name="My Home",
    annual_consumption_kwh=6000,
    pattern_type='working_family',
    seasonal_strength=0.6,
    peak_hour=19
)

# Get specific values
jan_consumption = generator.get_daily_consumption(profile, 1, True)
evening_hour = generator.get_hourly_consumption(profile, 1, 0, 19)

# Generate full year
year_data = generator.generate_year_consumption(profile)
```

### Custom Patterns

You can modify or add custom patterns in `PV_consumption_generator.py`:

```python
PATTERNS = {
    'my_custom_pattern': {
        'name': 'My Custom Pattern',
        'description': 'Custom consumption pattern',
        'base_pattern': [0.02, 0.01, ...],  # 24 hourly values
        'winter_peak': True
    }
}
```

## Future Enhancements

Planned features:
- Import consumption data from CSV
- Machine learning to detect pattern from historical data
- Time-of-use tariff optimization
- Integration with smart home systems
- Real-time consumption tracking

## Support and Feedback

- Report issues in the GitHub repository
- Suggest new household patterns
- Share your consumption insights
- Contribute improvements

## Version History

**Version 2.0** (October 2025)
- Initial release
- 5 household pattern types
- Gaussian seasonal distribution
- 5 visualization types
- Full GUI integration

---

**Note**: This is an analysis tool. Actual consumption may vary based on many factors including weather, occupancy, appliances, and behavior. Use these patterns as guidelines for solar system planning and optimization.

