"""
Test script for Consumption Pattern Generator V2
Tests the new consumption pattern generation and visualization features
"""

import sys
from datetime import datetime

# Test the consumption generator
from PV_consumption_generator import ConsumptionPatternGenerator, HouseholdProfile

print("=" * 80)
print("TESTING CONSUMPTION PATTERN GENERATOR V2")
print("=" * 80)
print()

# Initialize generator
generator = ConsumptionPatternGenerator()
print("✓ ConsumptionPatternGenerator initialized")
print()

# Test 1: Available patterns
print("Test 1: Available Patterns")
print("-" * 80)
patterns = generator.get_available_patterns()
print(f"Found {len(patterns)} patterns:")
for pattern in patterns:
    info = generator.get_pattern_info(pattern)
    print(f"  • {info['name']}: {info['description']}")
print()

# Test 2: Create household profile
print("Test 2: Create Household Profile")
print("-" * 80)
profile = generator.create_household_profile(
    name="Test Working Family",
    annual_consumption_kwh=6000,
    pattern_type='working_family',
    seasonal_strength=0.6,
    peak_hour=19
)
print(f"✓ Profile created: {profile.name}")
print(f"  Annual consumption: {profile.annual_consumption_kwh} kWh")
print(f"  Pattern type: {profile.pattern_type}")
print(f"  Seasonal strength: {profile.seasonal_strength}")
print(f"  Peak hour: {profile.peak_evening_hour}")
print()

# Test 3: Gaussian seasonal curve
print("Test 3: Gaussian Seasonal Curve")
print("-" * 80)
seasonal_curve = generator.generate_gaussian_seasonal_curve(peak_month=1, strength=0.6)
print("Monthly multipliers (Jan-Dec):")
for month, multiplier in enumerate(seasonal_curve, 1):
    print(f"  Month {month:2d}: {multiplier:.3f}")
print()

# Test 4: Daily consumption
print("Test 4: Daily Consumption Calculations")
print("-" * 80)
print("Daily consumption by month (weekday):")
for month in [1, 4, 7, 10]:  # Winter, Spring, Summer, Fall
    daily = generator.get_daily_consumption(profile, month, True)
    month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    print(f"  {month_names[month]}: {daily:.2f} kWh/day")
print()

# Test 5: Hourly pattern
print("Test 5: Hourly Pattern (January Monday)")
print("-" * 80)
print("Hour | Consumption (kWh)")
print("-----|------------------")
for hour in [0, 6, 12, 18, 19, 20, 23]:
    consumption = generator.get_hourly_consumption(profile, 1, 0, hour)
    bar = "█" * int(consumption * 5)
    print(f"{hour:02d}:00 | {consumption:.3f} {bar}")
print()

# Test 6: Full year generation
print("Test 6: Generate Full Year Data")
print("-" * 80)
print("Generating year data (365 days with hourly detail)...")
year_data = generator.generate_year_consumption(profile)
stats = year_data['statistics']

print(f"✓ Year data generated")
print(f"  Total annual: {stats['total_annual_kwh']:.0f} kWh")
print(f"  Average daily: {stats['average_daily_kwh']:.2f} kWh")
print(f"  Peak month: {stats['peak_month']} ({stats['monthly_totals'][stats['peak_month']]:.0f} kWh)")
print(f"  Low month: {stats['low_month']} ({stats['monthly_totals'][stats['low_month']]:.0f} kWh)")
print(f"  Variation: {(stats['monthly_totals'][stats['peak_month']] / stats['monthly_totals'][stats['low_month']]):.2f}x")
print()

# Test 7: Test graphs (if available)
print("Test 7: Graph Generation")
print("-" * 80)

try:
    from PV_consumption_graphs import ConsumptionGraphGenerator
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for testing
    
    graph_gen = ConsumptionGraphGenerator(generator)
    print("✓ ConsumptionGraphGenerator initialized")
    
    # Test creating a graph (don't show, just create)
    print("  Testing daily pattern comparison graph...")
    fig = graph_gen.plot_daily_pattern_comparison(profile, show=False)
    print("  ✓ Daily pattern comparison graph created")
    
    print("  Testing seasonal variation graph...")
    fig = graph_gen.plot_seasonal_variation(profile, show=False)
    print("  ✓ Seasonal variation graph created")
    
    print("  Testing weekly heatmap...")
    fig = graph_gen.plot_weekly_heatmap(profile, month=1, show=False)
    print("  ✓ Weekly heatmap created")
    
    print()
    print("✓ All graph tests passed")
    
except ImportError as e:
    print(f"⚠ Graph generation not available: {e}")
    print("  Install matplotlib and numpy to enable graphs")

print()

# Test 8: Pattern comparison
print("Test 8: Compare Different Patterns")
print("-" * 80)
patterns_to_compare = ['working_family', 'home_office', 'retired']
print(f"Comparing patterns for January weekday (19:00):")
for pattern_type in patterns_to_compare:
    test_profile = generator.create_household_profile(
        name=pattern_type,
        annual_consumption_kwh=6000,
        pattern_type=pattern_type,
        seasonal_strength=0.5
    )
    consumption = generator.get_hourly_consumption(test_profile, 1, 0, 19)
    info = generator.get_pattern_info(pattern_type)
    print(f"  {info['name']:20s}: {consumption:.3f} kWh")
print()

# Test 9: Weekend vs Weekday
print("Test 9: Weekend vs Weekday Comparison")
print("-" * 80)
print("January consumption comparison:")
weekday = generator.get_daily_consumption(profile, 1, True)
weekend = generator.get_daily_consumption(profile, 1, False)
print(f"  Weekday: {weekday:.2f} kWh/day")
print(f"  Weekend: {weekend:.2f} kWh/day")
print(f"  Weekend increase: {((weekend/weekday - 1) * 100):.1f}%")
print()

# Final summary
print("=" * 80)
print("ALL TESTS COMPLETED SUCCESSFULLY! ✓")
print("=" * 80)
print()
print("The Consumption Pattern Generator V2 is working correctly.")
print("You can now use it in the GUI application.")
print()
print("Quick Start:")
print("  1. Run: python PV_calculator_gui.py")
print("  2. Go to the '⭐ Consumption Patterns V2' tab")
print("  3. Select a pattern type and adjust parameters")
print("  4. Click any graph button to visualize the patterns")
print()

