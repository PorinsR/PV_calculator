"""
Battery Flow Calculator - Energy Management System
Calculates hour-by-hour energy flow including battery charging/discharging
Integrates consumption patterns, solar generation, and battery storage
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class BatteryFlowResult:
    """Results from battery flow simulation"""
    # Hourly data (24 or 8760 values)
    hourly_consumption: List[float]
    hourly_generation: List[float]
    hourly_battery_soc: List[float]  # State of charge (kWh)
    hourly_battery_charge: List[float]  # Positive = charging
    hourly_battery_discharge: List[float]  # Positive = discharging
    hourly_grid_import: List[float]
    hourly_grid_export: List[float]
    hourly_self_consumption: List[float]
    
    # Daily/period metrics
    total_consumption: float
    total_generation: float
    total_grid_import: float
    total_grid_export: float
    total_self_consumption: float
    battery_cycles: float
    self_sufficiency_ratio: float  # % consumption covered by solar+battery
    self_consumption_ratio: float  # % solar used locally (not exported)
    
    # Battery metrics
    max_battery_soc: float
    min_battery_soc: float
    avg_battery_soc: float
    battery_throughput: float  # Total kWh cycled through battery
    final_soc: float  # SOC at end of period (for continuity)


class BatteryFlowCalculator:
    """
    Simulates energy flow including battery charging/discharging
    Priority: Solar → Household → Battery → Grid
    """
    
    def __init__(self, 
                 battery_capacity_kwh: float,
                 battery_efficiency: float = 0.95,
                 max_charge_rate_kw: float = None,
                 max_discharge_rate_kw: float = None,
                 min_soc_percent: float = 10.0):
        """
        Initialize battery flow calculator
        
        Args:
            battery_capacity_kwh: Total battery capacity
            battery_efficiency: Round-trip efficiency (0.9-0.95 typical)
            max_charge_rate_kw: Max charging power (None = unlimited)
            max_discharge_rate_kw: Max discharge power (None = unlimited)
            min_soc_percent: Minimum state of charge to preserve battery
        """
        self.battery_capacity = battery_capacity_kwh
        self.battery_efficiency = battery_efficiency
        self.max_charge_rate = max_charge_rate_kw if max_charge_rate_kw else battery_capacity_kwh
        self.max_discharge_rate = max_discharge_rate_kw if max_discharge_rate_kw else battery_capacity_kwh
        self.min_soc = battery_capacity_kwh * (min_soc_percent / 100.0)
    
    def simulate_hourly_flow(self,
                            hourly_consumption: List[float],
                            hourly_generation: List[float],
                            initial_soc: float = None) -> BatteryFlowResult:
        """
        Simulate hour-by-hour energy flow with battery
        
        Args:
            hourly_consumption: List of hourly consumption values (kWh)
            hourly_generation: List of hourly solar generation values (kWh)
            initial_soc: Initial battery state of charge (kWh), default 50%
        
        Returns:
            BatteryFlowResult with all metrics
        """
        n_hours = len(hourly_consumption)
        
        if initial_soc is None:
            initial_soc = self.battery_capacity * 0.5  # Start at 50%
        
        # Initialize arrays
        battery_soc = []  # State of charge over time (end of each hour)
        battery_charge = []  # Energy charged into battery
        battery_discharge = []  # Energy discharged from battery
        grid_import = []
        grid_export = []
        self_consumption = []
        
        current_soc = initial_soc
        
        for hour in range(n_hours):
            consumption = hourly_consumption[hour]
            generation = hourly_generation[hour]
            
            # Calculate net balance before battery
            net_balance = generation - consumption
            
            if net_balance > 0:
                # SURPLUS: Solar > Consumption
                # 1. Use solar for consumption (self-consumption)
                self_cons = consumption
                excess = net_balance
                
                # 2. Charge battery with excess
                available_capacity = self.battery_capacity - current_soc
                charge_amount = min(excess, available_capacity, self.max_charge_rate)
                
                if charge_amount > 0:
                    # Apply charging efficiency (energy loss during charging)
                    actual_charge = charge_amount * self.battery_efficiency
                    current_soc += actual_charge
                    excess -= charge_amount
                    battery_charge.append(charge_amount)
                    battery_discharge.append(0)
                else:
                    battery_charge.append(0)
                    battery_discharge.append(0)
                
                # 3. Export remaining excess to grid
                grid_export.append(excess)
                grid_import.append(0)
                self_consumption.append(self_cons)
                
            else:
                # DEFICIT: Consumption > Solar
                # 1. Use all available solar
                self_cons = generation
                deficit = -net_balance
                
                # 2. Discharge battery to cover deficit
                available_discharge = current_soc - self.min_soc
                # Calculate how much battery energy we need (accounting for discharge efficiency)
                # If we need X kWh, we must discharge X/efficiency from battery
                needed_from_battery = min(deficit / self.battery_efficiency, available_discharge, self.max_discharge_rate)
                
                if needed_from_battery > 0:
                    # Discharge from battery
                    current_soc -= needed_from_battery
                    # Actual energy delivered (after efficiency loss)
                    actual_discharge = needed_from_battery * self.battery_efficiency
                    deficit -= actual_discharge
                    self_cons += actual_discharge
                    battery_discharge.append(needed_from_battery)
                    battery_charge.append(0)
                else:
                    battery_discharge.append(0)
                    battery_charge.append(0)
                
                # 3. Import remaining deficit from grid
                grid_import.append(max(0, deficit))  # Ensure no negative import
                grid_export.append(0)
                self_consumption.append(self_cons)
            
            # Store SOC at END of hour
            battery_soc.append(current_soc)
        
        # Calculate summary metrics
        total_consumption = sum(hourly_consumption)
        total_generation = sum(hourly_generation)
        total_grid_import = sum(grid_import)
        total_grid_export = sum(grid_export)
        total_self_consumption = sum(self_consumption)
        
        # Battery cycles (full charge/discharge cycles)
        battery_throughput = sum(battery_charge) + sum(battery_discharge)
        battery_cycles = battery_throughput / (2 * self.battery_capacity)
        
        # Self-sufficiency: % of consumption covered without grid import
        self_sufficiency = (total_self_consumption / total_consumption * 100) if total_consumption > 0 else 0
        
        # Self-consumption: % of solar used locally (not exported)
        self_consumption_ratio = (total_self_consumption / total_generation * 100) if total_generation > 0 else 0
        
        return BatteryFlowResult(
            hourly_consumption=hourly_consumption,
            hourly_generation=hourly_generation,
            hourly_battery_soc=battery_soc,
            hourly_battery_charge=battery_charge,
            hourly_battery_discharge=battery_discharge,
            hourly_grid_import=grid_import,
            hourly_grid_export=grid_export,
            hourly_self_consumption=self_consumption,
            total_consumption=total_consumption,
            total_generation=total_generation,
            total_grid_import=total_grid_import,
            total_grid_export=total_grid_export,
            total_self_consumption=total_self_consumption,
            battery_cycles=battery_cycles,
            self_sufficiency_ratio=self_sufficiency,
            self_consumption_ratio=self_consumption_ratio,
            max_battery_soc=max(battery_soc) if battery_soc else 0,
            min_battery_soc=min(battery_soc) if battery_soc else 0,
            avg_battery_soc=np.mean(battery_soc) if battery_soc else 0,
            battery_throughput=battery_throughput,
            final_soc=battery_soc[-1] if battery_soc else initial_soc  # Store final SOC
        )
    
    def simulate_daily_flow(self,
                           consumption_gen,
                           solar_gen,
                           household_profile,
                           solar_system,
                           month: int,
                           day_of_week: int = 0,
                           initial_soc: float = None) -> BatteryFlowResult:
        """
        Simulate a single day's energy flow
        
        Args:
            consumption_gen: ConsumptionPatternGenerator instance
            solar_gen: SolarGenerationCalculator instance
            household_profile: HouseholdProfile
            solar_system: SolarSystemProfile
            month: Month (1-12)
            day_of_week: Day of week (0=Monday, 6=Sunday)
            initial_soc: Initial battery SOC (kWh), defaults to 50% if None
        
        Returns:
            BatteryFlowResult for the day
        """
        # Get hourly consumption
        hourly_consumption = [
            consumption_gen.get_hourly_consumption(household_profile, month, day_of_week, h)
            for h in range(24)
        ]
        
        # Get hourly generation
        hourly_generation = [
            solar_gen.get_hourly_generation(solar_system, month, h)
            for h in range(24)
        ]
        
        return self.simulate_hourly_flow(hourly_consumption, hourly_generation, initial_soc=initial_soc)


def main():
    """Example usage"""
    print("=" * 80)
    print("BATTERY FLOW CALCULATOR - TEST")
    print("=" * 80)
    print()
    
    # Create battery calculator
    battery_calc = BatteryFlowCalculator(
        battery_capacity_kwh=10.0,
        battery_efficiency=0.95,
        min_soc_percent=10
    )
    
    # Example: typical day consumption pattern (kWh per hour)
    consumption = [
        0.3, 0.2, 0.2, 0.2, 0.2, 0.3,  # Night (00-05)
        0.5, 0.8, 0.6, 0.4, 0.4, 0.4,  # Morning (06-11)
        0.4, 0.4, 0.4, 0.4, 0.5, 0.7,  # Afternoon (12-17)
        1.0, 1.5, 1.2, 1.0, 0.7, 0.4   # Evening (18-23)
    ]
    
    # Example: solar generation pattern (kWh per hour)
    generation = [
        0, 0, 0, 0, 0, 0,              # Night
        0.2, 1.0, 2.0, 3.0, 3.5, 4.0,  # Morning rising
        4.2, 4.0, 3.5, 3.0, 2.0, 1.0,  # Afternoon falling
        0.2, 0, 0, 0, 0, 0             # Evening/night
    ]
    
    print(f"Battery: {battery_calc.battery_capacity} kWh")
    print(f"Efficiency: {battery_calc.battery_efficiency * 100}%")
    print(f"Daily consumption: {sum(consumption):.1f} kWh")
    print(f"Daily generation: {sum(generation):.1f} kWh")
    print()
    
    # Simulate
    result = battery_calc.simulate_hourly_flow(consumption, generation)
    
    print("RESULTS")
    print("-" * 80)
    print(f"Total consumption: {result.total_consumption:.1f} kWh")
    print(f"Total generation: {result.total_generation:.1f} kWh")
    print(f"Self-consumption: {result.total_self_consumption:.1f} kWh ({result.self_consumption_ratio:.1f}%)")
    print(f"Grid import: {result.total_grid_import:.1f} kWh")
    print(f"Grid export: {result.total_grid_export:.1f} kWh")
    print(f"Self-sufficiency: {result.self_sufficiency_ratio:.1f}%")
    print(f"Battery cycles: {result.battery_cycles:.2f}")
    print(f"Battery SOC range: {result.min_battery_soc:.1f} - {result.max_battery_soc:.1f} kWh")
    print()
    
    print("HOURLY BREAKDOWN")
    print("-" * 80)
    print("Hour | Cons | Gen  | SOC  | Charge | Discharge | Import | Export")
    print("-----|------|------|------|--------|-----------|--------|--------")
    for h in range(24):
        print(f"{h:02d}:00| {consumption[h]:4.1f} | {generation[h]:4.1f} | "
              f"{result.hourly_battery_soc[h]:4.1f} | {result.hourly_battery_charge[h]:6.2f} | "
              f"{result.hourly_battery_discharge[h]:9.2f} | {result.hourly_grid_import[h]:6.2f} | "
              f"{result.hourly_grid_export[h]:6.2f}")


if __name__ == "__main__":
    main()

