# PV System Feasibility Calculator - Web Version

A comprehensive web-based tool for analyzing photovoltaic (PV) system feasibility with battery storage and electric vehicle (EV) charging integration.

## Features

### 🔋 Complete Energy System Analysis

- **PV System Simulation**: Real solar generation patterns with seasonal variations
- **Battery Storage**: Advanced battery charge/discharge simulation with SOC tracking
- **EV Charging**: Integration of electric vehicle charging patterns
- **Grid Interaction**: Import/export calculations with Nord Pool pricing

### 📊 Comprehensive Visualizations

- **Daily Energy Flow**: 24-hour visualization of consumption, generation, and battery state
- **Annual Analysis**: Monthly breakdowns of energy balance and costs
- **Energy Distribution**: Detailed flow analysis (self-consumption, battery, grid)
- **Payback Analysis**: 20-year cumulative cost comparison across scenarios
- **Summary Reports**: Detailed financial and technical comparisons

### 🚗 EV Database

- Real-world consumption data for major EV manufacturers
- Support for Tesla, VW, BMW, Audi, Mercedes, Nissan, Hyundai, Kia, Polestar, Opel
- Configuration-specific data (battery size, year, drivetrain)
- Automatic consumption calculation based on selected vehicle

### 🌍 Location-Based Solar Data

- Pre-configured locations (Riga, Vilnius, Tallinn, Helsinki, Stockholm, Oslo, Copenhagen)
- PVGIS API integration for real solar radiation data
- Adjustable panel tilt and azimuth
- Seasonal generation patterns

### 💾 Configuration Management

- Save/load configurations using browser localStorage
- Export/import settings
- Reset to defaults
- Persistent storage across sessions

## Getting Started

### Prerequisites

- Modern web browser (Chrome, Firefox, Safari, Edge)
- No server required - runs entirely in browser
- Internet connection for PVGIS data fetching (optional)

### Installation

1. Download or clone all files to a local directory
2. Open `index.html` in your web browser
3. Start configuring your PV system!

### Files Structure

```
├── index.html          # Main HTML structure
├── style.css           # Complete styling
├── app.js              # UI logic and event handlers
├── calculator.js       # Core calculation engine
├── charts.js           # Chart.js visualization logic
├── ev-database.js      # EV consumption database
└── README_WEB.md       # This file
```

## Usage

### 1. Input Parameters Tab

#### Electricity Tariff

- Configure your electricity costs (power, energy, transfer, service fees)
- Set VAT rate
- Enter monthly service fee

#### Energy Consumption

- Set monthly household consumption (without EV)
- Choose consumption pattern (Working Family, Retired Couple, Home Office, Minimal)
- Adjust seasonal variation (0-50%, typically 20%)

#### PV System

- Enable/disable PV system analysis
- Set system size (kWp)
- Enter installation cost
- Select location or fetch real PVGIS data
- Configure panel tilt and azimuth

#### Battery Storage

- Enable/disable battery storage
- Set battery capacity (kWh)
- Enter battery cost
- Calculate recommended size

#### Nord Pool Pricing

- Set average selling price for excess energy

#### Electric Vehicle

- Enable/disable EV charging
- Select make, model, and configuration (auto-fills consumption)
- Set weekly distance and charging parameters
- Configure charging start time

### 2. Energy Flow Analysis Tab

#### Daily Energy Flow

- Select any date for analysis
- Visualize 24-hour energy patterns
- View battery SOC changes
- See grid import/export

#### Annual Analysis

- Full year simulation
- Monthly energy balance
- Self-sufficiency trends
- Cost and savings breakdown

#### Energy Distribution

- Doughnut chart of energy flows
- Self-consumption vs export vs import
- Battery utilization

#### Scenario Comparison

- Compare No PV vs PV Only vs PV+Battery
- 20-year cumulative payback timeline
- Breakeven analysis
- Detailed financial summary

## Calculation Methodology

### Solar Generation

- Location-based irradiance data (kWh/m²/day)
- Seasonal multipliers (35% winter to 135% summer peak)
- Day-length adjusted hourly generation curves
- System efficiency factor (85%)

### Consumption Patterns

- Pattern-based hourly distribution (weekday/weekend)
- Seasonal variations (20% default strength)
- EV charging integration with configurable timing
- Weekend consumption boost (15%)

### Battery Simulation

- Realistic charge/discharge efficiency (95%)
- Minimum SOC protection (10%)
- Priority: self-consumption > battery > grid export
- Discharge priority: battery > grid import

### Financial Analysis

- Total electricity cost including VAT
- Grid export income (Nord Pool)
- 20-year cumulative cost comparison
- Breakeven period calculation
- Annual savings estimation

## Technical Notes

### Browser Compatibility

- Tested on Chrome 100+, Firefox 100+, Safari 15+, Edge 100+
- Requires JavaScript enabled
- Uses ES6+ features
- LocalStorage for configuration persistence

### External Dependencies

- Chart.js 4.4.0 (CDN)
- Font Awesome 6.4.0 (CDN)
- No backend server required

### Data Storage

- Configurations stored in browser localStorage
- No server-side data transmission
- PVGIS API calls only when requested by user

## Limitations

1. **Solar Data**: Built-in model provides estimates ±15-25% accuracy. Use PVGIS for better accuracy (±5-8%)
2. **Battery Model**: Simplified model doesn't account for degradation over time
3. **EV Charging**: Assumes consistent daily charging; doesn't model sporadic patterns
4. **Weather**: Doesn't account for real-time weather variations
5. **Grid Pricing**: Uses static prices; doesn't model dynamic/spot pricing
6. **Maintenance**: Doesn't include maintenance costs or system degradation

## Future Enhancements

- [ ] Python backend for more complex calculations
- [ ] Historical weather data integration
- [ ] Dynamic pricing models (spot market)
- [ ] Battery degradation modeling
- [ ] Multiple EV support
- [ ] PDF report generation
- [ ] Multi-language support
- [ ] Mobile app version

## License

This software is provided as-is for educational and analytical purposes.

## Credits

- PV irradiance data based on PVGIS (EU Science Hub)
- EV consumption data from real-world testing
- Solar calculation methodology based on industry standards

## Support

For questions or issues:

1. Check calculations against known values
2. Verify input parameters
3. Try PVGIS data for your location
4. Compare with other PV calculators

## Version

Web Version 1.0 - Complete port from PyQt5 GUI

- All features implemented
- Client-side calculations
- No installation required
- Cross-platform compatible
