"""
PV System Feasibility Calculator
Calculates the economic feasibility of installing a photovoltaic (solar) system
with or without battery storage, considering grid connection costs and electricity sales.
"""

import json
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import math


@dataclass
class ElectricityTariff:
    """Electricity cost structure"""
    power_amperes: float  # Connected power in Amperes
    power_cost_per_ampere: float  # EUR/A
    electricity_cost: float  # EUR/kWh
    transfer_cost: float  # EUR/kWh (grid transfer cost)
    service_cost: float  # EUR/kWh (electricity providing service)
    monthly_service_fee: float  # EUR/month
    vat_rate: float = 0.21  # 21% VAT
    
    def get_total_cost_per_kwh(self) -> float:
        """Calculate total cost per kWh including VAT"""
        base_cost = self.electricity_cost + self.transfer_cost + self.service_cost
        return base_cost * (1 + self.vat_rate)
    
    def get_monthly_fixed_cost(self) -> float:
        """Calculate monthly fixed costs including VAT"""
        power_cost = self.power_amperes * self.power_cost_per_ampere
        return (power_cost + self.monthly_service_fee) * (1 + self.vat_rate)
    
    def get_annual_cost(self, monthly_consumption_kwh: float) -> float:
        """Calculate annual electricity cost"""
        annual_consumption = monthly_consumption_kwh * 12
        annual_variable_cost = annual_consumption * self.get_total_cost_per_kwh()
        annual_fixed_cost = self.get_monthly_fixed_cost() * 12
        return annual_variable_cost + annual_fixed_cost


@dataclass
class PVSystemSpecs:
    """PV system specifications"""
    peak_power_kw: float  # Peak power in kW (kWp)
    installation_cost: float  # EUR (total system cost)
    annual_degradation_rate: float = 0.005  # 0.5% per year typical
    system_efficiency: float = 0.85  # System losses (inverter, cables, etc.)
    lifetime_years: int = 25
    
    # Average solar irradiance (kWh/m²/day) - varies by location
    avg_daily_irradiance: float = 3.5  # Default for Central Europe
    
    # Monthly solar irradiance factors (relative to annual average)
    # Default for Central/Northern Europe (much less sun in winter)
    monthly_irradiance_factors: List[float] = field(default_factory=lambda: [
        0.3,   # January (very low)
        0.5,   # February
        0.8,   # March
        1.2,   # April (good)
        1.4,   # May (excellent)
        1.5,   # June (peak)
        1.5,   # July (peak)
        1.3,   # August (very good)
        1.0,   # September (good)
        0.7,   # October
        0.4,   # November (low)
        0.25   # December (very low)
    ])
    
    def estimate_annual_production(self, year: int = 0) -> float:
        """Estimate annual energy production in kWh accounting for seasonal variation"""
        # Performance ratio considering all losses
        degradation_factor = (1 - self.annual_degradation_rate) ** year
        
        # Calculate monthly production and sum for annual
        annual_production = 0
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        for month_idx, (days, factor) in enumerate(zip(days_in_month, self.monthly_irradiance_factors)):
            monthly_irradiance = self.avg_daily_irradiance * factor
            daily_production = self.peak_power_kw * monthly_irradiance * self.system_efficiency
            monthly_production = daily_production * days
            annual_production += monthly_production
        
        return annual_production * degradation_factor
    
    def estimate_daily_production(self, year: int = 0, month: int = None) -> float:
        """Estimate daily production in kWh for a specific month"""
        degradation_factor = (1 - self.annual_degradation_rate) ** year
        
        if month is not None and 1 <= month <= 12:
            # Calculate for specific month
            monthly_irradiance = self.avg_daily_irradiance * self.monthly_irradiance_factors[month - 1]
            daily_production = self.peak_power_kw * monthly_irradiance * self.system_efficiency
            return daily_production * degradation_factor
        
        # Return annual average
        return self.estimate_annual_production(year) / 365
    
    def estimate_monthly_production(self, year: int = 0, month: int = 6) -> float:
        """Estimate total production for a specific month"""
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        daily = self.estimate_daily_production(year, month)
        return daily * days_in_month[month - 1]


