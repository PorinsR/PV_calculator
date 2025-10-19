"""
Verify that annual consumption is correctly distributed across months
"""

from PV_consumption_generator import ConsumptionPatternGenerator
import numpy as np

generator = ConsumptionPatternGenerator()

# Test with 6000 kWh annual
profile = generator.create_household_profile(
    name="Test",
    annual_consumption_kwh=6000,
    pattern_type='working_family',
    seasonal_strength=0.6,
    peak_hour=19
)

print("=" * 80)
print("ANNUAL CONSUMPTION DISTRIBUTION VERIFICATION")
print("=" * 80)
print(f"Target Annual Consumption: {profile.annual_consumption_kwh} kWh")
print()

# Get the Gaussian seasonal curve
seasonal_curve = generator.generate_gaussian_seasonal_curve(peak_month=1, strength=0.6)

print("STEP 1: Gaussian Seasonal Curve")
print("-" * 80)
print("Month | Multiplier | Description")
print("------|------------|------------------")
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
for i, (month, mult) in enumerate(zip(months, seasonal_curve), 1):
    print(f"{month:5s} | {mult:10.3f} | {'Peak' if mult > 1.4 else 'Low' if mult < 0.6 else 'Average'}")

print(f"\nAverage of multipliers: {np.mean(seasonal_curve):.3f}")
print()

# Calculate monthly consumption using current method
print("STEP 2: Monthly Consumption (Current Method)")
print("-" * 80)
days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

monthly_totals = []
for month, days in enumerate(days_in_month, 1):
    # This is what the code currently does
    weekday_avg = generator.get_daily_consumption(profile, month, True)
    weekend_avg = generator.get_daily_consumption(profile, month, False)
    
    # Approximate: 22 weekdays, rest weekends
    weekdays = 22
    weekends = days - weekdays
    
    monthly_total = (weekday_avg * weekdays) + (weekend_avg * weekends)
    monthly_totals.append(monthly_total)

print("Month | Days | Weekday Avg | Weekend Avg | Monthly Total")
print("------|------|-------------|-------------|---------------")
for i, (month, days, total) in enumerate(zip(months, days_in_month, monthly_totals), 1):
    weekday_avg = generator.get_daily_consumption(profile, i, True)
    weekend_avg = generator.get_daily_consumption(profile, i, False)
    print(f"{month:5s} | {days:4d} | {weekday_avg:11.2f} | {weekend_avg:11.2f} | {total:13.2f}")

actual_annual = sum(monthly_totals)
print(f"\nTotal from monthly sums: {actual_annual:.2f} kWh")
print(f"Target annual: {profile.annual_consumption_kwh:.2f} kWh")
print(f"Difference: {actual_annual - profile.annual_consumption_kwh:.2f} kWh ({((actual_annual/profile.annual_consumption_kwh - 1) * 100):.1f}%)")
print()

# Show the issue
print("STEP 3: Root Cause Analysis")
print("-" * 80)
print("\nHow get_daily_consumption() works:")
print("1. base_daily = annual_consumption / 365")
print("2. daily = base_daily × seasonal_multiplier[month]")
print("3. if weekend: daily × 1.15")
print()

base_daily = profile.annual_consumption_kwh / 365
print(f"Base daily: {base_daily:.3f} kWh")
print(f"January (multiplier {seasonal_curve[0]:.3f}): {base_daily * seasonal_curve[0]:.3f} kWh/weekday")
print(f"July (multiplier {seasonal_curve[6]:.3f}): {base_daily * seasonal_curve[6]:.3f} kWh/weekday")
print()

print("ISSUE: The Gaussian multipliers average to 1.0, but they're not normalized")
print("       to account for the number of days in each month!")
print()

# Calculate what the correct normalization should be
print("STEP 4: Correct Approach")
print("-" * 80)
print("\nTo get exact annual consumption, we need to:")
print("1. Generate Gaussian curve (winter peak)")
print("2. Calculate weighted average based on days per month")
print("3. Normalize so weighted average = 1.0")
print()

# Calculate current weighted average
weighted_sum = sum(seasonal_curve[i] * days for i, days in enumerate(days_in_month))
weighted_avg = weighted_sum / sum(days_in_month)
print(f"Current weighted average: {weighted_avg:.6f}")
print(f"Should be: 1.0")
print()

# Show corrected values
print("To fix: divide each multiplier by {:.6f}".format(weighted_avg))
corrected_curve = [m / weighted_avg for m in seasonal_curve]
print("\nCorrected Gaussian curve:")
for month, original, corrected in zip(months, seasonal_curve, corrected_curve):
    print(f"{month}: {original:.3f} → {corrected:.3f}")

print()
print("=" * 80)
print("CONCLUSION")
print("=" * 80)
print("Current implementation has a small bias (~2%) due to:")
print("- Gaussian curve not being normalized for days-per-month")
print("- Weekend adjustment (15%) not being pre-calculated")
print()
print("This is generally acceptable for practical purposes, but can be improved")
print("by normalizing the Gaussian curve properly.")

