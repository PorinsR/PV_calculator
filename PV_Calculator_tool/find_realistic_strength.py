"""
Find the right seasonal strength for realistic monthly variations
Target: 250 kWh high month, 180 kWh low month (1.4x ratio)
"""

from PV_consumption_generator import ConsumptionPatternGenerator
import numpy as np

generator = ConsumptionPatternGenerator()

# Test different seasonal strengths
print("=" * 80)
print("FINDING REALISTIC SEASONAL STRENGTH")
print("=" * 80)
print()

# For a household with reasonable variation
# High: 250 kWh, Low: 180 kWh → Ratio: 1.39x
target_high = 250
target_low = 180
target_ratio = target_high / target_low
target_annual = (target_high + target_low) * 6  # Rough estimate

print(f"Target: High month {target_high} kWh, Low month {target_low} kWh")
print(f"Target ratio: {target_ratio:.2f}x")
print(f"Estimated annual: ~{target_annual:.0f} kWh")
print()

print("Testing different seasonal strength values:")
print("-" * 80)
print("Strength | High/Low Ratio | High (kWh) | Low (kWh) | Annual")
print("---------|----------------|------------|-----------|--------")

days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

for strength in [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6]:
    # Create profile with this strength
    profile = generator.create_household_profile(
        name="Test",
        annual_consumption_kwh=target_annual,
        pattern_type='working_family',
        seasonal_strength=strength,
        peak_hour=19
    )
    
    # Calculate monthly totals
    monthly_totals = []
    for month in range(1, 13):
        weekday_avg = generator.get_daily_consumption(profile, month, True)
        weekend_avg = generator.get_daily_consumption(profile, month, False)
        days = days_in_month[month - 1]
        weekdays = 22 if days >= 30 else int(days * 22/30)
        weekends = days - weekdays
        monthly_total = (weekday_avg * weekdays) + (weekend_avg * weekends)
        monthly_totals.append(monthly_total)
    
    high = max(monthly_totals)
    low = min(monthly_totals)
    ratio = high / low
    actual_annual = sum(monthly_totals)
    
    marker = " ← GOOD" if 1.3 <= ratio <= 1.6 else ""
    print(f"{strength:8.2f} | {ratio:14.2f} | {high:10.0f} | {low:9.0f} | {actual_annual:6.0f}{marker}")

print()
print("=" * 80)
print("RECOMMENDATION")
print("=" * 80)
print()
print("For realistic household consumption (with electric heating):")
print("  • Seasonal strength: 0.15 - 0.25 (ratio 1.3x - 1.7x)")
print("  • Example: strength=0.2 gives ~1.5x winter/summer ratio")
print()
print("For well-insulated homes (minimal heating):")
print("  • Seasonal strength: 0.1 (ratio ~1.2x)")
print()
print("Current default of 0.6 (4x ratio) is TOO HIGH for most households!")
print()

# Show a realistic example
print("=" * 80)
print("REALISTIC EXAMPLE (strength=0.2)")
print("=" * 80)
print()

realistic_annual = 5200  # To get close to 250/180
profile = generator.create_household_profile(
    name="Realistic",
    annual_consumption_kwh=realistic_annual,
    pattern_type='working_family',
    seasonal_strength=0.2,  # Much more realistic
    peak_hour=19
)

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
monthly_totals = []

for month_num, (month, days) in enumerate(zip(months, days_in_month), 1):
    weekday_avg = generator.get_daily_consumption(profile, month_num, True)
    weekend_avg = generator.get_daily_consumption(profile, month_num, False)
    weekdays = 22 if days >= 30 else int(days * 22/30)
    weekends = days - weekdays
    monthly_total = (weekday_avg * weekdays) + (weekend_avg * weekends)
    monthly_totals.append(monthly_total)

print(f"Annual: {realistic_annual} kWh, Seasonal strength: 0.2")
print()
print("Month | Monthly (kWh)")
print("------|-------------")
for month, total in zip(months, monthly_totals):
    marker = " ← High" if total == max(monthly_totals) else " ← Low" if total == min(monthly_totals) else ""
    print(f"{month:5s} | {total:12.0f}{marker}")

print()
print(f"High month: {max(monthly_totals):.0f} kWh")
print(f"Low month:  {min(monthly_totals):.0f} kWh")
print(f"Ratio:      {max(monthly_totals)/min(monthly_totals):.2f}x")
print(f"Total:      {sum(monthly_totals):.0f} kWh")

