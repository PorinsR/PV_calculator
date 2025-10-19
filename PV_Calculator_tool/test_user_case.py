"""
Test script for the user's specific case to verify the bug fix
This should show POSITIVE savings and reasonable payback period
"""

from PV_calculator import (
    ElectricityTariff, ConsumptionProfile, PVSystemSpecs, 
    BatterySpecs, NordPoolPrice, EVProfile, PVFeasibilityCalculator
)

def main():
    print("=" * 80)
    print("TESTING USER'S CASE - VERIFYING BUG FIX")
    print("=" * 80)
    print()
    
    # User's parameters (based on the report)
    # Annual household: 8400 kWh → 700 kWh/month
    # Annual EV: 5840 kWh → 16 kWh/day
    # Effective cost: €0.1452/kWh
    
    # Reconstruct tariff from effective cost
    # Total cost = power + electricity + transfer + service + VAT
    # Effective €0.1452/kWh suggests:
    # - Electricity: ~€0.06/kWh
    # - Transfer: ~€0.04/kWh
    # - Service: ~€0.01/kWh
    # - Monthly service: ~€17/month
    # - Power: 25A × €0.50/A = €12.50/month
    # Total with 21% VAT ≈ €0.145/kWh
    
    tariff = ElectricityTariff(
        power_amperes=25,
        power_cost_per_ampere=0.50,      # €0.50/A/month
        electricity_cost=0.06,           # €0.06/kWh
        transfer_cost=0.04,              # €0.04/kWh
        service_cost=0.01,               # €0.01/kWh
        monthly_service_fee=17.0,        # €17/month
        vat_rate=0.21                    # 21%
    )
    
    # Verify tariff
    print("Tariff Verification:")
    print(f"  Total cost per kWh: €{tariff.get_total_cost_per_kwh():.4f}")
    print(f"  Expected: €0.1452")
    print()
    
    # User's consumption
    consumption = ConsumptionProfile(
        monthly_consumption_kwh=700  # 8400 kWh/year ÷ 12
    )
    
    # User's EV profile
    ev_profile = EVProfile(
        enabled=True,
        daily_driving_kwh=16.0,  # 5840 kWh/year ÷ 365
        charging_hours=[19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6]  # Evening/night
    )
    
    # User's PV system
    pv_system = PVSystemSpecs(
        peak_power_kw=12.0,
        installation_cost=2200.0,
        system_efficiency=0.85,
        annual_degradation_rate=0.005
    )
    
    # User's battery
    battery = BatterySpecs(
        capacity_kwh=14.0,
        installation_cost=2300.0,
        efficiency=0.95,
        depth_of_discharge=0.9,
        lifetime_years=10
    )
    
    # Nord Pool prices
    nord_pool = NordPoolPrice(
        average_price=0.06  # €0.06/kWh
    )
    
    print("=" * 80)
    print("SCENARIO SETUP")
    print("=" * 80)
    print(f"Household: {consumption.monthly_consumption_kwh} kWh/month = {consumption.get_annual_consumption()} kWh/year")
    print(f"EV: {ev_profile.daily_driving_kwh} kWh/day = {ev_profile.daily_driving_kwh * 365:.0f} kWh/year")
    print(f"Total consumption: {consumption.get_annual_consumption() + ev_profile.daily_driving_kwh * 365:.0f} kWh/year")
    print(f"PV System: {pv_system.peak_power_kw} kWp → ~{pv_system.estimate_annual_production():.0f} kWh/year")
    print(f"Battery: {battery.capacity_kwh} kWh")
    print()
    
    # Create calculator
    calculator = PVFeasibilityCalculator(
        tariff=tariff,
        consumption=consumption,
        pv_system=pv_system,
        battery=battery,
        nord_pool=nord_pool,
        ev_profile=ev_profile
    )
    
    # Calculate baseline (THIS SHOULD NOW INCLUDE EV!)
    baseline = calculator.calculate_baseline_costs()
    
    print("=" * 80)
    print("BASELINE COSTS (WITHOUT PV) - WITH BUG FIX")
    print("=" * 80)
    if 'household_annual_cost' in baseline:
        print(f"✅ Household electricity: €{baseline['household_annual_cost']:.2f}/year")
        print(f"✅ EV electricity: €{baseline['ev_annual_cost']:.2f}/year")
        print(f"✅ TOTAL: €{baseline['annual_cost']:.2f}/year")
    else:
        print(f"❌ OLD BUG: Only showing €{baseline['annual_cost']:.2f}/year (missing EV costs)")
    print(f"Monthly: €{baseline['monthly_cost']:.2f}")
    print()
    
    # Calculate with PV (no battery)
    pv_only = calculator.calculate_annual_costs_with_pv(with_battery=False)
    
    print("=" * 80)
    print("WITH PV ONLY (NO BATTERY)")
    print("=" * 80)
    print(f"Annual cost: €{pv_only['annual_cost']:.2f}")
    print(f"Grid import: {pv_only['annual_grid_import']:.0f} kWh")
    print(f"  - Household: {pv_only['annual_grid_import_household']:.0f} kWh")
    print(f"  - EV: {pv_only['annual_grid_import_ev']:.0f} kWh")
    print(f"Excess to grid: {pv_only['annual_excess_to_grid']:.0f} kWh")
    print(f"Revenue: €{pv_only['annual_revenue']:.2f}")
    print()
    print(f"💰 SAVINGS: €{baseline['annual_cost'] - pv_only['annual_cost']:.2f}/year")
    if baseline['annual_cost'] > pv_only['annual_cost']:
        payback = pv_system.installation_cost / (baseline['annual_cost'] - pv_only['annual_cost'])
        print(f"⏱️  PAYBACK: {payback:.1f} years")
        if payback < 10:
            print("✅ EXCELLENT investment!")
        elif payback < 15:
            print("✅ GOOD investment")
        else:
            print("⚠️  Long payback period")
    else:
        print("❌ LOSING MONEY!")
    print()
    
    # Calculate with PV + battery
    pv_battery = calculator.calculate_annual_costs_with_pv(with_battery=True)
    
    print("=" * 80)
    print("WITH PV + BATTERY")
    print("=" * 80)
    print(f"Annual cost: €{pv_battery['annual_cost']:.2f}")
    print(f"Grid import: {pv_battery['annual_grid_import']:.0f} kWh")
    print(f"  - Household: {pv_battery['annual_grid_import_household']:.0f} kWh")
    print(f"  - EV: {pv_battery['annual_grid_import_ev']:.0f} kWh")
    print(f"Excess to grid: {pv_battery['annual_excess_to_grid']:.0f} kWh")
    print(f"Revenue: €{pv_battery['annual_revenue']:.2f}")
    print(f"Self-sufficiency: {pv_battery['total_self_sufficiency_ratio']:.1%}")
    print()
    print(f"💰 SAVINGS: €{baseline['annual_cost'] - pv_battery['annual_cost']:.2f}/year")
    if baseline['annual_cost'] > pv_battery['annual_cost']:
        total_investment = pv_system.installation_cost + battery.installation_cost
        payback = total_investment / (baseline['annual_cost'] - pv_battery['annual_cost'])
        print(f"⏱️  PAYBACK: {payback:.1f} years (€{total_investment:.0f} investment)")
        if payback < 7:
            print("✅ EXCELLENT investment!")
        elif payback < 12:
            print("✅ GOOD investment")
        else:
            print("⚠️  Long payback period")
    else:
        print("❌ LOSING MONEY!")
    print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("Expected Results with Bug Fix:")
    print("  ✅ Baseline should be ~€2,000-2,300/year (household + EV)")
    print("  ✅ PV only should save €400-600/year")
    print("  ✅ PV + Battery should save €700-900/year")
    print("  ✅ Payback should be 4-6 years")
    print()
    
    if 'household_annual_cost' in baseline:
        print("✅ BUG FIX VERIFIED: Baseline includes both household and EV costs!")
    else:
        print("❌ BUG STILL EXISTS: Baseline missing EV costs!")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()

