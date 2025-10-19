"""
Test script to demonstrate the new Weekly Energy Balance graph
Shows day-wise consumption patterns and seasonal PV generation
"""

from PV_calculator import (
    ElectricityTariff, ConsumptionProfile, PVSystemSpecs, 
    BatterySpecs, NordPoolPrice, EVProfile, PVFeasibilityCalculator
)
from PV_calculator_graphs import PVGraphGenerator

def main():
    print("=" * 80)
    print("TESTING WEEKLY ENERGY BALANCE GRAPH")
    print("=" * 80)
    print()
    
    # Setup realistic system
    tariff = ElectricityTariff(
        power_amperes=25,
        power_cost_per_ampere=0.50,
        electricity_cost=0.08,
        transfer_cost=0.04,
        service_cost=0.01,
        monthly_service_fee=5.0,
        vat_rate=0.21
    )
    
    consumption = ConsumptionProfile(
        monthly_consumption_kwh=500  # 500 kWh/month household
    )
    
    pv_system = PVSystemSpecs(
        peak_power_kw=5.0,
        installation_cost=7000,
        avg_daily_irradiance=3.5
    )
    
    battery = BatterySpecs(
        capacity_kwh=7.0,
        installation_cost=4000
    )
    
    nord_pool = NordPoolPrice(average_price=0.06)
    
    # Optional: Enable EV charging
    ev_profile = EVProfile(
        enabled=True,
        daily_driving_kwh=15.0,  # ~60 km/day
        charging_power_kw=7.0
    )
    
    # Create calculator
    calculator = PVFeasibilityCalculator(
        tariff=tariff,
        consumption=consumption,
        pv_system=pv_system,
        battery=battery,
        nord_pool=nord_pool,
        ev_profile=ev_profile
    )
    
    # Create graph generator
    graph_gen = PVGraphGenerator(calculator)
    
    print("Generating weekly energy balance graphs...")
    print()
    
    # Generate graphs for different seasons
    weeks_to_show = [
        (1, "Winter", "January - Short days, low PV generation"),
        (13, "Spring", "Late March - Increasing daylight"),
        (26, "Summer", "Late June - Peak PV generation, long days"),
        (39, "Fall", "Late September - Decreasing daylight"),
        (52, "Winter", "Late December - Shortest days")
    ]
    
    for week_num, season, description in weeks_to_show:
        print(f"📊 Week {week_num} ({season}): {description}")
        print(f"   Generating graph...")
        
        try:
            # Generate and show the graph
            graph_gen.plot_weekly_energy_balance(
                week_number=week_num,
                with_battery=True,
                show=False  # Set to True to display interactively
            )
            print(f"   ✓ Graph generated successfully")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        print()
    
    print("=" * 80)
    print("WHAT TO OBSERVE IN THE GRAPHS:")
    print("=" * 80)
    print()
    print("1. PV Generation Pattern:")
    print("   • Summer (Week 26): Long days, PV from 5 AM - 9 PM")
    print("   • Winter (Week 1, 52): Short days, PV from 8 AM - 4 PM")
    print()
    print("2. Consumption Patterns:")
    print("   • Weekdays (Mon-Fri): Lower daytime consumption")
    print("   • Weekends (Sat-Sun): Higher daytime consumption")
    print("   • Evening peaks at 6-7 PM (everyone home)")
    print()
    print("3. Net Balance:")
    print("   • Green = Excess energy (exported to grid)")
    print("   • Red = Deficit (imported from grid)")
    print("   • Blue line = Battery state (if enabled)")
    print()
    print("4. Key Insights:")
    print("   • Summer weekdays: Best self-sufficiency")
    print("   • Winter weekdays: Highest grid imports (short days + evening peaks)")
    print("   • Weekends: Better PV utilization (consumption matches generation)")
    print("   • Battery: Helps bridge afternoon production to evening consumption")
    print()
    print("=" * 80)
    print("To display graphs interactively, change 'show=False' to 'show=True' in the code")
    print("=" * 80)

if __name__ == "__main__":
    main()

