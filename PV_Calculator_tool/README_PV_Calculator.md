# PV System Feasibility Calculator

A comprehensive tool to calculate the economic feasibility of installing a photovoltaic (solar) system with or without battery storage.

## 🚨 IMPORTANT: Recent Critical Update (v2.2)

**If you have an Electric Vehicle and ran calculations before October 2025:**

- **Previous versions had a bug** where EV electricity costs were NOT included in the baseline cost
- This made PV systems appear unprofitable when they're actually profitable
- **Please re-run your analysis** with the updated version
- See [`URGENT_UPDATE_NOTICE.md`](URGENT_UPDATE_NOTICE.md) for details

**Impact:** Users with EVs may have been told their PV payback was 100+ years when it's actually 5-10 years!

## Features

- **Complete Cost Analysis**: Calculates current electricity costs including power charges, transmission, service fees, and VAT
- **PV System Sizing**: Estimates energy production based on system size and location
- **Battery Optimization**: Evaluates battery storage economics and self-sufficiency improvements
- **Nord Pool Integration**: Calculates revenue from selling excess energy to the grid
- **Financial Metrics**: ROI, NPV, payback period, and detailed cost comparisons
- **Visual Break-Even Analysis**: Interactive graphs showing when your investment pays for itself
- **Multiple Visualization Tools**: Cost comparisons, energy flow diagrams, ROI charts
- **Two Interfaces**: Command-line and graphical user interface (GUI)

## Installation

### Requirements

- Python 3.7 or higher
- Standard library only (no external dependencies for core calculator)
- tkinter for GUI (usually included with Python)

### Files

- `PV_calculator.py` - Core calculation engine
- `PV_calculator_gui.py` - Graphical user interface
- `README_PV_Calculator.md` - This file

## Usage

### 1. Command Line Interface (Quick Analysis)

Run the calculator with example values:

```bash
python PV_calculator.py
```

To customize, edit the `main()` function in `PV_calculator.py` with your values.

### 2. Graphical User Interface (Recommended)

Launch the GUI:

```bash
python PV_calculator_gui.py
```

#### GUI Features:

- **Input Parameters Tab**: Enter all your electricity tariff, consumption, PV system, and battery specifications
- **Results Tab**: View detailed analysis report
- **Graphs Tab**: Generate visual break-even analysis and other charts
  - Break-Even Analysis: See exactly when your investment pays for itself
  - Cost Comparison: Visual comparison of annual costs
  - Energy Flow: Understand your daily energy production and consumption
  - ROI Comparison: Compare return on investment metrics
- **Save/Load Configuration**: Save your parameters for later use
- **Export Results**: Export analysis report and graphs

### 3. Standalone Graph Generation

Generate graphs directly from command line:

```bash
python PV_calculator_graphs.py
```

This will create 4 graphs showing different aspects of the analysis.

## Input Parameters

### Electricity Tariff

- **Connected Power (A)**: Your connection capacity in Amperes (e.g., 25A, 35A)
- **Power Cost (EUR/A)**: Monthly cost per ampere of connected power
- **Electricity Cost (EUR/kWh)**: Base electricity price per kWh
- **Transfer Cost (EUR/kWh)**: Grid transmission/distribution cost
- **Service Cost (EUR/kWh)**: Electricity supply service cost
- **Monthly Service Fee (EUR)**: Fixed monthly service charge
- **VAT Rate (%)**: Value-added tax rate (default: 21%)

### Energy Consumption

- **Monthly Consumption (kWh)**: Your average monthly electricity consumption

### PV System

- **System Size (kWp)**: Peak power of the solar system in kilowatts
- **Installation Cost (EUR)**: Total cost including panels, inverter, installation
- **Solar Irradiance (kWh/m²/day)**: Average daily solar irradiance at your location
  - Central/Northern Europe: 2.5-3.5
  - Southern Europe: 4.0-5.0
  - You can find this data online for your specific location

### Battery Storage (Optional)

- **Battery Capacity (kWh)**: Total battery capacity
- **Battery Cost (EUR)**: Total cost including installation

### Nord Pool Pricing

- **Average Selling Price (EUR/kWh)**: Average price for selling excess energy
  - Check current Nord Pool spot prices for your region
  - Typically 0.04-0.10 EUR/kWh

## Understanding the Results

### Current Situation

- Shows your baseline electricity costs without any PV system
- Total annual and monthly costs
- Effective cost per kWh

### Scenario 1: PV System Without Battery

- Energy self-consumption and grid import
- Self-sufficiency ratio (% of consumption covered by PV)
- Annual costs and savings
- Financial analysis: payback period, ROI, NPV

### Scenario 2: PV System With Battery

- Improved self-sufficiency with battery storage
- Battery charging/discharging patterns
- Additional costs vs. additional savings
- Battery-specific payback period

### Recommendations

- Assessment of economic viability
- Comparison of scenarios
- Guidance on whether battery storage adds value

## Visualizations

The calculator generates four types of graphs to help you understand the economics:

### 1. Break-Even Analysis Graph

- **Top Chart**: Cumulative cash flow over 25 years
  - Shows initial investment as negative cash flow
  - Displays when cash flow crosses zero (break-even point)
  - Marks break-even year with annotation
  - Compares PV-only vs. PV+Battery scenarios
