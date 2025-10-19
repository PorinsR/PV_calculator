"""
Solar Generation Visualization Graphs
Compares consumption patterns with solar generation to show excess/deficit
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

from PV_solar_generator import SolarGenerationCalculator, SolarSystemProfile, LOCATIONS
from PV_consumption_generator import ConsumptionPatternGenerator, HouseholdProfile


class SolarComparisonGraphs:
    """Generate comparison graphs between consumption and solar generation"""
    
    def __init__(self,
                 solar_calc: SolarGenerationCalculator,
                 consumption_gen: ConsumptionPatternGenerator):
        self.solar_calc = solar_calc
        self.consumption_gen = consumption_gen
    
    def plot_daily_comparison(self,
                             system: SolarSystemProfile,
                             household: HouseholdProfile,
                             month: int,
                             day_of_week: int = 0,
                             save_path: Optional[str] = None,
                             show: bool = True) -> plt.Figure:
        """
        Plot hourly comparison of generation vs consumption for a single day
        Shows excess and deficit periods
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        fig.suptitle(f'Solar Generation vs Consumption - {["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][day_of_week]} in Month {month}',
                    fontsize=14, fontweight='bold')
        
        hours = np.arange(24)
        
        # Get consumption pattern
        consumption = [self.consumption_gen.get_hourly_consumption(
            household, month, day_of_week, h) for h in hours]
        
        # Get generation pattern
        generation = [self.solar_calc.get_hourly_generation(
            system, month, h) for h in hours]
        
        # Calculate excess/deficit
        excess = [max(0, g - c) for g, c in zip(generation, consumption)]
        deficit = [max(0, c - g) for g, c in zip(generation, consumption)]
        self_consumption = [min(g, c) for g, c in zip(generation, consumption)]
        
        # Plot 1: Generation vs Consumption
        ax1.plot(hours, generation, 'o-', linewidth=2, label='Solar Generation',
                color='orange', markersize=6)
        ax1.plot(hours, consumption, 's-', linewidth=2, label='Household Consumption',
                color='blue', markersize=6)
        
        # Fill areas
        ax1.fill_between(hours, generation, alpha=0.3, color='orange', label='Generation area')
        ax1.fill_between(hours, consumption, alpha=0.3, color='blue', label='Consumption area')
        
        # Highlight excess/deficit
        for h in hours:
            if excess[h] > 0:
                ax1.axvspan(h-0.5, h+0.5, alpha=0.15, color='green')
            elif deficit[h] > 0:
                ax1.axvspan(h-0.5, h+0.5, alpha=0.15, color='red')
        
        ax1.set_xlabel('Hour of Day', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Power (kWh)', fontsize=11, fontweight='bold')
        ax1.set_title('Hourly Generation and Consumption', fontsize=12)
        ax1.legend(loc='upper left', fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(-0.5, 23.5)
        ax1.set_xticks(range(0, 24, 2))
        
        # Add annotations
        total_gen = sum(generation)
        total_cons = sum(consumption)
        total_excess = sum(excess)
        total_deficit = sum(deficit)
        self_suff = sum(self_consumption) / total_cons * 100 if total_cons > 0 else 0
        
        summary_text = f'Daily Summary:\n'
        summary_text += f'Generation: {total_gen:.1f} kWh\n'
        summary_text += f'Consumption: {total_cons:.1f} kWh\n'
        summary_text += f'Self-sufficiency: {self_suff:.1f}%\n'
        summary_text += f'Excess: {total_excess:.1f} kWh\n'
        summary_text += f'Deficit: {total_deficit:.1f} kWh'
        
        ax1.text(0.98, 0.97, summary_text, transform=ax1.transAxes,
                fontsize=10, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round,pad=0.7', facecolor='lightyellow', alpha=0.95,
                         edgecolor='orange', linewidth=2),
                fontweight='bold', family='monospace')
        
        # Plot 2: Excess and Deficit bars
        x_pos = np.arange(24)
        
        bars_excess = ax2.bar(x_pos, excess, width=0.8, label='Excess (to grid/battery)',
                             color='green', alpha=0.7)
        bars_deficit = ax2.bar(x_pos, [-d for d in deficit], width=0.8, label='Deficit (from grid/battery)',
                              color='red', alpha=0.7)
        
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax2.set_xlabel('Hour of Day', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Excess / Deficit (kWh)', fontsize=11, fontweight='bold')
        ax2.set_title('Hourly Energy Balance', fontsize=12)
        ax2.legend(loc='upper right', fontsize=10)
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.set_xlim(-0.5, 23.5)
        ax2.set_xticks(range(0, 24, 2))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Graph saved to: {save_path}")
        
        if show:
            plt.show()
        
        return fig
    
    def plot_monthly_generation_profile(self,
                                       system: SolarSystemProfile,
                                       save_path: Optional[str] = None,
                                       show: bool = True) -> plt.Figure:
        """
        Plot monthly solar generation profile across the year
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        fig.suptitle(f'Solar Generation Profile - {system.name}', fontsize=14, fontweight='bold')
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Get annual generation
        annual_data = self.solar_calc.calculate_annual_generation(system)
        monthly_totals = annual_data['monthly_totals']
        
        # Plot 1: Monthly generation bars
        x_pos = np.arange(12)
        bars = ax1.bar(x_pos, monthly_totals, color='orange', alpha=0.7, edgecolor='darkorange')
        
        # Highlight peak and low months
        peak_idx = annual_data['peak_month'] - 1
        low_idx = annual_data['low_month'] - 1
        bars[peak_idx].set_color('gold')
        bars[low_idx].set_color('lightblue')
        
        ax1.set_xlabel('Month', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Generation (kWh)', fontsize=11, fontweight='bold')
        ax1.set_title(f'Monthly Solar Generation - {system.location.name}', fontsize=12)
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(months)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar, val in zip(bars, monthly_totals):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.0f}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Summary text
        summary = f'Annual: {annual_data["annual_total"]:.0f} kWh\n'
        summary += f'Daily avg: {annual_data["average_daily"]:.1f} kWh\n'
        summary += f'Peak: {months[peak_idx]} ({monthly_totals[peak_idx]:.0f})\n'
        summary += f'Low: {months[low_idx]} ({monthly_totals[low_idx]:.0f})'
        
        ax1.text(0.02, 0.98, summary, transform=ax1.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.9),
                fontweight='bold', family='monospace')
        
        # Plot 2: Typical day generation curves for each season
        hours = np.arange(24)
        
        # Winter, Spring, Summer, Fall
        seasons = [(12, 'Winter (Dec)', 'blue'),
                  (3, 'Spring (Mar)', 'green'),
                  (6, 'Summer (Jun)', 'red'),
                  (9, 'Fall (Sep)', 'orange')]
        
        for month, label, color in seasons:
            pattern = self.solar_calc.get_hourly_pv_pattern(system.location, month, system.tilt_angle)
            daily_gen = self.solar_calc.calculate_daily_generation(system, month)
            hourly_gen = [daily_gen * p for p in pattern]
            
            ax2.plot(hours, hourly_gen, marker='o', linewidth=2, label=label, color=color)
        
        ax2.set_xlabel('Hour of Day', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Generation (kWh)', fontsize=11, fontweight='bold')
        ax2.set_title('Typical Daily Generation Profiles by Season', fontsize=12)
        ax2.legend(loc='upper left', fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(0, 23)
        ax2.set_xticks(range(0, 24, 3))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Graph saved to: {save_path}")
        
        if show:
            plt.show()
        
        return fig
    
    def plot_annual_comparison(self,
                              system: SolarSystemProfile,
                              household: HouseholdProfile,
                              save_path: Optional[str] = None,
                              show: bool = True) -> plt.Figure:
        """
        Compare monthly generation vs consumption across the year
        """
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.suptitle('Annual Solar Generation vs Household Consumption',
                    fontsize=14, fontweight='bold')
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        # Get generation
        annual_gen = self.solar_calc.calculate_annual_generation(system)
        generation = annual_gen['monthly_totals']
        
        # Get consumption
        consumption = []
        for month, days in enumerate(days_in_month, 1):
            weekday_avg = self.consumption_gen.get_daily_consumption(household, month, True)
            weekend_avg = self.consumption_gen.get_daily_consumption(household, month, False)
            weekdays = 22 if days >= 30 else int(days * 22/30)
            weekends = days - weekdays
            monthly_cons = (weekday_avg * weekdays) + (weekend_avg * weekends)
            consumption.append(monthly_cons)
        
        # Calculate net (generation - consumption)
        net = [g - c for g, c in zip(generation, consumption)]
        
        # Plot
        x_pos = np.arange(12)
        width = 0.35
        
        bars1 = ax.bar(x_pos - width/2, generation, width, label='Solar Generation',
                      color='orange', alpha=0.8)
        bars2 = ax.bar(x_pos + width/2, consumption, width, label='Consumption',
                      color='blue', alpha=0.8)
        
        ax.set_xlabel('Month', fontsize=11, fontweight='bold')
        ax.set_ylabel('Energy (kWh)', fontsize=11, fontweight='bold')
        ax.set_title(f'{system.name} vs {household.name}', fontsize=12)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(months)
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add net line
        ax2 = ax.twinx()
        ax2.plot(x_pos, net, 'go-', linewidth=2, markersize=8, label='Net (Gen - Cons)')
        ax2.axhline(y=0, color='black', linestyle='--', linewidth=1)
        ax2.set_ylabel('Net Energy (kWh)', fontsize=11, fontweight='bold', color='green')
        ax2.tick_params(axis='y', labelcolor='green')
        ax2.legend(loc='upper right', fontsize=10)
        
        # Highlight surplus/deficit months
        for i, n in enumerate(net):
            if n > 0:
                ax.axvspan(i-0.4, i+0.4, alpha=0.1, color='green')
            else:
                ax.axvspan(i-0.4, i+0.4, alpha=0.1, color='red')
        
        # Summary
        total_gen = sum(generation)
        total_cons = sum(consumption)
        total_surplus = sum([n for n in net if n > 0])
        total_deficit = sum([-n for n in net if n < 0])
        self_suff = (total_gen / total_cons * 100) if total_cons > 0 else 0
        
        summary = f'Annual Summary:\n'
        summary += f'Generation: {total_gen:.0f} kWh\n'
        summary += f'Consumption: {total_cons:.0f} kWh\n'
        summary += f'Coverage: {self_suff:.1f}%\n'
        summary += f'Surplus months: {sum([1 for n in net if n > 0])}\n'
        summary += f'Deficit months: {sum([1 for n in net if n < 0])}'
        
        ax.text(0.02, 0.98, summary, transform=ax.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.7', facecolor='lightyellow', alpha=0.95,
                         edgecolor='orange', linewidth=2),
                fontweight='bold', family='monospace')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Graph saved to: {save_path}")
        
        if show:
            plt.show()
        
        return fig


def main():
    """Example usage"""
    print("=" * 80)
    print("SOLAR vs CONSUMPTION COMPARISON GRAPHS")
    print("=" * 80)
    print()
    
    # Create generators
    solar_calc = SolarGenerationCalculator()
    consumption_gen = ConsumptionPatternGenerator()
    graph_gen = SolarComparisonGraphs(solar_calc, consumption_gen)
    
    # Create solar system
    location = LOCATIONS['riga_latvia']
    system = SolarSystemProfile(
        name="5kW Residential System",
        peak_power_kw=5.0,
        location=location
    )
    
    # Create household
    household = consumption_gen.create_household_profile(
        name="Typical Family",
        annual_consumption_kwh=6000,
        pattern_type='working_family',
        seasonal_strength=0.2
    )
    
    print("Generating graphs...")
    print()
    
    # Generate graphs (show one at a time)
    print("1. Daily comparison (June weekday)...")
    graph_gen.plot_daily_comparison(system, household, 6, 0, show=False)
    
    print("2. Monthly generation profile...")
    graph_gen.plot_monthly_generation_profile(system, show=False)
    
    print("3. Annual comparison...")
    graph_gen.plot_annual_comparison(system, household, show=True)
    
    print("\nAll graphs generated successfully!")


if __name__ == "__main__":
    main()

