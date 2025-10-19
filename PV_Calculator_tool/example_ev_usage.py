"""
Example: Using EV Consumption Feature
Demonstrates how to add EV consumption to household consumption patterns
"""

# Note: This example can be run once numpy is available
# For now, it serves as a reference implementation

def example_ev_consumption():
    """
    Example showing how to use the EV consumption feature
    """
    
    # Normally you would import these:
    # from PV_consumption_generator import ConsumptionPatternGenerator, EVConsumptionProfile
    
    print("=" * 70)
    print("EV Consumption Feature - Example Usage")
    print("=" * 70)
    print()
    
    print("Step 1: Create EV Profile")
    print("-" * 70)
    print("""
ev_profile = EVConsumptionProfile(
    enabled=True,
    weekly_distance_km=300,        # 300 km per week
    consumption_per_100km=18.0,    # 18 kWh per 100km
    charging_days=[True, True, True, True, True, False, False],  # Mon-Fri
    charging_hours=[22, 23, 0, 1, 2, 3, 4, 5, 6]  # 22:00-06:00
)
    """)
    
    # Calculate what this means
    weekly_kwh = (300 / 100.0) * 18.0
    daily_avg = weekly_kwh / 7.0
    per_charging_day = weekly_kwh / 5
    annual_kwh = weekly_kwh * 52
    hourly = per_charging_day / 9
    
    print(f"This configuration means:")
    print(f"  • Weekly consumption: {weekly_kwh:.1f} kWh")
    print(f"  • Daily average: {daily_avg:.2f} kWh")
    print(f"  • Per charging day (Mon-Fri): {per_charging_day:.1f} kWh")
    print(f"  • Per hour during charging: {hourly:.2f} kWh")
    print(f"  • Annual EV consumption: {annual_kwh:.0f} kWh")
    print()
    
    print("Step 2: Create Household Profile with EV")
    print("-" * 70)
    print("""
generator = ConsumptionPatternGenerator()

profile = generator.create_household_profile(
    name="Family with EV",
    annual_consumption_kwh=6000,
    pattern_type='working_family',
    seasonal_strength=0.6,
    peak_hour=19
)
profile.ev_profile = ev_profile
    """)
    print()
    
    print("Step 3: Generate Annual Data")
    print("-" * 70)
    print("""
year_data = generator.generate_year_consumption(profile)
stats = year_data['statistics']
    """)
    
    household_annual = 6000
    total_annual = household_annual + annual_kwh
    
    print("Results:")
    print(f"  • Household annual: {household_annual:.0f} kWh")
    print(f"  • EV annual: {annual_kwh:.0f} kWh")
    print(f"  • Total annual: {total_annual:.0f} kWh")
    print()
    
    print("Step 4: Analyze Specific Days")
    print("-" * 70)
    print("""
# Monday (charging day)
monday_total = generator.get_daily_consumption(profile, 1, True, 0)
monday_household = generator.get_daily_consumption(profile, 1, True, 0, include_ev=False)
monday_ev = monday_total - monday_household

# Saturday (no charging)
saturday_total = generator.get_daily_consumption(profile, 1, False, 5)
saturday_household = generator.get_daily_consumption(profile, 1, False, 5, include_ev=False)
    """)
    
    # Approximate values (would be exact with actual calculation)
    print("Results (January):")
    print(f"  Monday:")
    print(f"    - Household: ~27 kWh")
    print(f"    - EV: {per_charging_day:.1f} kWh")
    print(f"    - Total: ~{27 + per_charging_day:.1f} kWh")
    print(f"  Saturday:")
    print(f"    - Household: ~25 kWh (weekend is slightly higher)")
    print(f"    - EV: 0 kWh (no charging)")
    print(f"    - Total: ~25 kWh")
    print()
    
    print("Step 5: Hourly Breakdown")
    print("-" * 70)
    print("Sample hourly pattern for Monday (charging day):")
    print()
    print("Hour  | Household | EV      | Total   | Activity")
    print("------|-----------|---------|---------|------------------")
    
    # Sample hourly data
    hourly_samples = [
        (0, 0.55, hourly, "Charging"),
        (1, 0.52, hourly, "Charging"),
        (7, 1.45, 0, "Morning peak"),
        (12, 0.85, 0, "Midday"),
        (19, 2.15, 0, "Evening peak"),
        (22, 1.05, hourly, "Charging starts"),
        (23, 0.95, hourly, "Charging"),
    ]
    
    for hour, household, ev, activity in hourly_samples:
        total = household + ev
        ev_marker = "⚡" if ev > 0 else ""
        print(f"{hour:02d}:00 | {household:5.2f} kWh | {ev:5.2f} kWh | {total:5.2f} kWh | {activity} {ev_marker}")
    
    print("...")
    print()
    
    print("=" * 70)
    print("Additional Examples")
    print("=" * 70)
    print()
    
    print("Example 1: Solar-Optimized Daytime Charging")
    print("-" * 70)
    print("""
ev_solar = EVConsumptionProfile(
    enabled=True,
    weekly_distance_km=200,
    consumption_per_100km=17.0,
    charging_days=[True, True, True, True, True, False, False],
    charging_hours=[11, 12, 13, 14, 15]  # Midday solar peak
)
    """)
    
    solar_weekly = (200 / 100.0) * 17.0
    solar_per_day = solar_weekly / 5
    solar_hourly = solar_per_day / 5
    
    print(f"  • Weekly: {solar_weekly:.1f} kWh")
    print(f"  • Per weekday: {solar_per_day:.1f} kWh")
    print(f"  • Per hour (11:00-15:00): {solar_hourly:.2f} kWh")
    print(f"  • Annual: {solar_weekly * 52:.0f} kWh")
    print("  ✓ Charges during peak solar production hours")
    print()
    
    print("Example 2: Weekend Charging Only")
    print("-" * 70)
    print("""
ev_weekend = EVConsumptionProfile(
    enabled=True,
    weekly_distance_km=150,
    consumption_per_100km=16.0,
    charging_days=[False, False, False, False, False, True, True],
    charging_hours=[10, 11, 12, 13, 14, 15, 16]  # Weekend daytime
)
    """)
    
    weekend_weekly = (150 / 100.0) * 16.0
    weekend_per_day = weekend_weekly / 2
    weekend_hourly = weekend_per_day / 7
    
    print(f"  • Weekly: {weekend_weekly:.1f} kWh")
    print(f"  • Per weekend day: {weekend_per_day:.1f} kWh")
    print(f"  • Per hour: {weekend_hourly:.2f} kWh")
    print(f"  • Annual: {weekend_weekly * 52:.0f} kWh")
    print("  ✓ Suitable for low-mileage users or those with weekend solar access")
    print()
    
    print("Example 3: High-Mileage Commuter")
    print("-" * 70)
    print("""
ev_high_mileage = EVConsumptionProfile(
    enabled=True,
    weekly_distance_km=500,
    consumption_per_100km=20.0,
    charging_days=[True, True, True, True, True, False, False],
    charging_hours=[21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7]  # Long charging window
)
    """)
    
    high_weekly = (500 / 100.0) * 20.0
    high_per_day = high_weekly / 5
    high_hourly = high_per_day / 11
    
    print(f"  • Weekly: {high_weekly:.1f} kWh")
    print(f"  • Per weekday: {high_per_day:.1f} kWh")
    print(f"  • Per hour: {high_hourly:.2f} kWh")
    print(f"  • Annual: {high_weekly * 52:.0f} kWh")
    print("  ✓ Longer charging window to spread the load")
    print()
    
    print("=" * 70)
    print("Key Benefits")
    print("=" * 70)
    print()
    print("✓ Easy to configure - just enter your weekly distance and EV efficiency")
    print("✓ Flexible charging schedules - daily, weekdays, weekends, or custom")
    print("✓ Realistic patterns - charging only during specified hours")
    print("✓ Separate tracking - household and EV consumption tracked independently")
    print("✓ Annual projections - accurate yearly consumption with monthly breakdown")
    print()
    
    print("=" * 70)
    print("Next Steps")
    print("=" * 70)
    print()
    print("1. Read EV_CONSUMPTION_QUICKSTART.md for 5-minute setup")
    print("2. Read EV_CONSUMPTION_FEATURE.md for complete documentation")
    print("3. Integrate with PV calculator for solar system sizing")
    print("4. Optimize charging schedule for maximum solar self-consumption")
    print()
    print("For questions and support, see the documentation files.")
    print()

if __name__ == "__main__":
    example_ev_consumption()

