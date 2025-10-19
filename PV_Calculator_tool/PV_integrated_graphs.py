"""
Integrated Visualization Graphs
Creates comprehensive energy flow visualizations combining:
- Consumption patterns
- Solar generation
- Battery storage/discharge
- Grid import/export
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple


class IntegratedEnergyGraphs:
    """Generate comprehensive energy flow visualizations"""
    
    def __init__(self, consumption_gen, solar_gen, battery_calc, 
                 household_profile, solar_system):
        """
        Initialize with generators and profiles
        
        Args:
            consumption_gen: ConsumptionPatternGenerator instance
            solar_gen: SolarGenerationCalculator instance
            battery_calc: BatteryFlowCalculator instance
            household_profile: HouseholdProfile
            solar_system: SolarSystemProfile
        """
        self.consumption_gen = consumption_gen
        self.solar_gen = solar_gen
        self.battery_calc = battery_calc
        self.household_profile = household_profile
        self.solar_system = solar_system
    
    def plot_daily_energy_flow(self, month: int, day_of_week: int = 0, 
                               initial_soc: float = None,
                               figsize: Tuple = (14, 10),
                               import_rate: float = 0.15,
                               export_rate: float = 0.02) -> plt.Figure:
        """
        Complete daily energy flow visualization
        Shows consumption, generation, battery SOC, and grid flows
        
        Args:
            month: Month (1-12)
            day_of_week: Day of week (0=Monday, 6=Sunday)
            initial_soc: Initial battery SOC (kWh), defaults to 50% if None
            figsize: Figure size
            import_rate: Cost per kWh for grid import (EUR/kWh)
            export_rate: Revenue per kWh for grid export (EUR/kWh)
        
        Returns:
            matplotlib Figure
        """
        # Get battery flow results
        result = self.battery_calc.simulate_daily_flow(
            self.consumption_gen, self.solar_gen,
            self.household_profile, self.solar_system,
            month, day_of_week, initial_soc=initial_soc
        )
        
        hours = list(range(24))
        day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 
                    'Saturday', 'Sunday'][day_of_week]
        month_name = datetime(2024, month, 1).strftime('%B')
        
        fig, axes = plt.subplots(4, 1, figsize=figsize, sharex=True)
        fig.suptitle(f'Daily Energy Flow: {day_name} in {month_name}\n'
                    f'{self.household_profile.pattern_type.replace("_", " ").title()}',
                    fontsize=14, fontweight='bold')
        
        # Plot 1: Consumption vs Generation
        ax1 = axes[0]
        ax1.fill_between(hours, result.hourly_generation, alpha=0.3, 
                        color='gold', label='Solar Generation')
        ax1.plot(hours, result.hourly_generation, color='orange', 
                linewidth=2, marker='o', markersize=3)
        ax1.fill_between(hours, result.hourly_consumption, alpha=0.3, 
                        color='steelblue', label='Consumption')
        ax1.plot(hours, result.hourly_consumption, color='darkblue', 
                linewidth=2, marker='s', markersize=3)
        ax1.set_ylabel('Power (kWh)', fontsize=10)
        ax1.set_title('Energy Generation vs Consumption', fontsize=11, pad=10)
        ax1.legend(loc='upper left', fontsize=9)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(bottom=0)
        
        # Plot 2: Battery State
        ax2 = axes[1]
        ax2.fill_between(hours, result.hourly_battery_soc, alpha=0.3, color='green')
        ax2.plot(hours, result.hourly_battery_soc, color='darkgreen', 
                linewidth=2, marker='o', markersize=3)
        ax2.axhline(y=self.battery_calc.battery_capacity, color='red', 
                   linestyle='--', alpha=0.5, label='Max Capacity')
        ax2.axhline(y=self.battery_calc.min_soc, color='orange', 
                   linestyle='--', alpha=0.5, label='Min SOC')
        ax2.set_ylabel('Battery (kWh)', fontsize=10)
        ax2.set_title('Battery State of Charge', fontsize=11, pad=10)
        ax2.legend(loc='upper right', fontsize=9)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, self.battery_calc.battery_capacity * 1.1)
        
        # Plot 3: Battery Charging/Discharging
        ax3 = axes[2]
        ax3.bar(hours, result.hourly_battery_charge, alpha=0.6, 
               color='limegreen', label='Charging', width=0.8)
        ax3.bar(hours, [-x for x in result.hourly_battery_discharge], alpha=0.6, 
               color='coral', label='Discharging', width=0.8)
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax3.set_ylabel('Power (kWh)', fontsize=10)
        ax3.set_title('Battery Charge/Discharge', fontsize=11, pad=10)
        ax3.legend(loc='upper left', fontsize=9)
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Grid Import/Export
        ax4 = axes[3]
        ax4.bar(hours, [-x for x in result.hourly_grid_import], alpha=0.6, 
               color='red', label='Grid Import', width=0.8)
        ax4.bar(hours, result.hourly_grid_export, alpha=0.6, 
               color='green', label='Grid Export', width=0.8)
        ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax4.set_ylabel('Power (kWh)', fontsize=10)
        ax4.set_xlabel('Hour of Day', fontsize=10)
        ax4.set_title('Grid Import/Export', fontsize=11, pad=10)
        ax4.legend(loc='upper left', fontsize=9)
        ax4.grid(True, alpha=0.3)
        ax4.set_xticks(range(0, 24, 2))
        
        # Add EV charging indicators if EV is enabled
        if hasattr(self.household_profile, 'ev_profile') and self.household_profile.ev_profile and self.household_profile.ev_profile.enabled:
            ev_profile = self.household_profile.ev_profile
            
            # Check which hours have EV charging
            ev_hours = []
            for hour in range(24):
                # Check if this day charges (using day_of_week)
                if ev_profile.charging_days[day_of_week]:
                    if hour in ev_profile.charging_hours:
                        ev_hours.append(hour)
            
            if ev_hours:
                # Add EV charging indicator to consumption plot
                for hour in ev_hours:
                    ax1.axvspan(hour - 0.4, hour + 0.4, alpha=0.15, color='purple', zorder=0)
                
                # Add legend entry for EV charging
                from matplotlib.patches import Patch
                ev_patch = Patch(facecolor='purple', alpha=0.15, label='EV Charging')
                handles, labels = ax1.get_legend_handles_labels()
                handles.append(ev_patch)
                labels.append('EV Charging')
                ax1.legend(handles, labels, loc='upper left', fontsize=9)
                
                # Calculate EV charging info
                daily_km = ev_profile.weekly_distance_km / 7.0
                daily_ev_kwh = (daily_km / 100.0) * ev_profile.consumption_per_100km
                
                # Add EV info to summary
                ev_start = min(ev_hours)
                ev_end = max(ev_hours) + 1
                if ev_end == 24:
                    ev_end = 0
                
                ev_info = (f'\n\nEV Charging:\n'
                          f'Daily: {daily_ev_kwh:.2f} kWh\n'
                          f'Period: {ev_start:02d}:00-{ev_end:02d}:00\n'
                          f'Hours: {len(ev_hours)}h')
        else:
            ev_info = ''
        
        # Calculate monetary balance
        export_revenue = result.total_grid_export * export_rate
        import_cost = result.total_grid_import * import_rate
        net_money = export_revenue - import_cost
        
        # Add summary metrics
        textstr = (f'Daily Totals:\n'
                  f'Consumption: {result.total_consumption:.1f} kWh\n'
                  f'Generation: {result.total_generation:.1f} kWh\n'
                  f'Self-sufficiency: {result.self_sufficiency_ratio:.1f}%\n'
                  f'Grid Import: {result.total_grid_import:.1f} kWh\n'
                  f'Grid Export: {result.total_grid_export:.1f} kWh\n'
                  f'Battery Cycles: {result.battery_cycles:.2f}\n'
                  f'\n'
                  f'Monetary Balance:\n'
                  f'Export Revenue: {export_revenue:.2f} EUR\n'
                  f'Import Cost: {import_cost:.2f} EUR\n'
                  f'Net Balance: {net_money:.2f} EUR' + ev_info)
        
        fig.text(0.98, 0.02, textstr, fontsize=9, 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3),
                verticalalignment='bottom', horizontalalignment='right',
                family='monospace')
        
        plt.tight_layout()
        return fig
    
    def plot_weekly_comparison(self, month: int = 6, 
                              figsize: Tuple = (16, 10)) -> plt.Figure:
        """
        Weekly energy flow comparison (Mon-Sun)
        
        Args:
            month: Month to simulate (1-12)
            figsize: Figure size
        
        Returns:
            matplotlib Figure
        """
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        results = []
        
        # Simulate all 7 days
        for day_idx in range(7):
            result = self.battery_calc.simulate_daily_flow(
                self.consumption_gen, self.solar_gen,
                self.household_profile, self.solar_system,
                month, day_idx
            )
            results.append(result)
        
        fig, axes = plt.subplots(3, 1, figsize=figsize, sharex=True)
        month_name = datetime(2024, month, 1).strftime('%B')
        fig.suptitle(f'Weekly Energy Flow Comparison - {month_name}\n'
                    f'{self.household_profile.pattern_type.replace("_", " ").title()}',
                    fontsize=14, fontweight='bold')
        
        # Plot 1: Daily totals
        ax1 = axes[0]
        consumption_totals = [r.total_consumption for r in results]
        generation_totals = [r.total_generation for r in results]
        self_consumption_totals = [r.total_self_consumption for r in results]
        
        x = np.arange(len(days))
        width = 0.25
        
        ax1.bar(x - width, consumption_totals, width, label='Consumption', 
               alpha=0.8, color='steelblue')
        ax1.bar(x, generation_totals, width, label='Generation', 
               alpha=0.8, color='orange')
        ax1.bar(x + width, self_consumption_totals, width, label='Self-Consumption', 
               alpha=0.8, color='green')
        
        ax1.set_ylabel('Energy (kWh)', fontsize=10)
        ax1.set_title('Daily Energy Totals', fontsize=11, pad=10)
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.set_xticks(x)
        ax1.set_xticklabels(days)
        
        # Plot 2: Self-sufficiency ratio
        ax2 = axes[1]
        self_sufficiency = [r.self_sufficiency_ratio for r in results]
        ax2.bar(x, self_sufficiency, alpha=0.8, color='green')
        ax2.axhline(y=100, color='red', linestyle='--', alpha=0.5, label='100%')
        ax2.set_ylabel('Self-Sufficiency (%)', fontsize=10)
        ax2.set_title('Daily Self-Sufficiency', fontsize=11, pad=10)
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.set_xticks(x)
        ax2.set_xticklabels(days)
        ax2.set_ylim(0, 110)
        
        # Plot 3: Grid flows
        ax3 = axes[2]
        grid_import = [r.total_grid_import for r in results]
        grid_export = [r.total_grid_export for r in results]
        
        ax3.bar(x - width/2, grid_export, width, label='Grid Export', 
               alpha=0.8, color='lightgreen')
        ax3.bar(x + width/2, [-g for g in grid_import], width, label='Grid Import', 
               alpha=0.8, color='lightcoral')
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax3.set_ylabel('Energy (kWh)', fontsize=10)
        ax3.set_xlabel('Day of Week', fontsize=10)
        ax3.set_title('Grid Import/Export', fontsize=11, pad=10)
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.set_xticks(x)
        ax3.set_xticklabels(days)
        
        plt.tight_layout()
        return fig
    
    def plot_seasonal_comparison(self, months: List[int] = [1, 4, 7, 10],
                                day_of_week: int = 0,
                                figsize: Tuple = (16, 12)) -> plt.Figure:
        """
        Compare energy flow across different seasons
        
        Args:
            months: List of months to compare
            day_of_week: Day of week (0=Monday, 6=Sunday)
            figsize: Figure size
        
        Returns:
            matplotlib Figure
        """
        results = {}
        month_names = []
        
        for month in months:
            result = self.battery_calc.simulate_daily_flow(
                self.consumption_gen, self.solar_gen,
                self.household_profile, self.solar_system,
                month, day_of_week
            )
            month_name = datetime(2024, month, 1).strftime('%B')
            results[month_name] = result
            month_names.append(month_name)
        
        fig, axes = plt.subplots(3, 2, figsize=figsize)
        day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 
                    'Saturday', 'Sunday'][day_of_week]
        fig.suptitle(f'Seasonal Energy Flow Comparison - {day_name}\n'
                    f'{self.household_profile.pattern_type.replace("_", " ").title()}',
                    fontsize=14, fontweight='bold')
        
        hours = list(range(24))
        
        # Plot each month in a 3x2 grid
        for idx, month_name in enumerate(month_names):
            if idx >= 6:  # Max 6 subplots
                break
            
            row = idx // 2
            col = idx % 2
            ax = axes[row, col]
            
            result = results[month_name]
            
            # Stacked area plot
            ax.fill_between(hours, 0, result.hourly_generation, 
                           alpha=0.3, color='gold', label='Solar Gen')
            ax.plot(hours, result.hourly_generation, color='orange', 
                   linewidth=2)
            ax.plot(hours, result.hourly_consumption, color='darkblue', 
                   linewidth=2, label='Consumption')
            ax.plot(hours, result.hourly_battery_soc, color='green', 
                   linewidth=1.5, linestyle='--', label='Battery SOC')
            
            ax.set_title(f'{month_name}', fontsize=11, fontweight='bold')
            ax.set_ylabel('Energy (kWh)', fontsize=9)
            if row == 2:
                ax.set_xlabel('Hour', fontsize=9)
            ax.legend(fontsize=8, loc='upper left')
            ax.grid(True, alpha=0.3)
            ax.set_xlim(0, 23)
            ax.set_ylim(bottom=0)
            
            # Add metrics text
            textstr = (f'Self-suff: {result.self_sufficiency_ratio:.1f}%\n'
                      f'Import: {result.total_grid_import:.1f} kWh\n'
                      f'Export: {result.total_grid_export:.1f} kWh')
            ax.text(0.98, 0.97, textstr, transform=ax.transAxes,
                   fontsize=8, verticalalignment='top', 
                   horizontalalignment='right',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Hide unused subplots
        for idx in range(len(month_names), 6):
            row = idx // 2
            col = idx % 2
            axes[row, col].axis('off')
        
        plt.tight_layout()
        return fig
    
    def plot_annual_summary(self, figsize: Tuple = (16, 12)) -> plt.Figure:
        """
        Comprehensive annual energy flow summary
        Shows monthly totals for all metrics
        
        Returns:
            matplotlib Figure
        """
        months = range(1, 13)
        month_names = [datetime(2024, m, 1).strftime('%b') for m in months]
        
        # Collect monthly data (simulate representative days)
        monthly_consumption = []
        monthly_generation = []
        monthly_self_consumption = []
        monthly_grid_import = []
        monthly_grid_export = []
        monthly_self_sufficiency = []
        
        for month in months:
            # Simulate both weekday and weekend
            weekday_result = self.battery_calc.simulate_daily_flow(
                self.consumption_gen, self.solar_gen,
                self.household_profile, self.solar_system,
                month, 0  # Monday
            )
            weekend_result = self.battery_calc.simulate_daily_flow(
                self.consumption_gen, self.solar_gen,
                self.household_profile, self.solar_system,
                month, 5  # Saturday
            )
            
            # Average weekday/weekend (5 weekdays, 2 weekend days per week)
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1]
            weeks_in_month = days_in_month / 7
            
            monthly_cons = (weekday_result.total_consumption * 5 + 
                          weekend_result.total_consumption * 2) * weeks_in_month
            monthly_gen = (weekday_result.total_generation * 5 + 
                         weekend_result.total_generation * 2) * weeks_in_month
            monthly_self_cons = (weekday_result.total_self_consumption * 5 + 
                               weekend_result.total_self_consumption * 2) * weeks_in_month
            monthly_import = (weekday_result.total_grid_import * 5 + 
                            weekend_result.total_grid_import * 2) * weeks_in_month
            monthly_export = (weekday_result.total_grid_export * 5 + 
                            weekend_result.total_grid_export * 2) * weeks_in_month
            
            monthly_consumption.append(monthly_cons)
            monthly_generation.append(monthly_gen)
            monthly_self_consumption.append(monthly_self_cons)
            monthly_grid_import.append(monthly_import)
            monthly_grid_export.append(monthly_export)
            monthly_self_sufficiency.append(
                (monthly_self_cons / monthly_cons * 100) if monthly_cons > 0 else 0
            )
        
        fig, axes = plt.subplots(3, 2, figsize=figsize)
        fig.suptitle(f'Annual Energy Flow Summary\n'
                    f'{self.household_profile.pattern_type.replace("_", " ").title()} | '
                    f'Solar: {self.solar_system.peak_power_kw} kW | '
                    f'Battery: {self.battery_calc.battery_capacity} kWh',
                    fontsize=14, fontweight='bold')
        
        x = np.arange(len(month_names))
        
        # Plot 1: Monthly energy totals
        ax1 = axes[0, 0]
        ax1.plot(x, monthly_consumption, marker='o', linewidth=2, 
                label='Consumption', color='steelblue')
        ax1.plot(x, monthly_generation, marker='s', linewidth=2, 
                label='Generation', color='orange')
        ax1.plot(x, monthly_self_consumption, marker='^', linewidth=2, 
                label='Self-Consumption', color='green')
        ax1.set_ylabel('Energy (kWh)', fontsize=10)
        ax1.set_title('Monthly Energy Totals', fontsize=11, pad=10)
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(x)
        ax1.set_xticklabels(month_names)
        
        # Plot 2: Self-sufficiency ratio
        ax2 = axes[0, 1]
        ax2.bar(x, monthly_self_sufficiency, alpha=0.8, color='green')
        ax2.axhline(y=100, color='red', linestyle='--', alpha=0.5)
        ax2.set_ylabel('Self-Sufficiency (%)', fontsize=10)
        ax2.set_title('Monthly Self-Sufficiency', fontsize=11, pad=10)
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.set_xticks(x)
        ax2.set_xticklabels(month_names)
        ax2.set_ylim(0, 110)
        
        # Plot 3: Grid flows
        ax3 = axes[1, 0]
        width = 0.35
        ax3.bar(x - width/2, monthly_grid_import, width, label='Import', 
               alpha=0.8, color='lightcoral')
        ax3.bar(x + width/2, monthly_grid_export, width, label='Export', 
               alpha=0.8, color='lightgreen')
        ax3.set_ylabel('Energy (kWh)', fontsize=10)
        ax3.set_title('Monthly Grid Import/Export', fontsize=11, pad=10)
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.set_xticks(x)
        ax3.set_xticklabels(month_names)
        
        # Plot 4: Energy balance
        ax4 = axes[1, 1]
        energy_balance = [gen - cons for gen, cons in 
                         zip(monthly_generation, monthly_consumption)]
        colors = ['green' if b > 0 else 'red' for b in energy_balance]
        ax4.bar(x, energy_balance, alpha=0.8, color=colors)
        ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax4.set_ylabel('Energy Balance (kWh)', fontsize=10)
        ax4.set_title('Monthly Energy Balance (Gen - Cons)', fontsize=11, pad=10)
        ax4.grid(True, alpha=0.3, axis='y')
        ax4.set_xticks(x)
        ax4.set_xticklabels(month_names)
        
        # Plot 5: Cumulative energy flows
        ax5 = axes[2, 0]
        cumulative_cons = np.cumsum(monthly_consumption)
        cumulative_gen = np.cumsum(monthly_generation)
        cumulative_import = np.cumsum(monthly_grid_import)
        cumulative_export = np.cumsum(monthly_grid_export)
        
        ax5.plot(x, cumulative_cons, marker='o', linewidth=2, 
                label='Consumption', color='steelblue')
        ax5.plot(x, cumulative_gen, marker='s', linewidth=2, 
                label='Generation', color='orange')
        ax5.fill_between(x, cumulative_import, alpha=0.3, 
                        color='red', label='Grid Import')
        ax5.fill_between(x, cumulative_export, alpha=0.3, 
                        color='green', label='Grid Export')
        ax5.set_ylabel('Cumulative Energy (kWh)', fontsize=10)
        ax5.set_xlabel('Month', fontsize=10)
        ax5.set_title('Cumulative Energy Flows', fontsize=11, pad=10)
        ax5.legend(fontsize=9)
        ax5.grid(True, alpha=0.3)
        ax5.set_xticks(x)
        ax5.set_xticklabels(month_names)
        
        # Plot 6: Annual summary metrics
        ax6 = axes[2, 1]
        ax6.axis('off')
        
        total_cons = sum(monthly_consumption)
        total_gen = sum(monthly_generation)
        total_self_cons = sum(monthly_self_consumption)
        total_import = sum(monthly_grid_import)
        total_export = sum(monthly_grid_export)
        avg_self_suff = np.mean(monthly_self_sufficiency)
        
        summary_text = f"""
