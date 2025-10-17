"""
PV System Feasibility Calculator - Interactive GUI
User-friendly interface for the PV calculator
"""

import sys
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QCheckBox,
    QTextEdit, QScrollArea, QGroupBox, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from PV_calculator import (
    ElectricityTariff, ConsumptionProfile, PVSystemSpecs,
    BatterySpecs, NordPoolPrice, PVFeasibilityCalculator, EVProfile
)

# Try to import graphing module
try:
    from PV_calculator_graphs import PVGraphGenerator
    GRAPHS_AVAILABLE = True
except ImportError:
    GRAPHS_AVAILABLE = False
    print("Warning: matplotlib not available. Install it with: pip install matplotlib numpy")


class PVCalculatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PV System Feasibility Calculator")
        self.resize(900, 800)
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.tab_input = QWidget()
        self.tab_results = QWidget()
        self.tab_comparison = QWidget()
        self.tab_graphs = QWidget()
        
        self.tab_widget.addTab(self.tab_input, "Input Parameters")
        self.tab_widget.addTab(self.tab_results, "Results")
        self.tab_widget.addTab(self.tab_comparison, "Scenario Comparison")
        self.tab_widget.addTab(self.tab_graphs, "Graphs")
        
        # Setup tabs
        self.setup_input_tab()
        self.setup_results_tab()
        self.setup_comparison_tab()
        self.setup_graphs_tab()
        
        # Store calculator for graphs
        self.current_calculator = None
        
        # Load saved configuration if exists
        self.load_configuration()
    
    def setup_input_tab(self):
        """Setup the input parameters tab"""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create container widget for scroll area
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(container)
        
        # Set layout for tab
        tab_layout = QVBoxLayout(self.tab_input)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)
        
        # Electricity Tariff Section
        tariff_group = QGroupBox("Electricity Tariff")
        tariff_layout = QFormLayout()
        tariff_group.setLayout(tariff_layout)
        
        self.power_amperes = QLineEdit("25")
        tariff_layout.addRow("Connected Power (Amperes):", self.power_amperes)
        
        self.power_cost = QLineEdit("0.50")
        tariff_layout.addRow("Power Cost (EUR/A):", self.power_cost)
        
        self.electricity_cost = QLineEdit("0.08")
        tariff_layout.addRow("Electricity Cost (EUR/kWh):", self.electricity_cost)
        
        self.transfer_cost = QLineEdit("0.04")
        tariff_layout.addRow("Transfer Cost (EUR/kWh):", self.transfer_cost)
        
        self.service_cost = QLineEdit("0.01")
        tariff_layout.addRow("Service Cost (EUR/kWh):", self.service_cost)
        
        self.monthly_service_fee = QLineEdit("5.0")
        tariff_layout.addRow("Monthly Service Fee (EUR):", self.monthly_service_fee)
        
        self.vat_rate = QLineEdit("21")
        tariff_layout.addRow("VAT Rate (%):", self.vat_rate)
        
        main_layout.addWidget(tariff_group)
        
        # Consumption Section
        consumption_group = QGroupBox("Energy Consumption")
        consumption_layout = QHBoxLayout()
        consumption_group.setLayout(consumption_layout)
        
        consumption_layout.addWidget(QLabel("Monthly Household Consumption (kWh):"))
        self.monthly_consumption = QLineEdit("500")
        consumption_layout.addWidget(self.monthly_consumption)
        hint_label = QLabel("(household only, without EV)")
        hint_label.setStyleSheet("color: gray; font-style: italic;")
        consumption_layout.addWidget(hint_label)
        consumption_layout.addStretch()
        
        main_layout.addWidget(consumption_group)
        
        # PV System Section
        pv_group = QGroupBox("PV System")
        pv_layout = QVBoxLayout()
        pv_group.setLayout(pv_layout)
        
        self.pv_enabled = QCheckBox("Enable PV System Analysis")
        self.pv_enabled.setChecked(True)
        pv_layout.addWidget(self.pv_enabled)
        
        pv_form = QFormLayout()
        
        self.pv_size = QLineEdit("5.0")
        pv_form.addRow("System Size (kWp):", self.pv_size)
        
        self.pv_cost = QLineEdit("7000")
        pv_form.addRow("Installation Cost (EUR):", self.pv_cost)
        
        irradiance_h = QHBoxLayout()
        self.solar_irradiance = QLineEdit("3.5")
        irradiance_h.addWidget(self.solar_irradiance)
        irradiance_hint = QLabel("(Central Europe: 3-3.5, Southern Europe: 4-5)")
        irradiance_hint.setStyleSheet("color: gray; font-style: italic;")
        irradiance_h.addWidget(irradiance_hint)
        irradiance_h.addStretch()
        pv_form.addRow("Avg. Daily Solar Irradiance (kWh/m²):", irradiance_h)
        
        pv_layout.addLayout(pv_form)
        main_layout.addWidget(pv_group)
        
        # Battery Section
        battery_group = QGroupBox("Battery Storage (Optional)")
        battery_layout = QVBoxLayout()
        battery_group.setLayout(battery_layout)
        
        self.battery_enabled = QCheckBox("Include Battery Storage")
        self.battery_enabled.setChecked(True)
        battery_layout.addWidget(self.battery_enabled)
        
        battery_form = QFormLayout()
        
        self.battery_capacity = QLineEdit("7.0")
        battery_form.addRow("Battery Capacity (kWh):", self.battery_capacity)
        
        self.battery_cost = QLineEdit("4000")
        battery_form.addRow("Battery Cost (EUR):", self.battery_cost)
        
        battery_layout.addLayout(battery_form)
        
        battery_info = QLabel("💡 Best case: Battery capacity should cover daily household + EV needs (~50-80% of daily total)")
        battery_info.setWordWrap(True)
        battery_info.setStyleSheet("color: darkgreen; font-style: italic; font-size: 9pt;")
        battery_layout.addWidget(battery_info)
        
        battery_btn = QPushButton("Calculate Recommended Battery Size")
        battery_btn.clicked.connect(self.show_battery_recommendation)
        battery_layout.addWidget(battery_btn)
        
        main_layout.addWidget(battery_group)
        
        # Nord Pool Section
        nordpool_group = QGroupBox("Nord Pool Pricing")
        nordpool_layout = QHBoxLayout()
        nordpool_group.setLayout(nordpool_layout)
        
        nordpool_layout.addWidget(QLabel("Average Selling Price (EUR/kWh):"))
        self.nordpool_price = QLineEdit("0.06")
        nordpool_layout.addWidget(self.nordpool_price)
        nordpool_hint = QLabel("(for excess energy sold to grid)")
        nordpool_hint.setStyleSheet("color: gray; font-style: italic;")
        nordpool_layout.addWidget(nordpool_hint)
        nordpool_layout.addStretch()
        
        main_layout.addWidget(nordpool_group)
        
        # EV Charging Section (NEW!)
        ev_group = QGroupBox("Electric Vehicle Charging (Optional)")
        ev_layout = QVBoxLayout()
        ev_group.setLayout(ev_layout)
        
        self.ev_enabled = QCheckBox("Include EV Charging")
        self.ev_enabled.setChecked(False)
        ev_layout.addWidget(self.ev_enabled)
        
        ev_form = QFormLayout()
        
        km_h = QHBoxLayout()
        self.ev_daily_km = QLineEdit("60")
        km_h.addWidget(self.ev_daily_km)
        km_hint = QLabel("(typical: 30-100 km/day)")
        km_hint.setStyleSheet("color: gray; font-style: italic;")
        km_h.addWidget(km_hint)
        km_h.addStretch()
        ev_form.addRow("Daily Driving (km):", km_h)
        
        eff_h = QHBoxLayout()
        self.ev_efficiency = QLineEdit("25")
        eff_h.addWidget(self.ev_efficiency)
        eff_hint = QLabel("(typical: 15-30 kWh/100km)")
        eff_hint.setStyleSheet("color: gray; font-style: italic;")
        eff_h.addWidget(eff_hint)
        eff_h.addStretch()
        ev_form.addRow("Vehicle Efficiency (kWh/100km):", eff_h)
        
        pow_h = QHBoxLayout()
        self.ev_charger_power = QLineEdit("7.0")
        pow_h.addWidget(self.ev_charger_power)
        pow_hint = QLabel("(typical: 3.7, 7, 11, or 22 kW)")
        pow_hint.setStyleSheet("color: gray; font-style: italic;")
        pow_h.addWidget(pow_hint)
        pow_h.addStretch()
        ev_form.addRow("Home Charger Power (kW):", pow_h)
        
        ev_layout.addLayout(ev_form)
        
        ev_info = QLabel("Note: EV charges at night. Battery can provide power to both household and EV.")
        ev_info.setStyleSheet("color: blue; font-style: italic; font-size: 9pt;")
        ev_layout.addWidget(ev_info)
        
        main_layout.addWidget(ev_group)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        # Primary action buttons
        primary_layout = QHBoxLayout()
        
        calc_btn = QPushButton("Calculate")
        calc_btn.setMinimumHeight(35)
        calc_btn.setStyleSheet("font-weight: bold;")
        calc_btn.clicked.connect(self.calculate)
        primary_layout.addWidget(calc_btn)
        
        compare_btn = QPushButton("Compare Scenarios")
        compare_btn.setMinimumHeight(35)
        compare_btn.setStyleSheet("font-weight: bold;")
        compare_btn.clicked.connect(self.run_scenario_comparison)
        primary_layout.addWidget(compare_btn)
        
        primary_layout.addStretch()
        button_layout.addLayout(primary_layout)
        
        # Configuration buttons
        config_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Configuration")
        save_btn.clicked.connect(self.save_configuration)
        config_layout.addWidget(save_btn)
        
        load_btn = QPushButton("Load Configuration")
        load_btn.clicked.connect(self.load_configuration)
        config_layout.addWidget(load_btn)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        config_layout.addWidget(reset_btn)
        
        config_layout.addStretch()
        button_layout.addLayout(config_layout)
        
        main_layout.addLayout(button_layout)
    
    def setup_results_tab(self):
        """Setup the results display tab"""
        layout = QVBoxLayout(self.tab_results)
        
        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Courier", 9))
        layout.addWidget(self.results_text)
        
        # Export button
        export_layout = QHBoxLayout()
        export_btn = QPushButton("Export to Text File")
        export_btn.clicked.connect(self.export_results)
        export_layout.addWidget(export_btn)
        export_layout.addStretch()
        
        layout.addLayout(export_layout)
    
    def setup_comparison_tab(self):
        """Setup the scenario comparison tab"""
        layout = QVBoxLayout(self.tab_comparison)
        
        # Info text
        info_label = QLabel("Compare different scenarios and view seasonal analysis.")
        info_label.setFont(QFont("Arial", 10))
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Compare button
        compare_btn = QPushButton("Run Scenario Comparison")
        compare_btn.setMinimumHeight(40)
        compare_btn.setStyleSheet("font-size: 12pt; font-weight: bold;")
        compare_btn.clicked.connect(self.run_scenario_comparison)
        layout.addWidget(compare_btn)
        
        # Comparison results text area
        self.comparison_text = QTextEdit()
        self.comparison_text.setReadOnly(True)
        self.comparison_text.setFont(QFont("Courier", 9))
        layout.addWidget(self.comparison_text)
        
        # Export button
        export_layout = QHBoxLayout()
        export_btn = QPushButton("Export Comparison to Text File")
        export_btn.clicked.connect(self.export_comparison)
        export_layout.addWidget(export_btn)
        export_layout.addStretch()
        
        layout.addLayout(export_layout)
    
    def setup_graphs_tab(self):
        """Setup the graphs tab"""
        layout = QVBoxLayout(self.tab_graphs)
        
        if not GRAPHS_AVAILABLE:
            warning_label = QLabel("Graphing functionality not available.\n\n"
                                          "Please install required packages:\n"
                                  "pip install matplotlib numpy")
            warning_label.setFont(QFont("Arial", 12))
            warning_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(warning_label)
            return
        
        # Info text
        info_text = ("Click 'Generate Graphs' to create visual analysis of your PV system.\n"
                    "Graphs will be displayed in separate windows and saved as PNG files.")
        info_label = QLabel(info_text)
        info_label.setFont(QFont("Arial", 10))
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Buttons frame
        button_group = QGroupBox("Available Graphs")
        button_layout = QVBoxLayout()
        button_group.setLayout(button_layout)
        
        graphs = [
            ("Break-Even Analysis", "Shows when your investment pays for itself", self.show_breakeven_graph),
            ("Cost Comparison", "Compare annual costs across scenarios", self.show_cost_comparison_graph),
            ("Energy Flow", "Visualize daily energy production and consumption", self.show_energy_flow_graph),
            ("ROI Comparison", "Compare return on investment metrics", self.show_roi_graph),
            ("Monthly Seasonal Analysis", "View year-round PV generation vs consumption patterns", self.show_seasonal_graph),
            ("Monthly Revenue Offsetting", "See how summer revenue offsets winter costs", self.show_revenue_offsetting_graph),
            ("Generate All Graphs", "Create and save all graphs at once", self.generate_all_graphs)
        ]
        
        for name, description, command in graphs:
            row_layout = QHBoxLayout()
            
            btn = QPushButton(name)
            btn.setMinimumWidth(200)
            btn.clicked.connect(command)
            row_layout.addWidget(btn)
            
            desc_label = QLabel(description)
            desc_label.setFont(QFont("Arial", 9))
            row_layout.addWidget(desc_label)
            row_layout.addStretch()
            
            button_layout.addLayout(row_layout)
        
        layout.addWidget(button_group)
        
        # Status
        self.graph_status = QLabel("")
        self.graph_status.setFont(QFont("Arial", 9))
        self.graph_status.setStyleSheet("font-style: italic;")
        layout.addWidget(self.graph_status)
        
        layout.addStretch()
    
    def get_inputs(self):
        """Get all input values and create calculator objects"""
        try:
            # Tariff
            tariff = ElectricityTariff(
                power_amperes=float(self.power_amperes.text()),
                power_cost_per_ampere=float(self.power_cost.text()),
                electricity_cost=float(self.electricity_cost.text()),
                transfer_cost=float(self.transfer_cost.text()),
                service_cost=float(self.service_cost.text()),
                monthly_service_fee=float(self.monthly_service_fee.text()),
                vat_rate=float(self.vat_rate.text()) / 100
            )
            
            # Consumption
            consumption = ConsumptionProfile(
                monthly_consumption_kwh=float(self.monthly_consumption.text())
            )
            
            # PV System
            pv_system = None
            if self.pv_enabled.isChecked():
                pv_system = PVSystemSpecs(
                    peak_power_kw=float(self.pv_size.text()),
                    installation_cost=float(self.pv_cost.text()),
                    avg_daily_irradiance=float(self.solar_irradiance.text())
                )
            
            # Battery
            battery = None
            if self.battery_enabled.isChecked() and self.pv_enabled.isChecked():
                battery = BatterySpecs(
                    capacity_kwh=float(self.battery_capacity.text()),
                    installation_cost=float(self.battery_cost.text())
                )
            
            # Nord Pool
            nord_pool = NordPoolPrice(
                average_price=float(self.nordpool_price.text())
            )
            
            # EV Profile
            ev_profile = EVProfile(enabled=False)
            if self.ev_enabled.isChecked():
                daily_km = float(self.ev_daily_km.text())
                efficiency = float(self.ev_efficiency.text())
                daily_kwh = daily_km * efficiency / 100.0
                
                ev_profile = EVProfile(
                    enabled=True,
                    daily_driving_kwh=daily_kwh,
                    charging_power_kw=float(self.ev_charger_power.text())
                )
            
            return tariff, consumption, pv_system, battery, nord_pool, ev_profile
        except ValueError as e:
            QMessageBox.critical(self, "Input Error", 
                               f"Invalid input value: {str(e)}\nPlease check all fields contain valid numbers.")
            return None
    
    def calculate(self):
        """Perform calculation and display results"""
        inputs = self.get_inputs()
        if not inputs:
            return
        
        tariff, consumption, pv_system, battery, nord_pool, ev_profile = inputs
        
        # Create calculator
        calculator = PVFeasibilityCalculator(
            tariff=tariff,
            consumption=consumption,
            pv_system=pv_system,
            battery=battery,
            nord_pool=nord_pool,
            ev_profile=ev_profile
        )
        
        # Store calculator for graphs
        self.current_calculator = calculator
        
        # Generate report
        report = calculator.generate_report()
        
        # Display results
        self.results_text.clear()
        self.results_text.setPlainText(report)
        
        # Switch to results tab
        self.tab_widget.setCurrentWidget(self.tab_results)
        
        QMessageBox.information(self, "Success", "Calculation completed! Check the Results and Graphs tabs.")
    
    def save_configuration(self):
        """Save current configuration to file"""
        config = {
            'tariff': {
                'power_amperes': self.power_amperes.text(),
                'power_cost': self.power_cost.text(),
                'electricity_cost': self.electricity_cost.text(),
                'transfer_cost': self.transfer_cost.text(),
                'service_cost': self.service_cost.text(),
                'monthly_service_fee': self.monthly_service_fee.text(),
                'vat_rate': self.vat_rate.text()
            },
            'consumption': {
                'monthly_consumption': self.monthly_consumption.text()
            },
            'pv': {
                'enabled': self.pv_enabled.isChecked(),
                'size': self.pv_size.text(),
                'cost': self.pv_cost.text(),
                'irradiance': self.solar_irradiance.text()
            },
            'battery': {
                'enabled': self.battery_enabled.isChecked(),
                'capacity': self.battery_capacity.text(),
                'cost': self.battery_cost.text()
            },
            'nordpool': {
                'price': self.nordpool_price.text()
            },
            'ev': {
                'enabled': self.ev_enabled.isChecked(),
                'daily_km': self.ev_daily_km.text(),
                'efficiency': self.ev_efficiency.text(),
                'charger_power': self.ev_charger_power.text()
            }
        }
        
        with open('pv_calculator_config.json', 'w') as f:
            json.dump(config, f, indent=4)
        
        QMessageBox.information(self, "Success", "Configuration saved to pv_calculator_config.json")
    
    def load_configuration(self):
        """Load configuration from file"""
        if not os.path.exists('pv_calculator_config.json'):
            return
        
        try:
            with open('pv_calculator_config.json', 'r') as f:
                config = json.load(f)
            
            # Load tariff
            self.power_amperes.setText(str(config['tariff']['power_amperes']))
            self.power_cost.setText(str(config['tariff']['power_cost']))
            self.electricity_cost.setText(str(config['tariff']['electricity_cost']))
            self.transfer_cost.setText(str(config['tariff']['transfer_cost']))
            self.service_cost.setText(str(config['tariff']['service_cost']))
            self.monthly_service_fee.setText(str(config['tariff']['monthly_service_fee']))
            self.vat_rate.setText(str(config['tariff']['vat_rate']))
            
            # Load consumption
            self.monthly_consumption.setText(str(config['consumption']['monthly_consumption']))
            
            # Load PV
            self.pv_enabled.setChecked(config['pv']['enabled'])
            self.pv_size.setText(str(config['pv']['size']))
            self.pv_cost.setText(str(config['pv']['cost']))
            self.solar_irradiance.setText(str(config['pv']['irradiance']))
            
            # Load battery
            self.battery_enabled.setChecked(config['battery']['enabled'])
            self.battery_capacity.setText(str(config['battery']['capacity']))
            self.battery_cost.setText(str(config['battery']['cost']))
            
            # Load Nord Pool
            self.nordpool_price.setText(str(config['nordpool']['price']))
            
            # Load EV (if exists in config)
            if 'ev' in config:
                self.ev_enabled.setChecked(config['ev']['enabled'])
                self.ev_daily_km.setText(str(config['ev']['daily_km']))
                self.ev_efficiency.setText(str(config['ev']['efficiency']))
                self.ev_charger_power.setText(str(config['ev']['charger_power']))
            
            QMessageBox.information(self, "Success", "Configuration loaded from pv_calculator_config.json")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading configuration: {str(e)}")
    
    def reset_to_defaults(self):
        """Reset all fields to default values"""
        self.power_amperes.setText("25")
        self.power_cost.setText("0.50")
        self.electricity_cost.setText("0.08")
        self.transfer_cost.setText("0.04")
        self.service_cost.setText("0.01")
        self.monthly_service_fee.setText("5.0")
        self.vat_rate.setText("21")
        self.monthly_consumption.setText("500")
        self.pv_enabled.setChecked(True)
        self.pv_size.setText("5.0")
        self.pv_cost.setText("7000")
        self.solar_irradiance.setText("3.5")
        self.battery_enabled.setChecked(True)
        self.battery_capacity.setText("7.0")
        self.battery_cost.setText("4000")
        self.nordpool_price.setText("0.06")
        self.ev_enabled.setChecked(False)
        self.ev_daily_km.setText("60")
        self.ev_efficiency.setText("25")
        self.ev_charger_power.setText("7.0")
        
        QMessageBox.information(self, "Success", "All fields reset to default values")
    
    def export_results(self):
        """Export results to a text file"""
        results = self.results_text.toPlainText()
        if not results.strip():
            QMessageBox.warning(self, "Warning", "No results to export. Please calculate first.")
            return
        
        filename = f"PV_Analysis_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(results)
        
        QMessageBox.information(self, "Success", f"Results exported to {filename}")
    
    def export_comparison(self):
        """Export comparison results to a text file"""
        results = self.comparison_text.toPlainText()
        if not results.strip():
            QMessageBox.warning(self, "Warning", "No comparison results to export. Please run comparison first.")
            return
        
        filename = f"PV_Scenario_Comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(results)
        
        QMessageBox.information(self, "Success", f"Comparison results exported to {filename}")
    
    def run_scenario_comparison(self):
        """Run scenario comparison: with/without EV and seasonal analysis"""
        inputs = self.get_inputs()
        if not inputs:
            return
        
        tariff, consumption, pv_system, battery, nord_pool, ev_profile = inputs
        
        if not pv_system:
            QMessageBox.warning(self, "Warning", "PV system must be enabled for scenario comparison.")
            return
        
        # Build comparison report
        report = []
        report.append("=" * 80)
        report.append("PV SYSTEM SCENARIO COMPARISON")
        report.append("=" * 80)
        report.append("")
        
        # Scenario A: Without EV (or current settings if EV disabled)
        report.append("=" * 80)
        report.append("SCENARIO A: HOUSEHOLD WITHOUT EV")
        report.append("=" * 80)
        
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
        with_pv_no_ev = calc_no_ev.calculate_annual_costs_with_pv(with_battery=battery is not None)
        roi_no_ev = calc_no_ev.calculate_roi(with_battery=battery is not None)
        
        report.append("")
        report.append("Without PV:")
        report.append(f"  Annual Cost: €{baseline_no_ev['annual_cost']:.2f}")
        report.append(f"  Annual Consumption: {baseline_no_ev['annual_consumption']:.0f} kWh")
        report.append("")
        
        battery_text = "PV + Battery" if battery else "PV Only"
        report.append(f"With {battery_text}:")
        report.append(f"  Annual Cost: €{with_pv_no_ev['annual_cost']:.2f}")
        report.append(f"  Annual Savings: €{roi_no_ev['annual_savings']:.2f}")
        report.append(f"  Payback Period: {roi_no_ev['simple_payback_years']:.1f} years")
        report.append(f"  Self-Sufficiency: {with_pv_no_ev['self_sufficiency_ratio']*100:.1f}%")
        
        # Calculate PV production from PV system specs
        annual_pv_production = pv_system.estimate_annual_production()
        report.append(f"  Annual PV Production: {annual_pv_production:.0f} kWh")
        
        # Show grid import data
        report.append(f"  Grid Import: {with_pv_no_ev['annual_grid_import']:.0f} kWh")
        
        # Show excess energy sold to grid
        if 'annual_excess_to_grid' in with_pv_no_ev and with_pv_no_ev['annual_excess_to_grid'] > 0:
            report.append(f"  Excess to Grid: {with_pv_no_ev['annual_excess_to_grid']:.0f} kWh")
            if 'annual_revenue' in with_pv_no_ev:
                report.append(f"  Revenue from Grid Sales: €{with_pv_no_ev['annual_revenue']:.2f}")
        
        # Scenario B: With EV (if EV is enabled in current settings)
        if ev_profile.enabled:
            report.append("")
            report.append("=" * 80)
            ev_daily_km = float(self.ev_daily_km.text())
            report.append(f"SCENARIO B: HOUSEHOLD WITH EV ({ev_daily_km:.0f} km/day driving)")
            report.append("=" * 80)
            
            calc_with_ev = PVFeasibilityCalculator(
                tariff=tariff,
                consumption=consumption,
                pv_system=pv_system,
                battery=battery,
                nord_pool=nord_pool,
                ev_profile=ev_profile
            )
            
            baseline_with_ev = calc_with_ev.calculate_baseline_costs()
            with_pv_with_ev = calc_with_ev.calculate_annual_costs_with_pv(with_battery=battery is not None)
            roi_with_ev = calc_with_ev.calculate_roi(with_battery=battery is not None)
            
            annual_ev_cost = ev_profile.daily_driving_kwh * 365 * tariff.get_total_cost_per_kwh()
            
            report.append("")
            report.append("Without PV:")
            report.append(f"  Household Annual Cost: €{baseline_with_ev['annual_cost']:.2f}")
            report.append(f"  EV Charging Cost: €{annual_ev_cost:.2f}")
            report.append(f"  Total: €{baseline_with_ev['annual_cost'] + annual_ev_cost:.2f}")
            report.append("")
            
            report.append(f"With {battery_text}:")
            report.append(f"  Annual Cost: €{with_pv_with_ev['annual_cost']:.2f}")
            report.append(f"  Annual Savings: €{roi_with_ev['annual_savings']:.2f}")
            report.append(f"  Payback Period: {roi_with_ev['simple_payback_years']:.1f} years")
            report.append(f"  Household Self-Sufficiency: {with_pv_with_ev['self_sufficiency_ratio']*100:.1f}%")
            
            # Use .get() for optional keys
            total_self_suff = with_pv_with_ev.get('total_self_sufficiency_ratio', with_pv_with_ev['self_sufficiency_ratio'])
            report.append(f"  Total Self-Sufficiency (incl. EV): {total_self_suff*100:.1f}%")
            
            # Show PV production (same as scenario A)
            report.append(f"  Annual PV Production: {annual_pv_production:.0f} kWh")
            
            # Show grid import breakdown
            report.append("")
            report.append("  Grid Import Breakdown:")
            report.append(f"    - Total: {with_pv_with_ev['annual_grid_import']:.0f} kWh")
            report.append(f"    - Household: {with_pv_with_ev['annual_grid_import_household']:.0f} kWh")
            report.append(f"    - EV Charging: {with_pv_with_ev['annual_grid_import_ev']:.0f} kWh")
            
            # Show excess energy sold to grid
            if 'annual_excess_to_grid' in with_pv_with_ev and with_pv_with_ev['annual_excess_to_grid'] > 0:
                report.append(f"  Excess to Grid: {with_pv_with_ev['annual_excess_to_grid']:.0f} kWh")
                if 'annual_revenue' in with_pv_with_ev:
                    report.append(f"  Revenue from Grid Sales: €{with_pv_with_ev['annual_revenue']:.2f}")
            
            # Comparison
            report.append("")
            report.append("=" * 80)
            report.append("COMPARISON: IMPACT OF ADDING EV")
            report.append("=" * 80)
            
            ev_impact_cost = annual_ev_cost
            ev_impact_consumption = ev_profile.daily_driving_kwh * 365
            payback_difference = roi_with_ev['simple_payback_years'] - roi_no_ev['simple_payback_years']
            
            report.append("")
            report.append("EV Impact:")
            report.append(f"  Additional Annual Consumption: {ev_impact_consumption:.0f} kWh (+{ev_impact_consumption/baseline_no_ev['annual_consumption']*100:.0f}%)")
            report.append(f"  Additional Annual Cost (without PV): €{ev_impact_cost:.2f}")
            report.append(f"  PV System Payback Difference: {payback_difference:+.1f} years")
            
            report.append("")
            report.append("Key Insights:")
            report.append(f"  • EV adds ~€{ev_impact_cost:.0f}/year to electricity costs")
            report.append(f"  • PV can't directly charge EV (charges at night)")
            report.append(f"  • Battery is reserved for household peak loads")
            report.append(f"  • Consider larger PV system if planning to buy EV")
        
        # Seasonal breakdown
        report.append("")
        report.append("=" * 80)
        report.append("SEASONAL PRODUCTION & CONSUMPTION ANALYSIS")
        report.append("=" * 80)
        report.append("")
        
        # Header
        if ev_profile.enabled:
            report.append("{:<12} {:>10} {:>12} {:>12} {:>10}".format(
                "Month", "PV (kWh)", "House (kWh)", "EV (kWh)", "Self-Suff"))
        else:
            report.append("{:<12} {:>10} {:>12} {:>10}".format(
                "Month", "PV (kWh)", "House (kWh)", "Self-Suff"))
        report.append("-" * 65)
        
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        for month_num, (month_name, days) in enumerate(zip(months, days_in_month), 1):
            pv_daily = pv_system.estimate_daily_production(month=month_num)
            pv_monthly = pv_daily * days
            
            house_daily = consumption.get_daily_consumption(month=month_num)
            house_monthly = house_daily * days
            
            self_suff = min(100, (pv_monthly / house_monthly * 100)) if house_monthly > 0 else 0
            
            if ev_profile.enabled:
                ev_daily = ev_profile.daily_driving_kwh
                ev_monthly = ev_daily * days
                report.append("{:<12} {:>10.0f} {:>12.0f} {:>12.0f} {:>9.0f}%".format(
                    month_name, pv_monthly, house_monthly, ev_monthly, self_suff))
            else:
                report.append("{:<12} {:>10.0f} {:>12.0f} {:>9.0f}%".format(
                    month_name, pv_monthly, house_monthly, self_suff))
        
        report.append("")
        report.append("=" * 80)
        report.append("SEASONAL INSIGHTS:")
        report.append("  • PV production varies dramatically by season")
        report.append("  • Winter months (Dec-Feb): Very low production")
        report.append("  • Summer months (Jun-Aug): Peak production")
        report.append("  • Battery helps balance daily variations")
        report.append("  • Annual averaging would be misleading")
        report.append("=" * 80)
        
        # Display results
        comparison_report = "\n".join(report)
        self.comparison_text.clear()
        self.comparison_text.setPlainText(comparison_report)
        
        # Switch to comparison tab
        self.tab_widget.setCurrentWidget(self.tab_comparison)
        
        QMessageBox.information(self, "Success", "Scenario comparison completed!")
    
    def show_battery_recommendation(self):
        """Calculate and display recommended battery capacity"""
        try:
            # Get consumption values
            monthly_consumption = float(self.monthly_consumption.text())
            daily_household = monthly_consumption / 30
            
            # Get EV consumption if enabled
            daily_ev = 0
            if self.ev_enabled.isChecked():
                daily_km = float(self.ev_daily_km.text())
                efficiency = float(self.ev_efficiency.text())
                daily_ev = daily_km * efficiency / 100.0
            
            total_daily = daily_household + daily_ev
            
            # Calculate recommendations (50-80% of daily consumption)
            min_rec = total_daily * 0.5
            optimal_rec = total_daily * 0.65
            max_rec = total_daily * 0.8
            
            # Build recommendation message
            message = "🔋 Battery Capacity Recommendations\n\n"
            message += f"Daily Consumption:\n"
            message += f"  • Household: {daily_household:.1f} kWh/day\n"
            if daily_ev > 0:
                message += f"  • EV Charging: {daily_ev:.1f} kWh/day\n"
            message += f"  • Total: {total_daily:.1f} kWh/day\n\n"
            
            message += f"Recommended Battery Capacity:\n"
            message += f"  • Minimum: {min_rec:.1f} kWh (50% of daily)\n"
            message += f"  • Optimal: {optimal_rec:.1f} kWh (65% of daily) ⭐\n"
            message += f"  • Maximum: {max_rec:.1f} kWh (80% of daily)\n\n"
            
            message += "Note: These recommendations assume:\n"
            message += "  • Battery charges from excess PV during day\n"
            message += "  • Battery discharges for household evening peak\n"
            message += "  • Battery can also charge EV at night if capacity available\n"
            message += "  • Not all daily consumption happens during battery discharge period\n\n"
            
            # Current battery capacity
            current = float(self.battery_capacity.text())
            message += f"Your Current Setting: {current:.1f} kWh\n"
            
            if current < min_rec:
                message += f"⚠️ Below minimum recommendation (add {min_rec - current:.1f} kWh)\n"
            elif current < optimal_rec:
                message += f"✓ Acceptable, but consider increasing to {optimal_rec:.1f} kWh\n"
            elif current <= max_rec:
                message += f"✓ Good capacity for your needs!\n"
            else:
                message += f"ℹ️ Above typical recommendation (may be oversized)\n"
            
            QMessageBox.information(self, "Battery Capacity Recommendation", message)
            
        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please enter valid numbers for consumption and EV parameters.")
    
    def check_calculator(self):
        """Check if calculator is initialized"""
        if not GRAPHS_AVAILABLE:
            QMessageBox.critical(self, "Error", "Graphing functionality not available.\n\n"
                                        "Please install: pip install matplotlib numpy")
            return False
        
        if not self.current_calculator:
            QMessageBox.warning(self, "Warning", "Please run a calculation first before generating graphs.")
            return False
        
        return True
    
    def show_breakeven_graph(self):
        """Show break-even analysis graph"""
        if not self.check_calculator():
            return
        
        self.graph_status.setText("Generating break-even analysis...")
        QApplication.processEvents()
        
        try:
            graph_gen = PVGraphGenerator(self.current_calculator)
            graph_gen.plot_breakeven_analysis(show=True)
            self.graph_status.setText("✓ Break-even graph displayed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating graph: {str(e)}")
            self.graph_status.setText("✗ Error generating graph")
    
    def show_cost_comparison_graph(self):
        """Show cost comparison graph"""
        if not self.check_calculator():
            return
        
        self.graph_status.setText("Generating cost comparison...")
        QApplication.processEvents()
        
        try:
            graph_gen = PVGraphGenerator(self.current_calculator)
            graph_gen.plot_cost_comparison(show=True)
            self.graph_status.setText("✓ Cost comparison graph displayed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating graph: {str(e)}")
            self.graph_status.setText("✗ Error generating graph")
    
    def show_energy_flow_graph(self):
        """Show energy flow graph"""
        if not self.check_calculator():
            return
        
        self.graph_status.setText("Generating energy flow...")
        QApplication.processEvents()
        
        try:
            graph_gen = PVGraphGenerator(self.current_calculator)
            graph_gen.plot_energy_flow(show=True)
            self.graph_status.setText("✓ Energy flow graph displayed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating graph: {str(e)}")
            self.graph_status.setText("✗ Error generating graph")
    
    def show_roi_graph(self):
        """Show ROI comparison graph"""
        if not self.check_calculator():
            return
        
        self.graph_status.setText("Generating ROI comparison...")
        QApplication.processEvents()
        
        try:
            graph_gen = PVGraphGenerator(self.current_calculator)
            graph_gen.plot_roi_comparison(show=True)
            self.graph_status.setText("✓ ROI comparison graph displayed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating graph: {str(e)}")
            self.graph_status.setText("✗ Error generating graph")
    
    def show_seasonal_graph(self):
        """Show monthly seasonal analysis graph"""
        if not self.check_calculator():
            return
        
        self.graph_status.setText("Generating monthly seasonal analysis...")
        QApplication.processEvents()
        
        try:
            graph_gen = PVGraphGenerator(self.current_calculator)
            graph_gen.plot_monthly_seasonal_analysis(show=True)
            self.graph_status.setText("✓ Monthly seasonal analysis displayed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating graph: {str(e)}")
            self.graph_status.setText("✗ Error generating graph")
    
    def show_revenue_offsetting_graph(self):
        """Show monthly revenue offsetting graph"""
        if not self.check_calculator():
            return
        
        self.graph_status.setText("Generating revenue offsetting analysis...")
        QApplication.processEvents()
        
        try:
            graph_gen = PVGraphGenerator(self.current_calculator)
            graph_gen.plot_monthly_revenue_offsetting(show=True)
            self.graph_status.setText("✓ Revenue offsetting analysis displayed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating graph: {str(e)}")
            self.graph_status.setText("✗ Error generating graph")
    
    def generate_all_graphs(self):
        """Generate and save all graphs"""
        if not self.check_calculator():
            return
        
        self.graph_status.setText("Generating all graphs...")
        QApplication.processEvents()
        
        try:
            graph_gen = PVGraphGenerator(self.current_calculator)
            saved_files = graph_gen.generate_all_graphs(show=True)
            
            self.graph_status.setText(f"✓ All graphs generated and saved ({len(saved_files)} files)")
            
            file_list = "\n".join([os.path.basename(f) for f in saved_files])
            QMessageBox.information(self, "Success", 
                              f"All graphs have been generated and saved!\n\n"
                              f"Files created:\n{file_list}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating graphs: {str(e)}")
            self.graph_status.setText("✗ Error generating graphs")


def main():
    app = QApplication(sys.argv)
    window = PVCalculatorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