@dataclass
class BatterySpecs:
    """Battery storage specifications"""
    capacity_kwh: float  # Usable capacity in kWh
    installation_cost: float  # EUR (total battery cost)
    depth_of_discharge: float = 0.9  # 90% usable capacity
    efficiency: float = 0.95  # Round-trip efficiency (charge/discharge)
    lifetime_cycles: int = 6000  # Number of full charge cycles
    lifetime_years: int = 10
    
    def get_usable_capacity(self) -> float:
        """Get usable battery capacity"""
        return self.capacity_kwh * self.depth_of_discharge


@dataclass
class EVProfile:
    """Electric Vehicle charging profile"""
    enabled: bool = False
    battery_capacity_kwh: float = 60.0  # Typical EV battery (e.g., 60 kWh)
    charging_power_kw: float = 7.0  # Typical home charger (7 kW)
    daily_driving_kwh: float = 15.0  # Average daily consumption (e.g., 60 km at 25 kWh/100km)
    
    # Charging hours (when EV is plugged in and charging)
    # Default: evening charging from 19:00 to 07:00 next day
    charging_hours: List[int] = field(default_factory=lambda: [19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6])
    
    def get_hourly_ev_consumption(self, hour: int, month: int = 6) -> float:
        """Get EV charging consumption for a specific hour"""
        if not self.enabled:
            return 0.0
        
        if hour not in self.charging_hours:
            return 0.0
        
        # Distribute daily charging across charging hours
        # Reduce in summer (less heating), increase in winter
        seasonal_factor = 1.0 - 0.2 * math.cos((month - 1) * math.pi / 6)  # 0.8 to 1.2
        adjusted_daily = self.daily_driving_kwh * seasonal_factor
        
        # Distribute evenly across charging hours
        return adjusted_daily / len(self.charging_hours)


@dataclass
class ConsumptionProfile:
    """Energy consumption profile"""
    monthly_consumption_kwh: float
    
    # Consumption pattern (fraction of daily consumption per hour)
    # Default assumes higher consumption during evening/morning
    hourly_pattern: List[float] = field(default_factory=lambda: [
        0.03, 0.02, 0.02, 0.02, 0.02, 0.03,  # 00:00-05:59 (night)
        0.04, 0.05, 0.05, 0.04, 0.03, 0.03,  # 06:00-11:59 (morning)
        0.03, 0.03, 0.03, 0.03, 0.04, 0.05,  # 12:00-17:59 (afternoon)
        0.06, 0.08, 0.08, 0.07, 0.05, 0.04   # 18:00-23:59 (evening peak)
    ])
    
    # Monthly variation factors (1.0 = average month)
    # Default assumes higher consumption in winter (heating) and summer (cooling)
    monthly_factors: List[float] = field(default_factory=lambda: [
        1.2,   # January (winter heating)
        1.15,  # February
        1.1,   # March
        0.95,  # April (mild)
        0.85,  # May
        0.8,   # June (low consumption)
        0.8,   # July
        0.85,  # August
        0.9,   # September
        0.95,  # October
        1.1,   # November
        1.2    # December (winter heating)
    ])
    
    def get_daily_consumption(self, month: int = None) -> float:
        """Get daily consumption in kWh for a specific month"""
        base_daily = self.monthly_consumption_kwh / 30
        
        if month is not None and 1 <= month <= 12:
            return base_daily * self.monthly_factors[month - 1]
        
        return base_daily
    
    def get_annual_consumption(self) -> float:
        """Get annual consumption in kWh"""
        return self.monthly_consumption_kwh * 12
    
    def get_hourly_consumption(self, hour: int, month: int = None) -> float:
        """Get consumption for a specific hour"""
        daily = self.get_daily_consumption(month)
        return daily * self.hourly_pattern[hour % 24]