ANNUAL SUMMARY

Energy Totals:
  Consumption:      {total_cons:>8.0f} kWh
  Generation:       {total_gen:>8.0f} kWh
  Self-Consumption: {total_self_cons:>8.0f} kWh
  
Grid Flows:
  Import:           {total_import:>8.0f} kWh
  Export:           {total_export:>8.0f} kWh
  Net Balance:      {total_export - total_import:>8.0f} kWh
  
Performance:
  Avg Self-Sufficiency:    {avg_self_suff:>5.1f}%
  Self-Consumption Ratio:  {total_self_cons/total_gen*100:>5.1f}%
  Coverage Ratio:          {total_gen/total_cons*100:>5.1f}%
        """
        
        ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes,
                fontsize=10, verticalalignment='top',
                family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
        
        plt.tight_layout()
        return fig


def main():
    """Example usage"""
    from PV_consumption_generator import ConsumptionPatternGenerator, HouseholdProfile
    from PV_solar_generator import SolarGenerationCalculator, SolarSystemProfile, LOCATIONS
    from PV_battery_flow import BatteryFlowCalculator
    
    print("=" * 80)
    print("INTEGRATED ENERGY GRAPHS - TEST")
    print("=" * 80)
    print()
    
    # Create components
    consumption_gen = ConsumptionPatternGenerator()
    solar_gen = SolarGenerationCalculator()
    battery_calc = BatteryFlowCalculator(battery_capacity_kwh=10.0)
    
    household = HouseholdProfile(
        name='Test Family',
        pattern_type='working_family',
        annual_consumption_kwh=5000,
        seasonal_strength=0.2,
        peak_evening_hour=19
    )
    
    solar_system = SolarSystemProfile(
        name='Test System',
        peak_power_kw=6.0,
        location=LOCATIONS['riga_latvia'],
        tilt_angle=35.0,
        system_efficiency=0.85
    )
    
    print(f"Household: {household.pattern_type}")
    print(f"Annual consumption: {household.annual_consumption_kwh} kWh")
    print(f"Solar system: {solar_system.peak_power_kw} kW")
    print(f"Battery: {battery_calc.battery_capacity} kWh")
    print()
    
    # Create graph generator
    graph_gen = IntegratedEnergyGraphs(
        consumption_gen, solar_gen, battery_calc,
        household, solar_system
    )
    
    print("Generating graphs...")
    
    # Daily flow
    fig1 = graph_gen.plot_daily_energy_flow(month=6, day_of_week=0)
    fig1.savefig('integrated_daily_flow.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: integrated_daily_flow.png")
    
    # Weekly comparison
    fig2 = graph_gen.plot_weekly_comparison(month=6)
    fig2.savefig('integrated_weekly_comparison.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: integrated_weekly_comparison.png")
    
    # Seasonal comparison
    fig3 = graph_gen.plot_seasonal_comparison()
    fig3.savefig('integrated_seasonal_comparison.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: integrated_seasonal_comparison.png")
    
    # Annual summary
    fig4 = graph_gen.plot_annual_summary()
    fig4.savefig('integrated_annual_summary.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: integrated_annual_summary.png")
    
    print()
    print("All graphs generated successfully!")
    plt.close('all')


if __name__ == "__main__":
    main()

