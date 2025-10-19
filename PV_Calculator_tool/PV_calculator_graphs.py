"""
PV System Feasibility Calculator - Graphing Module
Generates visualization of break-even analysis and financial projections
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import math
from typing import Dict, List, Optional, Tuple
from PV_calculator import PVFeasibilityCalculator


class PVGraphGenerator:
    """Generate graphs for PV system financial analysis"""
    
    def __init__(self, calculator: PVFeasibilityCalculator):
        self.calculator = calculator
        
    def calculate_cashflow_over_time(self, with_battery: bool = False, years: int = 25) -> Dict:
        """Calculate year-by-year cash flow and cumulative savings"""
        if not self.calculator.pv_system:
            return None
        
        baseline = self.calculator.calculate_baseline_costs()
        
        # Initial investment
        initial_cost = self.calculator.pv_system.installation_cost
        if with_battery and self.calculator.battery:
            initial_cost += self.calculator.battery.installation_cost
        
        years_list = [0]
        cumulative_cashflow = [-initial_cost]
        annual_savings_list = [0]
        annual_operational_savings = [0]  # New: savings without one-time costs
        cumulative_savings = [0]
        battery_replacement_years = []
        battery_replacement_costs = []
        
        for year in range(1, years + 1):
            # Calculate costs for this year (with degradation)
            with_pv = self.calculator.calculate_annual_costs_with_pv(with_battery)
            
            # Account for degradation
            degradation_factor = (1 - self.calculator.pv_system.annual_degradation_rate) ** (year - 1)
            
            # Adjust savings based on degradation
            annual_savings = (baseline['annual_cost'] - with_pv['annual_cost']) * degradation_factor
            
            # Battery replacement (if applicable)
            replacement_cost = 0
            if with_battery and self.calculator.battery:
                if year % self.calculator.battery.lifetime_years == 0 and year < years:
                    replacement_cost = self.calculator.battery.installation_cost * 0.7  # Assume 30% price reduction
                    battery_replacement_years.append(year)
                    battery_replacement_costs.append(replacement_cost)
            
            net_annual_savings = annual_savings - replacement_cost
            
            years_list.append(year)
            annual_savings_list.append(net_annual_savings)
            annual_operational_savings.append(annual_savings)  # Store without replacement cost
            cumulative_savings.append(cumulative_savings[-1] + annual_savings)
            cumulative_cashflow.append(cumulative_cashflow[-1] + net_annual_savings)
        
        # Find break-even year
        breakeven_year = None
        for i, cf in enumerate(cumulative_cashflow):
            if cf >= 0:
                breakeven_year = years_list[i]
                # Interpolate for more precise break-even
                if i > 0 and cumulative_cashflow[i-1] < 0:
                    prev_cf = cumulative_cashflow[i-1]
                    curr_cf = cumulative_cashflow[i]
                    fraction = -prev_cf / (curr_cf - prev_cf)
                    breakeven_year = years_list[i-1] + fraction
                break
        
        return {
            'years': years_list,
            'cumulative_cashflow': cumulative_cashflow,
            'annual_savings': annual_savings_list,
            'annual_operational_savings': annual_operational_savings,
            'cumulative_savings': cumulative_savings,
            'breakeven_year': breakeven_year,
            'initial_investment': initial_cost,
            'battery_replacement_years': battery_replacement_years,
            'battery_replacement_costs': battery_replacement_costs
        }
    
    def plot_breakeven_analysis(self, save_path: Optional[str] = None, show: bool = True) -> plt.Figure:
        """Generate break-even analysis graph"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        fig.suptitle('PV System Break-Even Analysis', fontsize=16, fontweight='bold')
        
        # Calculate data for both scenarios
        pv_only = self.calculate_cashflow_over_time(with_battery=False)
        pv_battery = None
        if self.calculator.battery:
            pv_battery = self.calculate_cashflow_over_time(with_battery=True)
        
        # Plot 1: Cumulative Cash Flow
        ax1.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        ax1.plot(pv_only['years'], pv_only['cumulative_cashflow'], 
                linewidth=2.5, label='PV Only', marker='o', markersize=4, color='#2E86AB')
        
        if pv_battery:
            ax1.plot(pv_battery['years'], pv_battery['cumulative_cashflow'], 
                    linewidth=2.5, label='PV + Battery', marker='s', markersize=4, color='#A23B72')
        
        # Mark break-even points
        if pv_only['breakeven_year']:
            ax1.axvline(x=pv_only['breakeven_year'], color='#2E86AB', 
                       linestyle=':', alpha=0.7, linewidth=2)
            ax1.plot(pv_only['breakeven_year'], 0, 'o', markersize=12, 
                    color='#2E86AB', markeredgecolor='white', markeredgewidth=2)
            ax1.annotate(f'Break-even: {pv_only["breakeven_year"]:.1f} years',
                        xy=(pv_only['breakeven_year'], 0),
                        xytext=(pv_only['breakeven_year'] + 2, 2000),
                        fontsize=10, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='#2E86AB', alpha=0.7, edgecolor='none'),
                        color='white',
                        arrowprops=dict(arrowstyle='->', color='#2E86AB', lw=2))
        
        if pv_battery and pv_battery['breakeven_year']:
            ax1.axvline(x=pv_battery['breakeven_year'], color='#A23B72', 
                       linestyle=':', alpha=0.7, linewidth=2)
            ax1.plot(pv_battery['breakeven_year'], 0, 's', markersize=12, 
                    color='#A23B72', markeredgecolor='white', markeredgewidth=2)
            ax1.annotate(f'Break-even: {pv_battery["breakeven_year"]:.1f} years',
                        xy=(pv_battery['breakeven_year'], 0),
                        xytext=(pv_battery['breakeven_year'] + 2, -2000),
                        fontsize=10, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='#A23B72', alpha=0.7, edgecolor='none'),
                        color='white',
                        arrowprops=dict(arrowstyle='->', color='#A23B72', lw=2))
        
        ax1.set_xlabel('Years', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Cumulative Cash Flow (€)', fontsize=12, fontweight='bold')
        ax1.set_title('Cumulative Cash Flow Over Time', fontsize=13, pad=10)
        ax1.legend(fontsize=11, loc='best', framealpha=0.9)
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
        
        # Shade profitable region
        ax1.fill_between(pv_only['years'], 0, 
                        [max(cf, 0) for cf in pv_only['cumulative_cashflow']], 
                        alpha=0.2, color='green', label='Profit Region')
        
        # Plot 2: Annual Savings (showing operational savings, not one-time costs)
        ax2.plot(pv_only['years'], pv_only['annual_operational_savings'], 
                linewidth=2.5, label='PV Only', marker='o', markersize=4, color='#2E86AB')
        
        if pv_battery:
            ax2.plot(pv_battery['years'], pv_battery['annual_operational_savings'], 
                    linewidth=2.5, label='PV + Battery (operational)', marker='s', markersize=4, color='#A23B72')
            
            # Mark battery replacement years with red X markers
            if pv_battery['battery_replacement_years']:
                for repl_year, repl_cost in zip(pv_battery['battery_replacement_years'], 
                                                 pv_battery['battery_replacement_costs']):
                    # Get the operational savings for that year
                    year_idx = pv_battery['years'].index(repl_year)
                    operational_savings = pv_battery['annual_operational_savings'][year_idx]
                    
                    # Plot marker at the operational savings level
                    ax2.plot(repl_year, operational_savings, 'rx', markersize=12, 
                            markeredgewidth=3, label='Battery Replacement' if repl_year == pv_battery['battery_replacement_years'][0] else '')
                    
                    # Add annotation
                    ax2.annotate(f'Battery\nReplacement\n-€{repl_cost:,.0f}',
                               xy=(repl_year, operational_savings),
                               xytext=(repl_year, operational_savings - 200),
                               fontsize=8,
                               ha='center',
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='red', alpha=0.7, edgecolor='none'),
                               color='white',
                               arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
        
        ax2.set_xlabel('Years', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Annual Operational Savings (€)', fontsize=12, fontweight='bold')
        ax2.set_title('Annual Savings Over Time\n(smooth curve = ongoing savings, markers = one-time battery replacements)', 
                     fontsize=12, pad=10)
        ax2.legend(fontsize=10, loc='best', framealpha=0.9)
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Graph saved to: {save_path}")
        
        if show:
            plt.show()
        
        return fig
    
    def plot_cost_comparison(self, save_path: Optional[str] = None, show: bool = True) -> plt.Figure:
        """Generate cost comparison bar chart"""
        baseline = self.calculator.calculate_baseline_costs()
        
        scenarios = ['Current\n(No PV)']
        annual_costs = [baseline['annual_cost']]
        colors = ['#E63946']
        
        if self.calculator.pv_system:
            pv_only = self.calculator.calculate_annual_costs_with_pv(with_battery=False)
            scenarios.append('PV System\n(No Battery)')
            annual_costs.append(pv_only['annual_cost'])
            colors.append('#2E86AB')
            
            if self.calculator.battery:
                pv_battery = self.calculator.calculate_annual_costs_with_pv(with_battery=True)
                scenarios.append('PV System\n+ Battery')
                annual_costs.append(pv_battery['annual_cost'])
                colors.append('#A23B72')
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.bar(scenarios, annual_costs, color=colors, edgecolor='white', linewidth=2, alpha=0.8)
        
        # Add value labels on bars
        for bar, cost in zip(bars, annual_costs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'€{cost:,.0f}/year',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Add savings annotations
        if len(annual_costs) > 1:
            for i in range(1, len(annual_costs)):
                savings = baseline['annual_cost'] - annual_costs[i]
                percent_savings = (savings / baseline['annual_cost']) * 100
                ax.text(i, annual_costs[i] / 2,
                       f'Save €{savings:,.0f}\n({percent_savings:.1f}%)',
                       ha='center', va='center', fontsize=10, 
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8),
                       fontweight='bold', color='green')
        
        ax.set_ylabel('Annual Electricity Cost (€)', fontsize=12, fontweight='bold')
        ax.set_title('Annual Cost Comparison', fontsize=14, fontweight='bold', pad=20)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
        ax.grid(True, axis='y', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Graph saved to: {save_path}")
        
        if show:
            plt.show()
        
        return fig
    
    def plot_energy_flow(self, save_path: Optional[str] = None, show: bool = True) -> plt.Figure:
        """Generate energy flow visualization"""
        if not self.calculator.pv_system:
            return None
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Daily Energy Flow Analysis', fontsize=16, fontweight='bold')
        
        scenarios = [
            ('PV Only', False, axes[0]),
            ('PV + Battery', True, axes[1])
        ]
        
        for title, with_battery, ax in scenarios:
            if with_battery and not self.calculator.battery:
                ax.axis('off')
                ax.text(0.5, 0.5, 'No Battery Configured', 
                       ha='center', va='center', fontsize=14, transform=ax.transAxes)
                continue
            
            flow = self.calculator.simulate_daily_energy_flow(with_battery)
            
            # Calculate components
            daily_consumption = self.calculator.consumption.get_daily_consumption()
            pv_production = self.calculator.pv_system.estimate_daily_production()
            grid_import = flow['grid_import_kwh']
            self_consumption = flow['pv_self_consumption_kwh']
            excess = flow['excess_to_grid_kwh']
            
            # Create stacked bar chart
            categories = ['Consumption\nSources', 'PV\nProduction']
            
            # Consumption sources
            consumption_pv = self_consumption
            consumption_grid = grid_import
            
            # PV production use
            pv_self = self_consumption
            pv_excess = excess
            
            x = np.arange(len(categories))
            width = 0.6
            
            # Plot consumption
            ax.bar(0, consumption_pv, width, label='PV Self-Use', color='#F4A261', edgecolor='white', linewidth=2)
            ax.bar(0, consumption_grid, width, bottom=consumption_pv, label='Grid Import', 
                  color='#E63946', edgecolor='white', linewidth=2)
            
            # Plot production
            ax.bar(1, pv_self, width, color='#F4A261', edgecolor='white', linewidth=2)
            ax.bar(1, pv_excess, width, bottom=pv_self, label='Excess to Grid', 
                  color='#2A9D8F', edgecolor='white', linewidth=2)
            
            # Add value labels
            ax.text(0, consumption_pv/2, f'{consumption_pv:.1f} kWh', 
                   ha='center', va='center', fontweight='bold', fontsize=9)
            if consumption_grid > 0.5:
                ax.text(0, consumption_pv + consumption_grid/2, f'{consumption_grid:.1f} kWh', 
                       ha='center', va='center', fontweight='bold', fontsize=9)
            
            ax.text(1, pv_self/2, f'{pv_self:.1f} kWh', 
                   ha='center', va='center', fontweight='bold', fontsize=9)
            if pv_excess > 0.5:
                ax.text(1, pv_self + pv_excess/2, f'{pv_excess:.1f} kWh', 
                       ha='center', va='center', fontweight='bold', fontsize=9)
            
            # Add total labels
            ax.text(0, daily_consumption + 1, f'Total: {daily_consumption:.1f} kWh', 
                   ha='center', va='bottom', fontweight='bold', fontsize=10)
            ax.text(1, pv_production + 1, f'Total: {pv_production:.1f} kWh', 
                   ha='center', va='bottom', fontweight='bold', fontsize=10)
            
            ax.set_xticks(x)
            ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
            ax.set_ylabel('Energy (kWh/day)', fontsize=11, fontweight='bold')
            ax.set_title(f'{title}\nSelf-Sufficiency: {flow["self_sufficiency_ratio"]*100:.1f}%', 
                        fontsize=12, pad=10)
            ax.legend(fontsize=9, loc='upper left', framealpha=0.9)
            ax.grid(True, axis='y', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Graph saved to: {save_path}")
        
        if show:
            plt.show()
        
        return fig
    
    def plot_roi_comparison(self, save_path: Optional[str] = None, show: bool = True) -> plt.Figure:
        """Generate ROI comparison visualization"""
        if not self.calculator.pv_system:
            return None
        
        roi_pv = self.calculator.calculate_roi(with_battery=False)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Return on Investment Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Investment Breakdown
        labels = ['PV System']
        investments = [self.calculator.pv_system.installation_cost]
        colors_pie = ['#2E86AB']
        
        if self.calculator.battery:
            roi_battery = self.calculator.calculate_roi(with_battery=True)
            labels.append('Battery')
            investments.append(self.calculator.battery.installation_cost)
            colors_pie.append('#A23B72')
        else:
            roi_battery = None
        
        wedges, texts, autotexts = ax1.pie(investments, labels=labels, autopct='%1.1f%%',
                                            colors=colors_pie, startangle=90,
                                            textprops={'fontsize': 11, 'fontweight': 'bold'})
        
        # Make percentage text more visible
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
            autotext.set_fontweight('bold')
        
        ax1.set_title(f'Investment Breakdown\nTotal: €{sum(investments):,.0f}', 
                     fontsize=12, fontweight='bold', pad=10)
        
        # Plot 2: Payback Comparison
        scenarios_roi = []
        payback_periods = []
        colors_bar = []
        
        scenarios_roi.append('PV\nOnly')
        payback_periods.append(roi_pv['simple_payback_years'])
        colors_bar.append('#2E86AB')
        
        if roi_battery:
            scenarios_roi.append('PV +\nBattery')
            payback_periods.append(roi_battery['simple_payback_years'])
            colors_bar.append('#A23B72')
        
        bars = ax2.barh(scenarios_roi, payback_periods, color=colors_bar, 
                       edgecolor='white', linewidth=2, alpha=0.8)
        
        # Add value labels
        for bar, period in zip(bars, payback_periods):
            width = bar.get_width()
            ax2.text(width, bar.get_y() + bar.get_height()/2,
                    f'  {period:.1f} years',
                    ha='left', va='center', fontsize=11, fontweight='bold')
        
        # Add reference lines
        ax2.axvline(x=10, color='green', linestyle='--', alpha=0.5, linewidth=2, label='Excellent (<10y)')
        ax2.axvline(x=15, color='orange', linestyle='--', alpha=0.5, linewidth=2, label='Good (<15y)')
        
        ax2.set_xlabel('Payback Period (Years)', fontsize=12, fontweight='bold')
        ax2.set_title('Simple Payback Period', fontsize=12, fontweight='bold', pad=10)
        ax2.legend(fontsize=9, loc='lower right', framealpha=0.9)
        ax2.grid(True, axis='x', alpha=0.3, linestyle='--')
        ax2.set_xlim(0, max(payback_periods) * 1.2)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Graph saved to: {save_path}")
        
        if show:
            plt.show()
        
        return fig
    
    def plot_monthly_seasonal_analysis(self, save_path: Optional[str] = None, show: bool = True) -> plt.Figure:
        """Generate monthly seasonal analysis graph showing PV generation vs consumption patterns"""
        if not self.calculator.pv_system:
            return None
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        fig.suptitle('Monthly Seasonal Analysis - PV Generation vs Consumption', fontsize=16, fontweight='bold')
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        # Calculate monthly data
        pv_monthly = []
        household_monthly = []
        ev_monthly = []
        self_sufficiency_monthly = []
        
        for month_num, days in enumerate(days_in_month, 1):
            # PV production
            pv_daily = self.calculator.pv_system.estimate_daily_production(month=month_num)
            pv_month = pv_daily * days
            pv_monthly.append(pv_month)
            
            # Household consumption
            household_daily = self.calculator.consumption.get_daily_consumption(month=month_num)
            household_month = household_daily * days
            household_monthly.append(household_month)
            
            # EV consumption
            if self.calculator.ev_profile and self.calculator.ev_profile.enabled:
                ev_daily = self.calculator.ev_profile.daily_driving_kwh
                ev_month = ev_daily * days
                ev_monthly.append(ev_month)
            else:
                ev_monthly.append(0)
            
            # Self-sufficiency (PV / total consumption ratio, capped at 100%)
            # Total consumption includes both household and EV
            total_consumption_month = household_month + ev_monthly[-1]
            if total_consumption_month > 0:
                self_suff = min(100, (pv_month / total_consumption_month) * 100)
            else:
                self_suff = 0
            self_sufficiency_monthly.append(self_suff)
        
        x = np.arange(len(months))
        width = 0.35
        
        # Plot 1: Energy Production and Consumption
        bars1 = ax1.bar(x - width/2, pv_monthly, width, label='PV Production', 
                       color='#F4A261', edgecolor='white', linewidth=1.5, alpha=0.9)
        bars2 = ax1.bar(x + width/2, household_monthly, width, label='Household Consumption', 
                       color='#2E86AB', edgecolor='white', linewidth=1.5, alpha=0.9)
        
        # Add EV consumption as stacked bars if applicable
        has_ev = any(ev > 0 for ev in ev_monthly)
        if has_ev:
            bars3 = ax1.bar(x + width/2, ev_monthly, width, bottom=household_monthly,
                           label='EV Charging', color='#A23B72', edgecolor='white', linewidth=1.5, alpha=0.9)
        
        # Add annotations for winter and summer periods
        ax1.axvspan(-0.5, 2.5, alpha=0.1, color='blue', label='Winter (Low Sun)')
        ax1.axvspan(4.5, 7.5, alpha=0.1, color='yellow', label='Summer (Peak Sun)')
        
        ax1.set_xlabel('Month', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Energy (kWh/month)', fontsize=12, fontweight='bold')
        ax1.set_title('Monthly Energy Production vs Consumption', fontsize=13, pad=10)
        ax1.set_xticks(x)
        ax1.set_xticklabels(months, fontsize=10)
        ax1.legend(fontsize=10, loc='upper left', framealpha=0.9)
        ax1.grid(True, axis='y', alpha=0.3, linestyle='--')
        ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, p: f'{y:,.0f}'))
        
        # Add text annotations for key months
        # Winter minimum
        winter_min_idx = pv_monthly.index(min(pv_monthly[:3]))
        ax1.annotate(f'Winter Low\n{pv_monthly[winter_min_idx]:.0f} kWh',
                    xy=(winter_min_idx, pv_monthly[winter_min_idx]),
                    xytext=(winter_min_idx, pv_monthly[winter_min_idx] + max(pv_monthly) * 0.15),
                    fontsize=9, ha='center',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='blue', alpha=0.7, edgecolor='none'),
                    color='white',
                    arrowprops=dict(arrowstyle='->', color='blue', lw=1.5))
        
        # Summer maximum
        summer_max_idx = pv_monthly.index(max(pv_monthly))
        ax1.annotate(f'Summer Peak\n{pv_monthly[summer_max_idx]:.0f} kWh',
                    xy=(summer_max_idx, pv_monthly[summer_max_idx]),
                    xytext=(summer_max_idx, pv_monthly[summer_max_idx] + max(pv_monthly) * 0.15),
                    fontsize=9, ha='center',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='orange', alpha=0.7, edgecolor='none'),
                    color='white',
                    arrowprops=dict(arrowstyle='->', color='orange', lw=1.5))
        
        # Plot 2: Self-Sufficiency Ratio
        line = ax2.plot(x, self_sufficiency_monthly, linewidth=3, marker='o', markersize=8,
                       color='#2A9D8F', label='Self-Sufficiency %', markeredgecolor='white', 
                       markeredgewidth=2)
        
        # Fill area under the curve
        ax2.fill_between(x, 0, self_sufficiency_monthly, alpha=0.3, color='#2A9D8F')
        
        # Add 100% reference line
        ax2.axhline(y=100, color='green', linestyle='--', linewidth=2, alpha=0.5, label='100% Self-Sufficient')
        
        # Add seasonal shading
        ax2.axvspan(-0.5, 2.5, alpha=0.1, color='blue')
        ax2.axvspan(4.5, 7.5, alpha=0.1, color='yellow')
        
        # Add value labels on points
        for i, (month, value) in enumerate(zip(months, self_sufficiency_monthly)):
            ax2.text(i, value + 3, f'{value:.0f}%', ha='center', va='bottom', 
                    fontsize=8, fontweight='bold')
        
        ax2.set_xlabel('Month', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Self-Sufficiency (%)', fontsize=12, fontweight='bold')
        has_ev_text = " (Including EV)" if has_ev else " (Household Only)"
        ax2.set_title(f'Monthly Self-Sufficiency Ratio{has_ev_text}', fontsize=13, pad=10)
        ax2.set_xticks(x)
        ax2.set_xticklabels(months, fontsize=10)
        ax2.set_ylim(0, max(120, max(self_sufficiency_monthly) + 10))
        ax2.legend(fontsize=10, loc='lower left', framealpha=0.9)
        ax2.grid(True, alpha=0.3, linestyle='--')
        
        # Add summary statistics
        avg_self_suff = np.mean(self_sufficiency_monthly)
        winter_avg = np.mean(self_sufficiency_monthly[0:3] + self_sufficiency_monthly[11:12])
        summer_avg = np.mean(self_sufficiency_monthly[5:8])
        
        stats_text = f'Annual Average: {avg_self_suff:.1f}%\n'
        stats_text += f'Winter Avg: {winter_avg:.1f}%\n'
        stats_text += f'Summer Avg: {summer_avg:.1f}%'
        
        ax2.text(0.98, 0.97, stats_text, transform=ax2.transAxes,
                fontsize=10, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round,pad=0.8', facecolor='white', alpha=0.9, edgecolor='gray'),
                fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Graph saved to: {save_path}")
        
        if show:
            plt.show()
        
        return fig
    
    def calculate_monthly_costs_with_revenue(self) -> Dict:
        """Calculate month-by-month costs and revenue to show offsetting effect"""
        if not self.calculator.pv_system:
            return None
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        monthly_data = {
            'months': months,
            'pv_production': [],
            'total_consumption': [],
            'grid_import': [],
            'excess_to_grid': [],
            'import_cost': [],
            'export_revenue': [],
            'net_cost': [],
            'cumulative_balance': []
        }
        
        cumulative = 0
        tariff = self.calculator.tariff
        selling_price = self.calculator.nord_pool.average_price if self.calculator.nord_pool else 0.05
        
        for month_num, days in enumerate(days_in_month, 1):
            # Calculate monthly production and consumption
            pv_daily = self.calculator.pv_system.estimate_daily_production(month=month_num)
            pv_monthly = pv_daily * days
            
            household_daily = self.calculator.consumption.get_daily_consumption(month=month_num)
            household_monthly = household_daily * days
            
            ev_monthly = 0
            if self.calculator.ev_profile and self.calculator.ev_profile.enabled:
                ev_monthly = self.calculator.ev_profile.daily_driving_kwh * days
            
            total_consumption = household_monthly + ev_monthly
            
            # Calculate energy balance
            energy_balance = pv_monthly - total_consumption
            
            if energy_balance >= 0:
                # Surplus month - selling to grid
                grid_import = 0
                excess_to_grid = energy_balance
                import_cost = 0
                export_revenue = excess_to_grid * selling_price
                net_cost = -export_revenue  # Negative cost = earning money
            else:
                # Deficit month - buying from grid
                grid_import = -energy_balance
                excess_to_grid = 0
                import_cost = grid_import * tariff.get_total_cost_per_kwh()
                export_revenue = 0
                net_cost = import_cost
            
            # Add fixed monthly costs (power connection + service fee)
            monthly_fixed = tariff.get_monthly_fixed_cost()
            net_cost += monthly_fixed
            
            cumulative += (export_revenue - import_cost - monthly_fixed)
            
            monthly_data['pv_production'].append(pv_monthly)
            monthly_data['total_consumption'].append(total_consumption)
            monthly_data['grid_import'].append(grid_import)
            monthly_data['excess_to_grid'].append(excess_to_grid)
            monthly_data['import_cost'].append(import_cost)
            monthly_data['export_revenue'].append(export_revenue)
            monthly_data['net_cost'].append(net_cost)
            monthly_data['cumulative_balance'].append(cumulative)
        
        return monthly_data
    
    def plot_monthly_revenue_offsetting(self, save_path: Optional[str] = None, show: bool = True) -> plt.Figure:
        """Generate graph showing how summer revenue offsets winter costs"""
        if not self.calculator.pv_system:
            return None
        
        monthly_data = self.calculate_monthly_costs_with_revenue()
        if not monthly_data:
            return None
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        fig.suptitle('Monthly Revenue Offsetting Analysis', fontsize=16, fontweight='bold')
        
        months = monthly_data['months']
        x = np.arange(len(months))
        
        # Plot 1: Monthly Costs and Revenue
        width = 0.35
        
        # Import costs (red bars, going up)
        import_costs = monthly_data['import_cost']
        ax1.bar(x - width/2, import_costs, width, label='Grid Import Cost',
               color='#E63946', edgecolor='white', linewidth=1.5, alpha=0.9)
        
        # Export revenue (green bars, going down as negative)
        export_revenue = [-r for r in monthly_data['export_revenue']]  # Make negative for visual effect
        ax1.bar(x + width/2, export_revenue, width, label='Export Revenue (Credit)',
               color='#2A9D8F', edgecolor='white', linewidth=1.5, alpha=0.9)
        
        # Add fixed cost line
        fixed_cost = self.calculator.tariff.get_monthly_fixed_cost()
        ax1.axhline(y=fixed_cost, color='gray', linestyle='--', linewidth=2, alpha=0.5, 
                   label=f'Monthly Fixed Cost (€{fixed_cost:.2f})')
        
        # Add seasonal shading
        ax1.axvspan(-0.5, 2.5, alpha=0.1, color='blue', label='Winter (High Import)')
        ax1.axvspan(4.5, 7.5, alpha=0.1, color='yellow', label='Summer (Export Revenue)')
        
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
        ax1.set_xlabel('Month', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Monthly Cost / Revenue (€)', fontsize=12, fontweight='bold')
        ax1.set_title('Monthly Grid Costs vs Export Revenue', fontsize=13, pad=10)
        ax1.set_xticks(x)
        ax1.set_xticklabels(months, fontsize=10)
        ax1.legend(fontsize=9, loc='upper left', framealpha=0.9)
        ax1.grid(True, axis='y', alpha=0.3, linestyle='--')
        ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, p: f'€{y:.0f}'))
        
        # Add annotations for key months
        max_import_idx = import_costs.index(max(import_costs))
        if import_costs[max_import_idx] > 0:
            ax1.annotate(f'Peak Import\n€{import_costs[max_import_idx]:.0f}',
                        xy=(max_import_idx - width/2, import_costs[max_import_idx]),
                        xytext=(max_import_idx, import_costs[max_import_idx] + fixed_cost * 0.5),
                        fontsize=9, ha='center',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='red', alpha=0.7, edgecolor='none'),
                        color='white',
                        arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
        
        max_export_idx = monthly_data['export_revenue'].index(max(monthly_data['export_revenue']))
        if monthly_data['export_revenue'][max_export_idx] > 0:
            ax1.annotate(f'Peak Revenue\n€{monthly_data["export_revenue"][max_export_idx]:.0f}',
                        xy=(max_export_idx + width/2, export_revenue[max_export_idx]),
                        xytext=(max_export_idx, export_revenue[max_export_idx] - fixed_cost * 0.5),
                        fontsize=9, ha='center',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='green', alpha=0.7, edgecolor='none'),
                        color='white',
                        arrowprops=dict(arrowstyle='->', color='green', lw=1.5))
        
        # Plot 2: Net Cost and Cumulative Balance
        net_costs = monthly_data['net_cost']
        cumulative = monthly_data['cumulative_balance']
        
        # Bar chart for net monthly cost
        colors = ['#2A9D8F' if cost < 0 else '#E63946' for cost in net_costs]
        bars = ax2.bar(x, net_costs, color=colors, edgecolor='white', linewidth=1.5, alpha=0.7,
                      label='Net Monthly Cost')
        
        # Line chart for cumulative balance
        ax2_twin = ax2.twinx()
        line = ax2_twin.plot(x, cumulative, linewidth=3, marker='o', markersize=8,
                            color='#2E86AB', label='Cumulative Balance', markeredgecolor='white',
                            markeredgewidth=2)
        ax2_twin.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        
        # Add seasonal shading
        ax2.axvspan(-0.5, 2.5, alpha=0.1, color='blue')
        ax2.axvspan(4.5, 7.5, alpha=0.1, color='yellow')
        
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
        ax2.set_xlabel('Month', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Net Monthly Cost (€)', fontsize=12, fontweight='bold')
        ax2_twin.set_ylabel('Cumulative Balance (€)', fontsize=12, fontweight='bold', color='#2E86AB')
        ax2.set_title('Net Cost with Revenue Offsetting (Summer credits offset winter costs)', fontsize=13, pad=10)
        ax2.set_xticks(x)
        ax2.set_xticklabels(months, fontsize=10)
        ax2.grid(True, axis='y', alpha=0.3, linestyle='--')
        ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, p: f'€{y:.0f}'))
        ax2_twin.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, p: f'€{y:.0f}'))
        ax2_twin.tick_params(axis='y', labelcolor='#2E86AB')
        
        # Combined legend
        lines1, labels1 = ax2.get_legend_handles_labels()
        lines2, labels2 = ax2_twin.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, fontsize=10, loc='upper left', framealpha=0.9)
        
        # Add summary box
        total_import_cost = sum(monthly_data['import_cost'])
        total_export_revenue = sum(monthly_data['export_revenue'])
        annual_fixed = self.calculator.tariff.get_monthly_fixed_cost() * 12
        net_annual = total_import_cost - total_export_revenue + annual_fixed
        
        summary_text = f'Annual Summary:\n'
        summary_text += f'Import Cost: €{total_import_cost:.2f}\n'
        summary_text += f'Export Revenue: €{total_export_revenue:.2f}\n'
        summary_text += f'Fixed Costs: €{annual_fixed:.2f}\n'
        summary_text += f'Net Annual: €{net_annual:.2f}'
        
        ax2.text(0.98, 0.97, summary_text, transform=ax2.transAxes,
                fontsize=10, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round,pad=0.8', facecolor='white', alpha=0.95, edgecolor='gray'),
                fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Graph saved to: {save_path}")
        
        if show:
            plt.show()
        
        return fig
    
    def plot_weekly_energy_balance(self, week_number: int = 1, with_battery: bool = True, 
                                   save_path: Optional[str] = None, show: bool = True) -> plt.Figure:
        """
        Plot hourly energy balance for a specific week of the year
        Shows PV generation, consumption, and net balance
        
        Args:
            week_number: Week of year (1-52)
            with_battery: Whether to include battery in simulation
            save_path: Path to save the figure
            show: Whether to display the figure
        """
        if not self.calculator.pv_system:
            raise ValueError("PV system must be configured to generate weekly analysis")
        
        # Calculate which month and starting day
        # Approximate: week 1 = Jan 1-7, week 2 = Jan 8-14, etc.
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        # Find the month and day for the start of this week
        start_day_of_year = (week_number - 1) * 7 + 1
        
        current_day = 0
        start_month = 1
        start_day = 1
        
        for month_idx, days in enumerate(days_in_month):
            if current_day + days >= start_day_of_year:
                start_month = month_idx + 1
                start_day = start_day_of_year - current_day
                break
            current_day += days
        
        # Determine starting day of week (assume Jan 1 = Monday)
        start_day_of_week = (start_day_of_year - 1) % 7
        
        # Day names
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        # Simulate each day of the week
        hours = []
        pv_generation = []
        consumption = []
        battery_charge_list = []
        battery_discharge_list = []
        battery_state_list = []
        net_balance = []
        
        current_month = start_month
        current_day_in_month = start_day
        day_of_week = start_day_of_week
        
        for day in range(7):
            # Check if we need to move to next month
            if current_day_in_month > days_in_month[current_month - 1]:
                current_month += 1
                current_day_in_month = 1
                if current_month > 12:
                    current_month = 1
            
            # Get PV pattern for this month
            pv_pattern = self.calculator.pv_system.get_hourly_pv_pattern(current_month)
            daily_pv = self.calculator.pv_system.estimate_daily_production(month=current_month)
            
            # Simulate this day
            battery_state = 0
            battery_capacity = (self.calculator.battery.get_usable_capacity() 
                              if (with_battery and self.calculator.battery) else 0)
            
            # Track EV charging for realistic behavior (charge at full power until done)
            ev_energy_needed_today = 0
            ev_energy_charged_today = 0
            if self.calculator.ev_profile.enabled:
                # Calculate today's EV energy need with seasonal adjustment
                seasonal_factor = 1.0 - 0.2 * math.cos((current_month - 1) * math.pi / 6)
                ev_energy_needed_today = self.calculator.ev_profile.daily_driving_kwh * seasonal_factor
            
            for hour in range(24):
                hour_of_week = day * 24 + hour
                hours.append(hour_of_week)
                
                # PV generation
                pv_hour = daily_pv * pv_pattern[hour]
                pv_generation.append(pv_hour)
                
                # Household consumption (day-of-week aware)
                consumption_hour = self.calculator.consumption.get_hourly_consumption(
                    hour, current_month, day_of_week
                )
                
                # Add EV consumption if enabled (realistic: charge at full charger power until done)
                if self.calculator.ev_profile.enabled:
                    # Check if this is a charging hour and EV still needs charge
                    if hour in self.calculator.ev_profile.charging_hours and ev_energy_charged_today < ev_energy_needed_today:
                        # Charge at full charger power until daily need is met
                        remaining_energy = ev_energy_needed_today - ev_energy_charged_today
                        ev_charge_this_hour = min(self.calculator.ev_profile.charging_power_kw, remaining_energy)
                        consumption_hour += ev_charge_this_hour
                        ev_energy_charged_today += ev_charge_this_hour
                
                consumption.append(consumption_hour)
                
                # Battery simulation
                battery_charge = 0
                battery_discharge = 0
                balance = pv_hour - consumption_hour
                
                if with_battery and self.calculator.battery:
                    if balance > 0:  # Excess PV
                        # Try to charge battery
                        charge_amount = min(balance, battery_capacity - battery_state)
                        charge_actual = charge_amount * self.calculator.battery.efficiency
                        battery_state += charge_actual
                        battery_charge = charge_actual
                        balance -= charge_amount
                    else:  # Deficit
                        # Try to discharge battery
                        deficit = -balance
                        discharge_amount = min(deficit, battery_state)
                        discharge_actual = discharge_amount * self.calculator.battery.efficiency
                        battery_state -= discharge_amount
                        battery_discharge = discharge_actual
                        balance += discharge_actual
                
                battery_charge_list.append(battery_charge)
                battery_discharge_list.append(battery_discharge)
                battery_state_list.append(battery_state)
                net_balance.append(balance)
            
            day_of_week = (day_of_week + 1) % 7
            current_day_in_month += 1
        
        # Create figure
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 1, height_ratios=[2, 1.5, 1], hspace=0.3)
        
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        ax3 = fig.add_subplot(gs[2])  # Independent x-axis for day summary
        
        # Determine month name for title
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        title_month = month_names[start_month - 1]
        
        fig.suptitle(f'Weekly Energy Balance - Week {week_number} ({title_month} {start_day})', 
                    fontsize=16, fontweight='bold')
        
        # Plot 1: PV Generation vs Consumption
        ax1.fill_between(hours, 0, pv_generation, alpha=0.3, color='orange', label='PV Generation')
        ax1.plot(hours, pv_generation, color='orange', linewidth=2, label='PV Generation (kW)')
        ax1.fill_between(hours, 0, consumption, alpha=0.3, color='red', label='Consumption')
        ax1.plot(hours, consumption, color='red', linewidth=2, label='Total Consumption (kW)')
        
        ax1.set_ylabel('Power (kW)', fontsize=11, fontweight='bold')
        ax1.set_title('Hourly PV Generation vs Consumption', fontsize=12, fontweight='bold')
        ax1.legend(loc='upper right', fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(0, 168)  # Exactly 7 days × 24 hours
        
        # Set x-axis ticks at day boundaries
        ax1.set_xticks([0, 24, 48, 72, 96, 120, 144, 168])
        ax1.set_xticklabels(['Mon\n0h', '24h', '48h', '72h', '96h', '120h', '144h', 'Sun\n168h'], fontsize=9)
        
        # Add vertical lines for days
        for day in range(1, 8):
            ax1.axvline(x=day*24, color='gray', linestyle='--', alpha=0.5)
        
        # Add day labels
        for day in range(7):
            day_name = day_names[(start_day_of_week + day) % 7]
            is_weekend = ((start_day_of_week + day) % 7) in [5, 6]
            color = 'darkblue' if is_weekend else 'black'
            weight = 'bold' if is_weekend else 'normal'
            ax1.text(day*24 + 12, ax1.get_ylim()[1] * 0.95, day_name,
                    ha='center', va='top', fontsize=11, fontweight=weight, color=color,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
        
        # Plot 2: Net Balance with Battery
        positive_balance = [max(0, b) for b in net_balance]
        negative_balance = [min(0, b) for b in net_balance]
        
        ax2.fill_between(hours, 0, positive_balance, alpha=0.5, color='green', label='Excess (to grid)')
        ax2.fill_between(hours, 0, negative_balance, alpha=0.5, color='red', label='Deficit (from grid)')
        ax2.plot(hours, net_balance, color='black', linewidth=1.5, label='Net Balance', alpha=0.7)
        ax2.axhline(y=0, color='gray', linestyle='-', linewidth=1)
        
        if with_battery and self.calculator.battery:
            # Add battery state on secondary axis
            ax2_twin = ax2.twinx()
            ax2_twin.plot(hours, battery_state_list, color='blue', linewidth=2, 
                         linestyle='--', label='Battery State', alpha=0.7)
            ax2_twin.set_ylabel('Battery State (kWh)', fontsize=11, fontweight='bold', color='blue')
            ax2_twin.tick_params(axis='y', labelcolor='blue')
            ax2_twin.set_ylim([0, battery_capacity * 1.1])
            
            # Combined legend
            lines1, labels1 = ax2.get_legend_handles_labels()
            lines2, labels2 = ax2_twin.get_legend_handles_labels()
            ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=10)
        else:
            ax2.legend(loc='upper right', fontsize=10)
        
        ax2.set_ylabel('Net Power (kW)', fontsize=11, fontweight='bold')
        ax2.set_title('Net Energy Balance (Positive=Export, Negative=Import)', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(0, 168)  # Exactly 7 days × 24 hours
        ax2.set_xlabel('Hour of Week', fontsize=11, fontweight='bold')
        
        # Set x-axis ticks at day boundaries (matching ax1)
        ax2.set_xticks([0, 24, 48, 72, 96, 120, 144, 168])
        ax2.set_xticklabels(['0h', '24h', '48h', '72h', '96h', '120h', '144h', '168h'], fontsize=9)
        
        # Add vertical lines for days
        for day in range(1, 8):
            ax2.axvline(x=day*24, color='gray', linestyle='--', alpha=0.5)
        
        # Plot 3: Daily Energy Summary
        daily_pv = []
        daily_consumption = []
        daily_export = []
        daily_import = []
        day_labels = []
        
        for day in range(7):
            start_h = day * 24
            end_h = (day + 1) * 24
            
            day_pv = sum(pv_generation[start_h:end_h])
            day_cons = sum(consumption[start_h:end_h])
            day_export = sum([max(0, b) for b in net_balance[start_h:end_h]])
            day_import = sum([abs(min(0, b)) for b in net_balance[start_h:end_h]])
            
            daily_pv.append(day_pv)
            daily_consumption.append(day_cons)
            daily_export.append(day_export)
            daily_import.append(day_import)
            
            day_name = day_names[(start_day_of_week + day) % 7]
            day_labels.append(day_name)
        
        x_pos = np.arange(7)
        width = 0.25
        
        bars1 = ax3.bar(x_pos - width*1.5, daily_pv, width, label='PV Generated', 
                       color='orange', alpha=0.8)
        bars2 = ax3.bar(x_pos - width/2, daily_consumption, width, label='Consumed', 
                       color='red', alpha=0.8)
        bars3 = ax3.bar(x_pos + width/2, daily_export, width, label='Exported', 
                       color='green', alpha=0.8)
        bars4 = ax3.bar(x_pos + width*1.5, daily_import, width, label='Imported', 
                       color='darkred', alpha=0.8)
        
        ax3.set_ylabel('Energy (kWh)', fontsize=11, fontweight='bold')
        ax3.set_title('Daily Energy Summary', fontsize=12, fontweight='bold')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(day_labels, fontsize=10)
        ax3.legend(loc='upper right', fontsize=9, ncol=4)
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Fix x-axis limits to prevent bars from being cut off
        ax3.set_xlim(-0.6, 6.6)
        
        # Highlight weekends
        for day in range(7):
            if ((start_day_of_week + day) % 7) in [5, 6]:
                ax3.axvspan(day-0.5, day+0.5, alpha=0.1, color='blue')
        
        # Add summary statistics
        week_pv_total = sum(daily_pv)
        week_cons_total = sum(daily_consumption)
        week_export_total = sum(daily_export)
        week_import_total = sum(daily_import)
        self_sufficiency = ((week_cons_total - week_import_total) / week_cons_total * 100 
                           if week_cons_total > 0 else 0)
        
        summary_text = f'Week Summary:\n'
        summary_text += f'PV: {week_pv_total:.1f} kWh\n'
        summary_text += f'Consumed: {week_cons_total:.1f} kWh\n'
        summary_text += f'Exported: {week_export_total:.1f} kWh\n'
        summary_text += f'Imported: {week_import_total:.1f} kWh\n'
        summary_text += f'Self-Sufficiency: {self_sufficiency:.1f}%'
        
        ax3.text(0.98, 0.97, summary_text, transform=ax3.transAxes,
                fontsize=9, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.95, 
                         edgecolor='orange', linewidth=2),
                fontweight='bold', family='monospace')
        
        ax3.set_xlabel('Day of Week', fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Graph saved to: {save_path}")
        
        if show:
            plt.show()
        
        return fig
    
    def generate_all_graphs(self, output_dir: str = ".", show: bool = True):
        """Generate all graphs and save them"""
        import os
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        graphs = [
            ('breakeven', self.plot_breakeven_analysis),
            ('cost_comparison', self.plot_cost_comparison),
            ('energy_flow', self.plot_energy_flow),
            ('roi_comparison', self.plot_roi_comparison),
            ('monthly_seasonal', self.plot_monthly_seasonal_analysis),
            ('monthly_revenue_offsetting', self.plot_monthly_revenue_offsetting)
        ]
        
        saved_files = []
        for name, plot_func in graphs:
            filepath = os.path.join(output_dir, f'PV_Analysis_{name}_{timestamp}.png')
            plot_func(save_path=filepath, show=show)
            saved_files.append(filepath)
        
        print(f"\n{'='*60}")
        print("All graphs generated successfully!")
        print(f"{'='*60}")
        for filepath in saved_files:
            print(f"  ✓ {os.path.basename(filepath)}")
        print(f"{'='*60}\n")
        
        return saved_files


def main():
    """Example usage"""
    from PV_calculator import (
        ElectricityTariff, ConsumptionProfile, PVSystemSpecs,
        BatterySpecs, NordPoolPrice
    )
    
    # Setup calculator (same as PV_calculator.py example)
    tariff = ElectricityTariff(
        power_amperes=25,
        power_cost_per_ampere=0.50,
        electricity_cost=0.08,
        transfer_cost=0.04,
        service_cost=0.01,
        monthly_service_fee=5.0,
        vat_rate=0.21
    )
    
    consumption = ConsumptionProfile(monthly_consumption_kwh=500)
    
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
    
    calculator = PVFeasibilityCalculator(
        tariff=tariff,
        consumption=consumption,
        pv_system=pv_system,
        battery=battery,
        nord_pool=nord_pool
    )
    
    # Generate graphs
    graph_gen = PVGraphGenerator(calculator)
    
    print("Generating PV System Analysis Graphs...")
    print("=" * 60)
    
    # Generate all graphs
    graph_gen.generate_all_graphs(show=True)


if __name__ == "__main__":
    main()

