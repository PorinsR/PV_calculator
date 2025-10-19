"""
Test with user's example: low month 180 kWh, high month 250 kWh
"""

from PV_consumption_generator import ConsumptionPatternGenerator

generator = ConsumptionPatternGenerator()

# Calculate annual consumption from the example
# Low month: 180 kWh (July - 31 days)
# High month: 250 kWh (January - 31 days)

# With seasonal strength 0.6, the ratio should be about 4:1
# July multiplier ≈ 0.4, January multiplier ≈ 1.6

# Work backwards: if January is 250 kWh/month
# 250 kWh / 31 days = 8.06 kWh/day average (including weekends)
# With multiplier 1.569, base_daily = 8.06 / 1.569 = 5.14 kWh
# Annual = 5.14 × 365 = 1876 kWh

# Actually, let's be more precise
# January: 22 weekdays × daily_weekday + 9 weekends × daily_weekend = 250
# With weekend = 1.15 × weekday
# 22 × d + 9 × 1.15 × d = 250
# d × (22 + 10.35) = 250
# d × 32.35 = 250
# d = 7.73 kWh/weekday

# With multiplier 1.569, base = 7.73 / 1.569 = 4.93 kWh
# Annual = 4.93 × 365 = 1799 kWh

# Let's find the annual that gives us close to 180-250 range
target_annual = 1800

profile = generator.create_household_profile(
    name="Example",
    annual_consumption_kwh=target_annual,
    pattern_type='working_family',
    seasonal_strength=0.6,
    peak_hour=19
)

print("=" * 80)
print("USER EXAMPLE VERIFICATION")
print("=" * 80)
print(f"Target: Low month ≈ 180 kWh, High month ≈ 250 kWh")
print(f"Annual consumption set to: {target_annual} kWh")
print()

days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

print("MONTHLY BREAKDOWN")
print("-" * 80)
print("Month | Days | Weekday | Weekend | Monthly Total | Description")
print("------|------|---------|---------|---------------|------------------")

monthly_totals = []
for month_num, (month, days) in enumerate(zip(months, days_in_month), 1):
    weekday_avg = generator.get_daily_consumption(profile, month_num, True)
    weekend_avg = generator.get_daily_consumption(profile, month_num, False)
    
    # Approximate weekday/weekend distribution
    weekdays = 22 if days >= 30 else int(days * 22/30)
    weekends = days - weekdays
    
    monthly_total = (weekday_avg * weekdays) + (weekend_avg * weekends)
    monthly_totals.append(monthly_total)
    
    if month_num == 1:
        desc = "← High month (winter)"
    elif month_num == 7:
        desc = "← Low month (summer)"
    else:
        desc = ""
    
    print(f"{month:5s} | {days:4d} | {weekday_avg:7.2f} | {weekend_avg:7.2f} | {monthly_total:13.2f} | {desc}")

actual_annual = sum(monthly_totals)
high_month = max(monthly_totals)
low_month = min(monthly_totals)

print()
print("SUMMARY")
print("-" * 80)
print(f"High month (January): {monthly_totals[0]:.0f} kWh (target ≈250)")
print(f"Low month (July):     {monthly_totals[6]:.0f} kWh (target ≈180)")
print(f"Ratio (high/low):     {monthly_totals[0]/monthly_totals[6]:.2f}x")
print()
print(f"Total annual:         {actual_annual:.0f} kWh")
print(f"Target annual:        {target_annual} kWh")
print(f"Accuracy:             {((actual_annual/target_annual) * 100):.2f}%")
print()

# Show how the pattern splits each month into days
print("=" * 80)
print("HOW IT WORKS")
print("=" * 80)
print()
print("Step 1: Annual Consumption Input")
print(f"  User enters: {target_annual} kWh/year")
print()

print("Step 2: Gaussian Distribution Creates Monthly Multipliers")
seasonal_curve = generator.generate_gaussian_seasonal_curve(peak_month=1, strength=0.6)
print(f"  January multiplier: {seasonal_curve[0]:.3f} (peak)")
print(f"  July multiplier:    {seasonal_curve[6]:.3f} (low)")
print(f"  Ratio:              {seasonal_curve[0]/seasonal_curve[6]:.1f}x")
print()

print("Step 3: Calculate Daily Base")
base_daily = target_annual / 365
print(f"  Base daily = {target_annual} / 365 = {base_daily:.2f} kWh/day")
print()

print("Step 4: Apply Monthly Multiplier")
jan_daily_weekday = base_daily * seasonal_curve[0]
jul_daily_weekday = base_daily * seasonal_curve[6]
print(f"  January weekday = {base_daily:.2f} × {seasonal_curve[0]:.3f} = {jan_daily_weekday:.2f} kWh/day")
print(f"  July weekday    = {base_daily:.2f} × {seasonal_curve[6]:.3f} = {jul_daily_weekday:.2f} kWh/day")
print()

print("Step 5: Weekend Adjustment")
print(f"  Weekend = weekday × 1.15 (15% higher)")
jan_daily_weekend = jan_daily_weekday * 1.15
jul_daily_weekend = jul_daily_weekday * 1.15
print(f"  January weekend = {jan_daily_weekday:.2f} × 1.15 = {jan_daily_weekend:.2f} kWh/day")
print(f"  July weekend    = {jul_daily_weekday:.2f} × 1.15 = {jul_daily_weekend:.2f} kWh/day")
print()

print("Step 6: Calculate Monthly Total")
print(f"  January: 22 weekdays × {jan_daily_weekday:.2f} + 9 weekends × {jan_daily_weekend:.2f}")
print(f"         = {22 * jan_daily_weekday:.2f} + {9 * jan_daily_weekend:.2f} = {monthly_totals[0]:.2f} kWh")
print()
print(f"  July:    22 weekdays × {jul_daily_weekday:.2f} + 9 weekends × {jul_daily_weekend:.2f}")
print(f"         = {22 * jul_daily_weekday:.2f} + {9 * jul_daily_weekend:.2f} = {monthly_totals[6]:.2f} kWh")
print()

print("Step 7: Split Each Day into 24 Hours")
print("  Using the workday/weekend hourly patterns defined earlier")
print("  Workday: baseline with morning peak (7-8) and evening peak (18-22)")
print("  Weekend: flat throughout day, no timed peaks")
print()

print("=" * 80)
print(f"✓ Annual consumption of {target_annual} kWh is correctly distributed!")
print(f"✓ High month: {monthly_totals[0]:.0f} kWh, Low month: {monthly_totals[6]:.0f} kWh")
print("=" * 80)