@dataclass
class NordPoolPrice:
    """Nord Pool spot price data"""
    # Average selling price for excess energy (EUR/kWh)
    # This is simplified - in reality, you'd fetch actual hourly prices
    average_price: float = 0.05  # EUR/kWh
    
    # Hourly variation pattern (multiplier on average)
    hourly_multipliers: List[float] = field(default_factory=lambda: [
        0.7, 0.6, 0.6, 0.6, 0.7, 0.8,   # 00:00-05:59 (low demand)
        0.9, 1.0, 1.1, 1.2, 1.3, 1.2,   # 06:00-11:59 (morning ramp)
        1.1, 1.0, 0.9, 0.9, 1.0, 1.2,   # 12:00-17:59 (midday/afternoon)
        1.4, 1.5, 1.4, 1.2, 1.0, 0.8    # 18:00-23:59 (evening peak)
    ])
    
    def get_hourly_price(self, hour: int) -> float:
        """Get selling price for a specific hour"""
        return self.average_price * self.hourly_multipliers[hour % 24]


class PVFeasibilityCalculator:
    """Main calculator for PV system feasibility analysis"""
    
    def __init__(
        self,
        tariff: ElectricityTariff,
        consumption: ConsumptionProfile,
        pv_system: Optional[PVSystemSpecs] = None,
        battery: Optional[BatterySpecs] = None,
        nord_pool: Optional[NordPoolPrice] = None,
        ev_profile: Optional[EVProfile] = None
    ):
        self.tariff = tariff
        self.consumption = consumption
        self.pv_system = pv_system
        self.battery = battery
        self.nord_pool = nord_pool or NordPoolPrice()
        self.ev_profile = ev_profile or EVProfile()
    
    def get_recommended_battery_capacity(self) -> Dict:
        """Calculate recommended battery capacity based on daily consumption"""
        daily_household = self.consumption.get_daily_consumption()
        daily_ev = self.ev_profile.daily_driving_kwh if self.ev_profile.enabled else 0
        total_daily = daily_household + daily_ev
        
        # Recommended: 50-80% of daily consumption (best case scenario)
        # This accounts for the fact that not all consumption happens when battery is available
        min_recommended = total_daily * 0.5
        optimal_recommended = total_daily * 0.65
        max_recommended = total_daily * 0.8
        
        return {
            'daily_household_kwh': daily_household,
            'daily_ev_kwh': daily_ev,
            'total_daily_kwh': total_daily,
            'min_recommended_kwh': min_recommended,
            'optimal_recommended_kwh': optimal_recommended,
            'max_recommended_kwh': max_recommended
        }
    
    def calculate_baseline_costs(self) -> Dict:
        """Calculate current electricity costs without PV system"""
        # Household electricity costs
        household_annual_cost = self.tariff.get_annual_cost(self.consumption.monthly_consumption_kwh)
        
        # EV electricity costs (if EV is enabled)
        ev_annual_cost = 0
        if self.ev_profile.enabled:
            annual_ev_kwh = self.ev_profile.daily_driving_kwh * 365
            ev_annual_cost = annual_ev_kwh * self.tariff.get_total_cost_per_kwh()
        
        # Total costs
        total_annual_cost = household_annual_cost + ev_annual_cost
        monthly_cost = total_annual_cost / 12
        
        return {
            'annual_cost': total_annual_cost,
            'monthly_cost': monthly_cost,
            'cost_per_kwh': self.tariff.get_total_cost_per_kwh(),
            'annual_consumption': self.consumption.get_annual_consumption(),
            'household_annual_cost': household_annual_cost,
            'ev_annual_cost': ev_annual_cost
        }
    
    def simulate_daily_energy_flow(self, with_battery: bool = False, month: int = 6) -> Dict:
        """
        Simulate energy flow for an average day in a specific month
        Returns: consumption from grid, PV self-consumption, excess to grid, battery usage, EV charging
        
        Args:
            with_battery: Whether to include battery storage
            month: Month of year (1-12) for seasonal calculations
        """
        if not self.pv_system:
            return None
        
        daily_consumption = self.consumption.get_daily_consumption(month)
        daily_pv_production = self.pv_system.estimate_daily_production(month=month)
        
        # Simplified hourly simulation
        # PV production pattern (0 at night, peak at noon)
        pv_hourly_pattern = [
            0, 0, 0, 0, 0, 0,  # 00:00-05:59
            0.02, 0.05, 0.08, 0.10, 0.12, 0.13,  # 06:00-11:59
            0.14, 0.13, 0.12, 0.10, 0.06, 0.03,  # 12:00-17:59
            0.01, 0, 0, 0, 0, 0  # 18:00-23:59
        ]
        
        grid_import_household = 0
        grid_import_ev = 0
        pv_self_consumption = 0
        excess_to_grid = 0
        battery_charge = 0
        battery_discharge = 0
        ev_charged_kwh = 0
        
        battery_state = 0  # Current battery charge (kWh)
        battery_capacity = self.battery.get_usable_capacity() if (with_battery and self.battery) else 0
        
        for hour in range(24):
            # Household consumption (not including EV)
            household_consumption = self.consumption.get_hourly_consumption(hour, month)
            
            # EV charging (separate tracking)
            ev_consumption = self.ev_profile.get_hourly_ev_consumption(hour, month)
            
            pv_production = daily_pv_production * pv_hourly_pattern[hour]
            
            # Step 1: Try to cover household consumption with PV
            household_balance = pv_production - household_consumption
            
            if household_balance > 0:  # Excess PV production
                pv_self_consumption += household_consumption
                excess = household_balance
                
                # Charge battery with excess PV
                if with_battery and battery_state < battery_capacity:
                    charge_amount = min(excess, battery_capacity - battery_state)
                    charge_amount_actual = charge_amount * (self.battery.efficiency if self.battery else 0)
                    battery_state += charge_amount_actual
                    battery_charge += charge_amount_actual
                    excess -= charge_amount
                
                # Remaining excess to grid
                excess_to_grid += excess
                
            else:  # Need more energy for household
                pv_self_consumption += pv_production
                deficit = -household_balance
                
                # Try to cover household deficit with battery
                if with_battery and battery_state > 0:
                    discharge_amount = min(deficit, battery_state)
                    discharge_amount_actual = discharge_amount * (self.battery.efficiency if self.battery else 0)
                    battery_state -= discharge_amount
                    battery_discharge += discharge_amount_actual
                    deficit -= discharge_amount_actual
                
                # Remaining household deficit from grid
                grid_import_household += deficit
            
            # Step 2: EV charging - can use battery or grid
            if ev_consumption > 0:
                ev_charged_kwh += ev_consumption
                
                # Try to charge EV from battery first (if available)
                if with_battery and battery_state > 0:
                    from_battery = min(ev_consumption, battery_state)
                    from_battery_actual = from_battery * (self.battery.efficiency if self.battery else 0)
                    battery_state -= from_battery
                    battery_discharge += from_battery_actual
                    
                    # Remaining EV charging from grid
                    remaining_ev = ev_consumption - from_battery_actual
                    grid_import_ev += remaining_ev
                else:
                    # All EV charging from grid
                    grid_import_ev += ev_consumption
        
        total_consumption = daily_consumption + ev_charged_kwh
        total_grid_import = grid_import_household + grid_import_ev
        
        return {
            'grid_import_kwh': total_grid_import,
            'grid_import_household_kwh': grid_import_household,
            'grid_import_ev_kwh': grid_import_ev,
            'pv_self_consumption_kwh': pv_self_consumption,
            'excess_to_grid_kwh': excess_to_grid,
            'battery_charge_kwh': battery_charge,
            'battery_discharge_kwh': battery_discharge,
            'ev_charged_kwh': ev_charged_kwh,
            'total_consumption_kwh': total_consumption,
            'household_consumption_kwh': daily_consumption,
            'self_sufficiency_ratio': pv_self_consumption / daily_consumption if daily_consumption > 0 else 0,
            'total_self_sufficiency_ratio': pv_self_consumption / total_consumption if total_consumption > 0 else 0
        }
    
    def calculate_annual_costs_with_pv(self, with_battery: bool = False) -> Dict:
        """Calculate annual costs with PV system using monthly simulations"""
        if not self.pv_system:
            return None
        
        # Simulate each month separately to account for seasonal variations
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        annual_grid_import = 0
        annual_grid_import_household = 0
        annual_grid_import_ev = 0
        annual_excess_to_grid = 0
        annual_pv_self_consumption = 0
        annual_ev_charged = 0
        annual_household_consumption = 0
        
        for month in range(1, 13):
            daily_flow = self.simulate_daily_energy_flow(with_battery, month)
            days = days_in_month[month - 1]
            
            annual_grid_import += daily_flow['grid_import_kwh'] * days
            annual_grid_import_household += daily_flow['grid_import_household_kwh'] * days
            annual_grid_import_ev += daily_flow['grid_import_ev_kwh'] * days
            annual_excess_to_grid += daily_flow['excess_to_grid_kwh'] * days
            annual_pv_self_consumption += daily_flow['pv_self_consumption_kwh'] * days
            annual_ev_charged += daily_flow['ev_charged_kwh'] * days
            annual_household_consumption += daily_flow['household_consumption_kwh'] * days
        
        # Costs
        annual_variable_cost = annual_grid_import * self.tariff.get_total_cost_per_kwh()
        annual_fixed_cost = self.tariff.get_monthly_fixed_cost() * 12
        
        # Revenue from excess energy (including transfer cost for selling)
        # Assume average Nord Pool price minus transfer cost
        net_selling_price = self.nord_pool.average_price - self.tariff.transfer_cost * (1 + self.tariff.vat_rate)
        net_selling_price = max(0, net_selling_price)  # Can't be negative
        
        annual_revenue = annual_excess_to_grid * net_selling_price
        
        net_annual_cost = annual_variable_cost + annual_fixed_cost - annual_revenue
        
        total_consumption = annual_household_consumption + annual_ev_charged
        
        return {
            'annual_cost': net_annual_cost,
            'monthly_cost': net_annual_cost / 12,
            'annual_grid_import': annual_grid_import,
            'annual_grid_import_household': annual_grid_import_household,
            'annual_grid_import_ev': annual_grid_import_ev,
            'annual_excess_to_grid': annual_excess_to_grid,
            'annual_revenue': annual_revenue,
            'annual_ev_charged': annual_ev_charged,
            'self_sufficiency_ratio': annual_pv_self_consumption / annual_household_consumption if annual_household_consumption > 0 else 0,
            'total_self_sufficiency_ratio': annual_pv_self_consumption / total_consumption if total_consumption > 0 else 0
        }
    
    def calculate_roi(self, with_battery: bool = False) -> Dict:
        """Calculate ROI and payback period"""
        if not self.pv_system:
            return None
        
        baseline = self.calculate_baseline_costs()
        with_pv = self.calculate_annual_costs_with_pv(with_battery)
        
        # Initial investment
        initial_cost = self.pv_system.installation_cost
        if with_battery and self.battery:
            initial_cost += self.battery.installation_cost
        
        # Annual savings
        annual_savings = baseline['annual_cost'] - with_pv['annual_cost']
        
        # Simple payback period
        simple_payback_years = initial_cost / annual_savings if annual_savings > 0 else float('inf')
        
        # Calculate NPV and IRR (simplified, assuming constant savings)
        discount_rate = 0.05  # 5% discount rate
        project_lifetime = min(self.pv_system.lifetime_years, 25)
        
        npv = -initial_cost
        for year in range(1, project_lifetime + 1):
            # Account for degradation
            year_savings = annual_savings * ((1 - self.pv_system.annual_degradation_rate) ** year)
            npv += year_savings / ((1 + discount_rate) ** year)
        
        # ROI over project lifetime
        total_savings = sum(annual_savings * ((1 - self.pv_system.annual_degradation_rate) ** year) 
                           for year in range(1, project_lifetime + 1))
        roi_percent = (total_savings - initial_cost) / initial_cost * 100
        
        return {
            'initial_investment': initial_cost,
            'annual_savings': annual_savings,
            'simple_payback_years': simple_payback_years,
            'npv_25_years': npv,
            'roi_percent': roi_percent,
            'project_lifetime_years': project_lifetime,
            'baseline_annual_cost': baseline['annual_cost'],
            'with_pv_annual_cost': with_pv['annual_cost']
        }
    
    def generate_report(self) -> str:
        """Generate comprehensive feasibility report"""
        report = []
        report.append("=" * 80)
        report.append("PV SYSTEM FEASIBILITY ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Baseline costs
        report.append("CURRENT SITUATION (WITHOUT PV)")
        report.append("-" * 80)
        baseline = self.calculate_baseline_costs()
        report.append(f"Annual Household Consumption: {baseline['annual_consumption']:.0f} kWh")
        
        if self.ev_profile.enabled:
            annual_ev_consumption = self.ev_profile.daily_driving_kwh * 365
            report.append(f"Annual EV Consumption: {annual_ev_consumption:.0f} kWh")
            report.append(f"Total Annual Consumption: {baseline['annual_consumption'] + annual_ev_consumption:.0f} kWh")
            report.append("")
            report.append("EV Charging Profile:")
            report.append(f"  Daily Driving: {self.ev_profile.daily_driving_kwh:.1f} kWh (~{self.ev_profile.daily_driving_kwh * 4:.0f} km)")
            report.append(f"  Charging Hours: {len(self.ev_profile.charging_hours)} hours/day (evening/night)")
            report.append(f"  Note: EV can use battery (if available) or grid power")
        
        report.append("")
        report.append(f"Electricity Costs (without PV):")
        if self.ev_profile.enabled:
            report.append(f"  Household: €{baseline['household_annual_cost']:.2f}/year")
            report.append(f"  EV Charging: €{baseline['ev_annual_cost']:.2f}/year")
        report.append(f"Annual Cost: €{baseline['annual_cost']:.2f}")
        report.append(f"Monthly Cost: €{baseline['monthly_cost']:.2f}")
        report.append(f"Effective Cost per kWh: €{baseline['cost_per_kwh']:.4f}")
        report.append("")
        
        if self.pv_system:
            # PV system specs
            report.append("PV SYSTEM SPECIFICATIONS")
            report.append("-" * 80)
            report.append(f"System Size: {self.pv_system.peak_power_kw:.1f} kWp")
            report.append(f"Installation Cost: €{self.pv_system.installation_cost:.2f}")
            report.append(f"Estimated Annual Production: {self.pv_system.estimate_annual_production():.0f} kWh")
            report.append(f"Estimated Daily Production: {self.pv_system.estimate_daily_production():.1f} kWh")
            report.append("")
            
            # With PV, without battery
            report.append("SCENARIO 1: PV SYSTEM WITHOUT BATTERY")
            report.append("-" * 80)
            pv_no_battery = self.calculate_annual_costs_with_pv(with_battery=False)
            report.append(f"Annual Grid Import: {pv_no_battery['annual_grid_import']:.0f} kWh")
            if self.ev_profile.enabled:
                report.append(f"  - Household: {pv_no_battery['annual_grid_import_household']:.0f} kWh")
                report.append(f"  - EV Charging: {pv_no_battery['annual_grid_import_ev']:.0f} kWh")
            report.append(f"Annual Excess to Grid: {pv_no_battery['annual_excess_to_grid']:.0f} kWh")
            report.append(f"Household Self-Sufficiency: {pv_no_battery['self_sufficiency_ratio']*100:.1f}%")
            if self.ev_profile.enabled:
                report.append(f"Total Self-Sufficiency (incl. EV): {pv_no_battery['total_self_sufficiency_ratio']*100:.1f}%")
            report.append(f"Annual Cost: €{pv_no_battery['annual_cost']:.2f}")
            report.append(f"Annual Revenue (from excess): €{pv_no_battery['annual_revenue']:.2f}")
            report.append(f"Monthly Cost: €{pv_no_battery['monthly_cost']:.2f}")
            report.append("")
            
            roi_no_battery = self.calculate_roi(with_battery=False)
            report.append("Financial Analysis:")
            report.append(f"  Initial Investment: €{roi_no_battery['initial_investment']:.2f}")
            report.append(f"  Annual Savings: €{roi_no_battery['annual_savings']:.2f}")
            report.append(f"  Simple Payback Period: {roi_no_battery['simple_payback_years']:.1f} years")
            report.append(f"  NPV (25 years, 5% discount): €{roi_no_battery['npv_25_years']:.2f}")
            report.append(f"  ROI over {roi_no_battery['project_lifetime_years']} years: {roi_no_battery['roi_percent']:.1f}%")
            report.append("")
            
            # With PV and battery
            if self.battery:
                report.append("SCENARIO 2: PV SYSTEM WITH BATTERY STORAGE")
                report.append("-" * 80)
                report.append(f"Battery Capacity: {self.battery.capacity_kwh:.1f} kWh (usable: {self.battery.get_usable_capacity():.1f} kWh)")
                report.append(f"Battery Cost: €{self.battery.installation_cost:.2f}")
                report.append("")
                
                pv_with_battery = self.calculate_annual_costs_with_pv(with_battery=True)
                report.append(f"Annual Grid Import: {pv_with_battery['annual_grid_import']:.0f} kWh")
                if self.ev_profile.enabled:
                    report.append(f"  - Household: {pv_with_battery['annual_grid_import_household']:.0f} kWh")
                    report.append(f"  - EV Charging: {pv_with_battery['annual_grid_import_ev']:.0f} kWh")
                report.append(f"Annual Excess to Grid: {pv_with_battery['annual_excess_to_grid']:.0f} kWh")
                report.append(f"Household Self-Sufficiency: {pv_with_battery['self_sufficiency_ratio']*100:.1f}%")
                if self.ev_profile.enabled:
                    report.append(f"Total Self-Sufficiency (incl. EV): {pv_with_battery['total_self_sufficiency_ratio']*100:.1f}%")
                report.append(f"Annual Cost: €{pv_with_battery['annual_cost']:.2f}")
                report.append(f"Annual Revenue (from excess): €{pv_with_battery['annual_revenue']:.2f}")
                report.append(f"Monthly Cost: €{pv_with_battery['monthly_cost']:.2f}")
                report.append("")
                
                roi_with_battery = self.calculate_roi(with_battery=True)
                report.append("Financial Analysis:")
                report.append(f"  Initial Investment: €{roi_with_battery['initial_investment']:.2f}")
                report.append(f"  Annual Savings: €{roi_with_battery['annual_savings']:.2f}")
                report.append(f"  Simple Payback Period: {roi_with_battery['simple_payback_years']:.1f} years")
                report.append(f"  NPV (25 years, 5% discount): €{roi_with_battery['npv_25_years']:.2f}")
                report.append(f"  ROI over {roi_with_battery['project_lifetime_years']} years: {roi_with_battery['roi_percent']:.1f}%")
                report.append("")
                
                # Comparison
                report.append("BATTERY INVESTMENT ANALYSIS")
                report.append("-" * 80)
                battery_cost = self.battery.installation_cost
                additional_savings = roi_with_battery['annual_savings'] - roi_no_battery['annual_savings']
                battery_payback = battery_cost / additional_savings if additional_savings > 0 else float('inf')
                report.append(f"Additional Investment: €{battery_cost:.2f}")
                report.append(f"Additional Annual Savings: €{additional_savings:.2f}")
                report.append(f"Battery Payback Period: {battery_payback:.1f} years")
                
                if battery_payback < self.battery.lifetime_years:
                    report.append(f"✓ Battery is ECONOMICALLY VIABLE (payback within {self.battery.lifetime_years} year lifetime)")
                else:
                    report.append(f"✗ Battery may NOT be economically viable (payback exceeds {self.battery.lifetime_years} year lifetime)")
                report.append("")
        
        report.append("=" * 80)
        report.append("RECOMMENDATIONS")
        report.append("=" * 80)
        
        if self.pv_system:
            roi = self.calculate_roi(with_battery=False)
            if roi['simple_payback_years'] < 10:
                report.append("✓ PV system installation is HIGHLY RECOMMENDED")
                report.append(f"  - Payback in {roi['simple_payback_years']:.1f} years")
                report.append(f"  - Positive NPV: €{roi['npv_25_years']:.2f}")
            elif roi['simple_payback_years'] < 15:
                report.append("✓ PV system installation is RECOMMENDED")
                report.append(f"  - Reasonable payback period: {roi['simple_payback_years']:.1f} years")
            else:
                report.append("⚠ PV system installation may not be optimal")
                report.append(f"  - Long payback period: {roi['simple_payback_years']:.1f} years")
                report.append("  - Consider reviewing system size or costs")
            
            if self.battery:
                roi_battery = self.calculate_roi(with_battery=True)
                roi_no_battery = self.calculate_roi(with_battery=False)
                if roi_battery['simple_payback_years'] < roi_no_battery['simple_payback_years'] * 1.2:
                    report.append("")
                    report.append("✓ Battery storage adds value and is recommended")
                else:
                    report.append("")
                    report.append("⚠ Battery storage significantly increases payback period")
                    report.append("  - Consider starting without battery and adding later")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Example usage of the PV calculator"""
    print("PV System Feasibility Calculator")
    print("=" * 80)
    print()
    
    # Example: Configure electricity tariff
    tariff = ElectricityTariff(
        power_amperes=25,  # 25A connection
        power_cost_per_ampere=0.50,  # €0.50 per ampere
        electricity_cost=0.08,  # €0.08/kWh
        transfer_cost=0.04,  # €0.04/kWh
        service_cost=0.01,  # €0.01/kWh
        monthly_service_fee=5.0,  # €5/month
        vat_rate=0.21  # 21% VAT
    )
    
    # Example: Monthly consumption
    consumption = ConsumptionProfile(
        monthly_consumption_kwh=500  # 500 kWh per month (household only)
    )
    
    # Example: PV system (5 kWp system)
    pv_system = PVSystemSpecs(
        peak_power_kw=5.0,
        installation_cost=7000,  # €7000 for 5kWp system
        avg_daily_irradiance=3.5  # Central Europe average
    )
    
    # Example: Battery system (optional)
    battery = BatterySpecs(
        capacity_kwh=7.0,  # 7 kWh battery
        installation_cost=4000  # €4000
    )
    
    # Nord Pool pricing
    nord_pool = NordPoolPrice(
        average_price=0.06  # €0.06/kWh average selling price
    )
    
    # Example: EV charging profile (optional)
    # Uncomment to include EV in the calculation
    ev_profile = EVProfile(
        enabled=True,  # Set to False to exclude EV
        daily_driving_kwh=15.0,  # ~60 km per day at 25 kWh/100km
        charging_power_kw=7.0,  # 7 kW home charger
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
    
    # Generate and print report
    report = calculator.generate_report()
    print(report)
    
    print("\n")
    print("Note: This is an example calculation with seasonal variations and EV charging.")
    print("Adjust the parameters above to match your specific situation.")
    print("\nNEW FEATURES:")
    print("- Seasonal solar production (much lower in winter)")
    print("- Seasonal consumption patterns (higher in winter/summer)")
    print("- EV charging support (evening charging from grid)")
    print("- Battery prioritizes household loads over EV")


if __name__ == "__main__":
    main()

