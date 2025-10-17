"""
Example demonstrating EV charging and seasonal variations
Run this to see the new features in action!
"""

from PV_calculator import (
    ElectricityTariff, ConsumptionProfile, PVSystemSpecs,
    BatterySpecs, NordPoolPrice, EVProfile, PVFeasibilityCalculator
)

def compare_scenarios():
    """Compare scenarios: No EV vs. With EV"""
    
    print("=" * 80)
    print("PV CALCULATOR - EV & SEASONAL VARIATIONS DEMO")
    print("=" * 80)
    print()
    
    # Common parameters
    tariff = ElectricityTariff(
        power_amperes=25,
        power_cost_per_ampere=0.50,
        electricity_cost=0.10,  # €0.10/kWh
        transfer_cost=0.04,
        service_cost=0.01,
        monthly_service_fee=5.0,
        vat_rate=0.21
    )
    
    consumption = ConsumptionProfile(
        monthly_consumption_kwh=500  # Household only
    )
    
    pv_system = PVSystemSpecs(
        peak_power_kw=6.0,  # 6 kWp system
        installation_cost=8000,
        avg_daily_irradiance=3.5
    )
    
    battery = BatterySpecs(
        capacity_kwh=10.0,
        installation_cost=5000
    )
    
    nord_pool = NordPoolPrice(
        average_price=0.06
    )
    
    # Scenario 1: Without EV
    print("\n" + "=" * 80)
    print("SCENARIO A: HOUSEHOLD WITHOUT EV")
    print("=" * 80)
    
    ev_no = EVProfile(enabled=False)
    calc_no_ev = PVFeasibilityCalculator(
        tariff=tariff,
        consumption=consumption,
        pv_system=pv_system,
        battery=battery,
        nord_pool=nord_pool,
        ev_profile=ev_no
    )
    
    baseline_no_ev = calc_no_ev.calculate_baseline_costs()
    with_pv_no_ev = calc_no_ev.calculate_annual_costs_with_pv(with_battery=True)
    roi_no_ev = calc_no_ev.calculate_roi(with_battery=True)
    
    print(f"\nWithout PV:")
    print(f"  Annual Cost: €{baseline_no_ev['annual_cost']:.2f}")
    print(f"\nWith PV + Battery:")
    print(f"  Annual Cost: €{with_pv_no_ev['annual_cost']:.2f}")
    print(f"  Annual Savings: €{roi_no_ev['annual_savings']:.2f}")
    print(f"  Payback Period: {roi_no_ev['simple_payback_years']:.1f} years")
    print(f"  Self-Sufficiency: {with_pv_no_ev['self_sufficiency_ratio']*100:.1f}%")
    
    # Scenario 2: With EV (60 km/day)
    print("\n" + "=" * 80)
    print("SCENARIO B: HOUSEHOLD WITH EV (60 km/day driving)")
    print("=" * 80)
    
    ev_yes = EVProfile(
        enabled=True,
        daily_driving_kwh=15.0,  # ~60 km at 25 kWh/100km
        charging_power_kw=7.0
    )
    
    calc_with_ev = PVFeasibilityCalculator(
        tariff=tariff,
        consumption=consumption,
        pv_system=pv_system,
        battery=battery,
        nord_pool=nord_pool,
        ev_profile=ev_yes
    )
    
    baseline_with_ev = calc_with_ev.calculate_baseline_costs()
    with_pv_with_ev = calc_with_ev.calculate_annual_costs_with_pv(with_battery=True)
    roi_with_ev = calc_with_ev.calculate_roi(with_battery=True)
    
    annual_ev_cost = ev_yes.daily_driving_kwh * 365 * tariff.get_total_cost_per_kwh()
    
    print(f"\nWithout PV:")
    print(f"  Household Annual Cost: €{baseline_with_ev['annual_cost']:.2f}")
    print(f"  EV Charging Cost: €{annual_ev_cost:.2f}")
    print(f"  Total: €{baseline_with_ev['annual_cost'] + annual_ev_cost:.2f}")
    
    print(f"\nWith PV + Battery:")
    print(f"  Annual Cost: €{with_pv_with_ev['annual_cost']:.2f}")
    print(f"  Annual Savings: €{roi_with_ev['annual_savings']:.2f}")
    print(f"  Payback Period: {roi_with_ev['simple_payback_years']:.1f} years")
    print(f"  Household Self-Sufficiency: {with_pv_with_ev['self_sufficiency_ratio']*100:.1f}%")
    print(f"  Total Self-Sufficiency (incl. EV): {with_pv_with_ev['total_self_sufficiency_ratio']*100:.1f}%")
    print(f"\n  Grid Import Breakdown:")
    print(f"    - Household: {with_pv_with_ev['annual_grid_import_household']:.0f} kWh")
    print(f"    - EV Charging: {with_pv_with_ev['annual_grid_import_ev']:.0f} kWh")
    
    # Comparison
    print("\n" + "=" * 80)
    print("COMPARISON: IMPACT OF ADDING EV")
    print("=" * 80)
    
    ev_impact_cost = annual_ev_cost
    ev_impact_consumption = ev_yes.daily_driving_kwh * 365
    payback_difference = roi_with_ev['simple_payback_years'] - roi_no_ev['simple_payback_years']
    
    print(f"\nEV Impact:")
    print(f"  Additional Annual Consumption: {ev_impact_consumption:.0f} kWh (+{ev_impact_consumption/baseline_no_ev['annual_consumption']*100:.0f}%)")
    print(f"  Additional Annual Cost (without PV): €{ev_impact_cost:.2f}")
    print(f"  PV System Payback Difference: {payback_difference:+.1f} years")
    
    print(f"\nKey Insights:")
    print(f"  • EV adds ~€{ev_impact_cost:.0f}/year to electricity costs")
    print(f"  • PV can't directly charge EV (charges at night)")
    print(f"  • Battery is reserved for household peak loads")
    print(f"  • Consider larger PV system if planning to buy EV")
    
    # Seasonal breakdown
    print("\n" + "=" * 80)
    print("SEASONAL PRODUCTION & CONSUMPTION (With EV)")
    print("=" * 80)
    print("\n{:<12} {:>10} {:>12} {:>12} {:>10}".format(
        "Month", "PV (kWh)", "House (kWh)", "EV (kWh)", "Self-Suff"))
    print("-" * 65)
    
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    for month_num, (month_name, days) in enumerate(zip(months, days_in_month), 1):
        pv_daily = pv_system.estimate_daily_production(month=month_num)
        pv_monthly = pv_daily * days
        
        house_daily = consumption.get_daily_consumption(month=month_num)
        house_monthly = house_daily * days
        
        ev_daily = ev_yes.daily_driving_kwh if ev_yes.enabled else 0
        ev_monthly = ev_daily * days
        
        self_suff = (pv_monthly / house_monthly * 100) if house_monthly > 0 else 0
        
        print("{:<12} {:>10.0f} {:>12.0f} {:>12.0f} {:>9.0f}%".format(
            month_name, pv_monthly, house_monthly, ev_monthly, self_suff))
    
    print("\n" + "=" * 80)
    print("Notice how PV production varies dramatically by season!")
    print("Winter months (Dec-Feb): Very low production")
    print("Summer months (Jun-Aug): Peak production")
    print("This is why annual averaging would be misleading.")
    print("=" * 80)


if __name__ == "__main__":
    compare_scenarios()