- **Bottom Chart**: Annual savings over time
  - Shows year-by-year savings
  - Accounts for system degradation
  - Includes battery replacement costs (if applicable)

### 2. Cost Comparison Graph

- Bar chart comparing annual electricity costs
- Shows current costs, PV-only costs, and PV+Battery costs
- Displays absolute savings in euros and percentage
- Color-coded for easy comparison

### 3. Energy Flow Graph

- Side-by-side comparison of PV-only vs. PV+Battery
- Stacked bar charts showing:
  - How consumption is covered (PV vs. Grid)
  - How PV production is used (Self-use vs. Sold to grid)
- Self-sufficiency ratio for each scenario

### 4. ROI Comparison Graph

- **Left Chart**: Investment breakdown pie chart
  - Shows proportion of costs (PV vs. Battery)
- **Right Chart**: Payback period comparison
  - Horizontal bar chart of payback periods
  - Reference lines for "excellent" and "good" investments

## Example Scenarios

### Small Residential (3kWp System)

- Monthly consumption: 300 kWh
- System size: 3 kWp
- Installation cost: €4,500
- Battery: 5 kWh, €3,000

### Medium Residential (5kWp System)

- Monthly consumption: 500 kWh
- System size: 5 kWp
- Installation cost: €7,000
- Battery: 7 kWh, €4,000

### Large Residential (8kWp System)

- Monthly consumption: 800 kWh
- System size: 8 kWp
- Installation cost: €10,000
- Battery: 10 kWh, €5,500

## Key Assumptions

The calculator uses the following assumptions (can be modified in the code):

1. **PV System**:

   - System efficiency: 85% (accounts for inverter and cable losses)
   - Annual degradation: 0.5% per year
   - System lifetime: 25 years

2. **Battery**:

   - Depth of discharge: 90% (usable capacity)
   - Round-trip efficiency: 95%
   - Lifetime: 10 years or 6,000 cycles

3. **Consumption Pattern**:

   - Default hourly pattern with peaks in morning and evening
   - Can be customized in `ConsumptionProfile` class

4. **Financial**:
   - Discount rate: 5% for NPV calculation
   - No consideration of inflation or changing electricity prices

## How PV Economics Work

### Self-Consumption

- Energy you produce and use directly = savings at full retail rate
- Most economically valuable use of solar energy

### Grid Export

- Excess energy sold to grid at Nord Pool prices
- Subject to transmission costs
- Typically much lower value than self-consumption

### Battery Value

- Increases self-consumption by storing excess daytime production
- Most valuable when there's large difference between:
  - Retail electricity price (what you pay)
  - Nord Pool price (what you get for excess)

### Payback Calculation

- Simple Payback = Initial Investment / Annual Savings
- NPV considers time value of money and system degradation
- Typical good payback period: 8-12 years

## Tips for Optimization

1. **Right-Size Your System**:

   - System producing 80-100% of your annual consumption is often optimal
   - Oversizing reduces economics due to low export prices

2. **Battery Economics**:

   - Battery payback often longer than PV system alone
   - Most economical when: high retail prices + low export prices
   - Consider adding battery later if prices drop

3. **Consumption Timing**:

   - Shift consumption to daytime when PV produces (washing, charging, etc.)
   - Improves economics without battery investment

4. **Get Multiple Quotes**:
   - Installation costs vary significantly
   - Lower costs = faster payback

## Customization

### Modifying Consumption Patterns

Edit the `hourly_pattern` in `ConsumptionProfile` class to match your actual usage.

### Adjusting PV Production Patterns

Edit the `pv_hourly_pattern` in `simulate_daily_energy_flow()` for your specific panel orientation.

### Real Nord Pool Prices

For production use, integrate real-time Nord Pool API data instead of using averages.

## Limitations

1. **Simplified Model**: Uses average daily values, not full year simulation
2. **No Seasonality**: Doesn't account for seasonal variation in production/consumption
3. **Fixed Prices**: Assumes constant electricity prices over project lifetime
4. **Average Solar Data**: Uses annual average, not monthly variations
5. **Standard Consumption**: Generic consumption patterns, not customized

## Future Enhancements

Potential improvements (contributions welcome):

- Monthly simulation with seasonal variations
- Real-time Nord Pool price integration
- Custom consumption profile import (from smart meter data)
- Multiple battery optimization algorithms
- Grid feed-in limitations (some regions have export limits)
- Detailed tax benefits and subsidies
- Comparison with financing options (loans vs. cash purchase)

## Support and Contribution

For questions, issues, or improvements:

1. Check the code comments for detailed explanations
2. The calculator is designed to be easily modified
3. All assumptions are documented in the code

## License

This tool is provided as-is for educational and planning purposes. Always consult with professional solar installers and financial advisors for actual installation decisions.

## Disclaimer

- Results are estimates based on assumptions
- Actual performance may vary based on:
  - Weather and location
  - System quality and installation
  - Actual consumption patterns
  - Future price changes
  - Maintenance and repairs
- Use this tool for preliminary feasibility assessment only
- Get professional quotes and analysis before making investment decisions

---

**Version**: 1.0  
**Last Updated**: October 2025
