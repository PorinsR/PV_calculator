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
    QTextEdit, QScrollArea, QGroupBox, QMessageBox, QSizePolicy, QSpinBox
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

# Try to import consumption pattern generator (Version 2)
try:
    from PV_consumption_generator import ConsumptionPatternGenerator, HouseholdProfile, EVConsumptionProfile
    from PV_consumption_graphs import ConsumptionGraphGenerator
    CONSUMPTION_V2_AVAILABLE = True
except ImportError:
    CONSUMPTION_V2_AVAILABLE = False
    EVConsumptionProfile = None
    print("Warning: Consumption pattern generator V2 not available")

# Try to import solar generation calculator (Version 2)
try:
    from PV_solar_generator import SolarGenerationCalculator, SolarSystemProfile, LOCATIONS
    from PV_solar_graphs import SolarComparisonGraphs
    SOLAR_V2_AVAILABLE = True
except ImportError:
    SOLAR_V2_AVAILABLE = False
    print("Warning: Solar generation calculator V2 not available")

# Try to import battery flow and integrated visualizations (Version 2)
try:
    from PV_battery_flow import BatteryFlowCalculator
    from PV_integrated_graphs import IntegratedEnergyGraphs
    INTEGRATED_V2_AVAILABLE = True
except ImportError:
    INTEGRATED_V2_AVAILABLE = False
    print("Warning: Integrated energy flow visualization V2 not available")


class PVCalculatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PV System Feasibility Calculator")
        self.resize(900, 800)
        
        # Initialize caches for enhanced features
        self.enhanced_solar_cache = None
        self.enhanced_ev_cache = None
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs (simplified to 2 tabs)
        self.tab_input = QWidget()
        self.tab_unified_v2 = QWidget()  # Unified Energy Flow Analysis
        
        self.tab_widget.addTab(self.tab_input, "Input Parameters")
        self.tab_widget.addTab(self.tab_unified_v2, "🔋 Energy Flow Analysis")
        
        # Initialize data structures BEFORE setting up tabs
        # Store calculator for graphs
        self.current_calculator = None
        
        # Store EV consumption profile for use in graphs/analysis
        self.current_ev_consumption_profile = None
        
        # Store consumption pattern generator (V2) - MUST be before setup_consumption_v2_tab()
        if CONSUMPTION_V2_AVAILABLE:
            self.consumption_generator = ConsumptionPatternGenerator()
        else:
            self.consumption_generator = None
        
        # Store solar generation calculator (V2) - MUST be before setup_solar_v2_tab()
        if SOLAR_V2_AVAILABLE:
            self.solar_generator = SolarGenerationCalculator()
        else:
            self.solar_generator = None
        
        # Store battery SOC cache for continuity between days
        # Key: (year, day_of_year), Value: final_soc
        self.battery_soc_cache = {}
        
        # Setup tabs (after initializing generators)
        self.setup_input_tab()
        self.setup_unified_v2_tab()  # Unified Energy Flow
        
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
        consumption_main_layout = QVBoxLayout()
        consumption_group.setLayout(consumption_main_layout)
        
        consumption_layout = QHBoxLayout()
        consumption_layout.addWidget(QLabel("Monthly Household Consumption (kWh):"))
        self.monthly_consumption = QLineEdit("500")
        consumption_layout.addWidget(self.monthly_consumption)
        hint_label = QLabel("(household only, without EV)")
        hint_label.setStyleSheet("color: gray; font-style: italic;")
        consumption_layout.addWidget(hint_label)
        consumption_layout.addStretch()
        consumption_main_layout.addLayout(consumption_layout)
        
        # V2: Consumption pattern type
        from PyQt5.QtWidgets import QComboBox
        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(QLabel("Consumption Pattern Type:"))
        self.consumption_pattern_type = QComboBox()
        if CONSUMPTION_V2_AVAILABLE and self.consumption_generator:
            patterns = self.consumption_generator.get_available_patterns()
            for pattern in patterns:
                info = self.consumption_generator.get_pattern_info(pattern)
                self.consumption_pattern_type.addItem(info['name'], pattern)
        else:
            self.consumption_pattern_type.addItem("Working Family", "working_family")
        pattern_layout.addWidget(self.consumption_pattern_type)
        pattern_layout.addStretch()
        consumption_main_layout.addLayout(pattern_layout)
        
        # V2: Seasonal strength
        from PyQt5.QtWidgets import QSlider
        seasonal_layout = QHBoxLayout()
        seasonal_layout.addWidget(QLabel("Seasonal Variation:"))
        self.consumption_seasonal = QSlider(Qt.Horizontal)
        self.consumption_seasonal.setMinimum(0)
        self.consumption_seasonal.setMaximum(50)
        self.consumption_seasonal.setValue(20)
        self.consumption_seasonal.setTickPosition(QSlider.TicksBelow)
        self.consumption_seasonal.setTickInterval(10)
        self.consumption_seasonal.setFixedWidth(150)
        seasonal_layout.addWidget(self.consumption_seasonal)
        
        self.consumption_seasonal_label = QLabel("0.20")
        self.consumption_seasonal_label.setMinimumWidth(40)
        seasonal_layout.addWidget(self.consumption_seasonal_label)
        
        self.consumption_seasonal.valueChanged.connect(
            lambda v: self.consumption_seasonal_label.setText(f"{v/100:.2f}")
        )
        
        seasonal_hint = QLabel("(0.1=minimal, 0.2=typical, 0.3=high)")
        seasonal_hint.setStyleSheet("color: gray; font-style: italic; font-size: 8pt;")
        seasonal_layout.addWidget(seasonal_hint)
        seasonal_layout.addStretch()
        consumption_main_layout.addLayout(seasonal_layout)
        
        # Day-wise consumption profile info
        daywise_info = QLabel(
            "✨ V2 Features: Realistic consumption patterns with Gaussian seasonal distribution\n"
            "• Weekdays: Baseline with morning (7-8) and evening (18-22) peaks\n"
            "• Weekends: Flat distribution, 15% higher overall consumption\n"
            "• Seasonal: Winter peak (higher heating), summer low"
        )
        daywise_info.setWordWrap(True)
        daywise_info.setStyleSheet("color: darkblue; font-style: italic; font-size: 9pt; background-color: #e8f4f8; padding: 5px; border-radius: 3px;")
        consumption_main_layout.addWidget(daywise_info)
        
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
        
        # V2: Location selector
        location_layout = QHBoxLayout()
        self.pv_location = QComboBox()
        if SOLAR_V2_AVAILABLE:
            for key, loc in LOCATIONS.items():
                self.pv_location.addItem(f"{loc.name} ({loc.avg_daily_irradiance} kWh/m²/day)", key)
            # Set default based on solar_irradiance value if possible
            self.pv_location.setCurrentIndex(0)  # Default to first (Riga)
        else:
            self.pv_location.addItem("Manual Entry", "manual")
        location_layout.addWidget(self.pv_location)
        location_hint = QLabel("(V2: Auto-calculates irradiance)")
        location_hint.setStyleSheet("color: gray; font-style: italic; font-size: 8pt;")
        location_layout.addWidget(location_hint)
        location_layout.addStretch()
        pv_form.addRow("Location:", location_layout)
        
        # V2: Panel tilt
        from PyQt5.QtWidgets import QDoubleSpinBox
        self.pv_tilt = QDoubleSpinBox()
        self.pv_tilt.setMinimum(0)
        self.pv_tilt.setMaximum(90)
        self.pv_tilt.setValue(35)
        self.pv_tilt.setSuffix("°")
        pv_form.addRow("Panel Tilt Angle:", self.pv_tilt)
        
        pv_layout.addLayout(pv_form)
        
        # Enhanced Solar Data Section
        enhanced_solar_layout = QHBoxLayout()
        
        fetch_solar_btn = QPushButton("🌐 Fetch Real Solar Data from PVGIS")
        fetch_solar_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        fetch_solar_btn.clicked.connect(self.fetch_enhanced_solar_data)
        fetch_solar_btn.setToolTip("Fetch accurate solar production data from PVGIS (EU Science Hub)\nBased on real satellite and weather data for your location")
        enhanced_solar_layout.addWidget(fetch_solar_btn)
        
        pv_layout.addLayout(enhanced_solar_layout)
        
        # Data source indicator
        self.solar_data_source = QLabel("📊 Using: Built-in solar model")
        self.solar_data_source.setStyleSheet("color: #666; font-style: italic; font-size: 9pt; padding: 5px;")
        pv_layout.addWidget(self.solar_data_source)
        
        # Info about enhanced features
        enhanced_info = QLabel(
            "💡 Enhanced Solar Data:\n"
            "• PVGIS: EU Science Hub's accurate satellite-based solar radiation data\n"
            "• Weather: Historical cloud cover data for location-specific accuracy\n"
            "• Accuracy: ±5-8% (vs ±15-25% with built-in model)\n"
            "• No installation needed - uses direct API calls!"
        )
        enhanced_info.setWordWrap(True)
        enhanced_info.setStyleSheet("color: darkgreen; font-style: italic; font-size: 8pt; background-color: #e8f5e9; padding: 5px; border-radius: 3px;")
        pv_layout.addWidget(enhanced_info)
        
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
        
        # Initialize structured EV database
        try:
            from PV_ev_database_structured import StructuredEVDatabase
            self.ev_database = StructuredEVDatabase()
        except ImportError:
            self.ev_database = None
            print("Warning: Structured EV database not available")
        
        # Car Make
        from PyQt5.QtWidgets import QComboBox
        self.ev_make = QComboBox()
        self.ev_make.addItem("-- Select Make --", "")
        
        # Populate makes from database
        if self.ev_database:
            for make in self.ev_database.get_makes():
                self.ev_make.addItem(make, make)
        
        self.ev_make.currentIndexChanged.connect(self.on_ev_make_changed)
        ev_form.addRow("Make:", self.ev_make)
        
        # Car Model
        self.ev_model = QComboBox()
        self.ev_model.addItem("-- Select Model --", "")
        self.ev_model.currentIndexChanged.connect(self.on_ev_model_changed)
        ev_form.addRow("Model:", self.ev_model)
        
        # Configuration (Battery, Drivetrain, Year)
        self.ev_configuration = QComboBox()
        self.ev_configuration.addItem("-- Select Configuration --", "")
        self.ev_configuration.currentIndexChanged.connect(self.on_ev_configuration_changed)
        ev_form.addRow("Configuration:", self.ev_configuration)
        
        # Consumption (auto-filled, read-only)
        consumption_h = QHBoxLayout()
        self.ev_consumption_display = QLineEdit("--")
        self.ev_consumption_display.setReadOnly(True)
        self.ev_consumption_display.setStyleSheet("background-color: white;")
        consumption_h.addWidget(self.ev_consumption_display)
        consumption_hint = QLabel("kWh/100km")
        consumption_hint.setStyleSheet("color: gray; font-style: italic;")
        consumption_h.addWidget(consumption_hint)
        consumption_h.addStretch()
        ev_form.addRow("Consumption:", consumption_h)
        
        # Weekly distance
        self.ev_weekly_km = QLineEdit("420")
        ev_form.addRow("Weekly Distance (km):", self.ev_weekly_km)
        
        # Charger power
        pow_h = QHBoxLayout()
        self.ev_charger_power = QLineEdit("7.0")
        pow_h.addWidget(self.ev_charger_power)
        pow_hint = QLabel("(typical: 3.7, 7, 11, or 22 kW)")
        pow_hint.setStyleSheet("color: gray; font-style: italic;")
        pow_h.addWidget(pow_hint)
        pow_h.addStretch()
        ev_form.addRow("Home Charger Power (kW):", pow_h)
        
        ev_layout.addLayout(ev_form)
        
        # Charging Start Time
        charging_start_layout = QHBoxLayout()
        charging_start_layout.addWidget(QLabel("Charging Start Time:"))
        
        self.ev_charging_start = QSpinBox()
        self.ev_charging_start.setMinimum(0)
        self.ev_charging_start.setMaximum(23)
        self.ev_charging_start.setValue(22)  # Default: 22:00
        self.ev_charging_start.setSuffix(":00")
        charging_start_layout.addWidget(self.ev_charging_start)
        
        charging_hint = QLabel("(charging will continue until daily consumption is met)")
        charging_hint.setStyleSheet("color: gray; font-style: italic; font-size: 9pt;")
        charging_start_layout.addWidget(charging_hint)
        charging_start_layout.addStretch()
        ev_layout.addLayout(charging_start_layout)
        
        # Charging duration info (calculated automatically)
        self.ev_duration_info = QLabel("")
        self.ev_duration_info.setStyleSheet("color: darkblue; font-style: italic; font-size: 9pt;")
        self.ev_duration_info.setWordWrap(True)
        ev_layout.addWidget(self.ev_duration_info)
        
        # Update duration info when values change
        self.ev_weekly_km.textChanged.connect(self.update_ev_charging_duration)
        self.ev_consumption_display.textChanged.connect(self.update_ev_charging_duration)
        self.ev_charger_power.textChanged.connect(self.update_ev_charging_duration)
        self.ev_charging_start.valueChanged.connect(self.update_ev_charging_duration)
        
        ev_info = QLabel("💡 Select your car to auto-fill consumption. Charging starts at selected time and continues until daily needs are met.")
        ev_info.setWordWrap(True)
        ev_info.setStyleSheet("color: blue; font-style: italic; font-size: 9pt;")
        ev_layout.addWidget(ev_info)
        
        main_layout.addWidget(ev_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Configuration")
        save_btn.clicked.connect(self.save_configuration)
        button_layout.addWidget(save_btn)
        
        load_btn = QPushButton("Load Configuration")
        load_btn.clicked.connect(self.load_configuration)
        button_layout.addWidget(load_btn)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
    
    def get_ev_database(self):
        """EV consumption database by make/model/year"""
        return {
            'tesla': {
                'Model 3': {'2024': 14.4, '2023': 14.4, '2022': 15.0, '2021': 15.5, '2020': 15.5, '2019': 15.8},
                'Model Y': {'2024': 16.9, '2023': 16.9, '2022': 17.1, '2021': 17.1, '2020': 17.8},
                'Model S': {'2024': 17.3, '2023': 18.1, '2022': 18.5, '2021': 19.0, '2020': 19.5},
                'Model X': {'2024': 19.5, '2023': 20.0, '2022': 20.5, '2021': 21.0, '2020': 21.5}
            },
            'vw': {
                'ID.3': {'2024': 15.5, '2023': 15.8, '2022': 16.0, '2021': 16.2, '2020': 16.5},
                'ID.4': {'2024': 17.5, '2023': 17.8, '2022': 18.0, '2021': 18.5},
                'ID.5': {'2024': 18.5, '2023': 18.8, '2022': 19.0},
                'e-Golf': {'2020': 17.3, '2019': 17.5, '2018': 17.8}
            },
            'bmw': {
                'i3': {'2022': 16.3, '2021': 16.5, '2020': 16.8, '2019': 17.0, '2018': 17.2},
                'i4': {'2024': 18.1, '2023': 18.5, '2022': 19.0},
                'iX': {'2024': 21.4, '2023': 21.8, '2022': 22.5},
                'iX3': {'2024': 18.9, '2023': 19.2, '2022': 19.5, '2021': 19.8}
            },
            'nissan': {
                'Leaf': {'2024': 17.1, '2023': 17.3, '2022': 17.5, '2021': 17.8, '2020': 18.0, '2019': 18.5},
                'Ariya': {'2024': 19.0, '2023': 19.5, '2022': 20.0}
            },
            'hyundai': {
                'Ioniq 5': {'2024': 18.0, '2023': 18.5, '2022': 19.0, '2021': 19.5},
                'Kona Electric': {'2024': 16.8, '2023': 17.0, '2022': 17.3, '2021': 17.5, '2020': 17.8, '2019': 18.0},
                'Ioniq Electric': {'2022': 15.5, '2021': 15.8, '2020': 16.0, '2019': 16.3}
            },
            'kia': {
                'EV6': {'2024': 18.0, '2023': 18.5, '2022': 19.0},
                'Niro EV': {'2024': 16.5, '2023': 16.8, '2022': 17.0, '2021': 17.3, '2020': 17.5, '2019': 17.8},
                'e-Soul': {'2023': 17.5, '2022': 17.8, '2021': 18.0, '2020': 18.3}
            },
            'audi': {
                'e-tron': {'2024': 22.5, '2023': 23.0, '2022': 23.5, '2021': 24.0, '2020': 24.5, '2019': 25.0},
                'Q4 e-tron': {'2024': 18.5, '2023': 19.0, '2022': 19.5, '2021': 20.0},
                'e-tron GT': {'2024': 21.6, '2023': 22.0, '2022': 22.5, '2021': 23.0}
            },
            'mercedes': {
                'EQC': {'2024': 22.2, '2023': 22.5, '2022': 23.0, '2021': 23.5, '2020': 24.0, '2019': 24.5},
                'EQA': {'2024': 18.0, '2023': 18.5, '2022': 19.0, '2021': 19.5},
                'EQS': {'2024': 19.8, '2023': 20.5, '2022': 21.0}
            },
            'renault': {
                'Zoe': {'2024': 17.2, '2023': 17.5, '2022': 17.7, '2021': 18.0, '2020': 18.5, '2019': 19.0},
                'Megane E-Tech': {'2024': 16.0, '2023': 16.5, '2022': 17.0}
            },
            'peugeot': {
                'e-208': {'2024': 15.5, '2023': 15.8, '2022': 16.0, '2021': 16.3, '2020': 16.5},
                'e-2008': {'2024': 17.0, '2023': 17.3, '2022': 17.5, '2021': 17.8, '2020': 18.0}
            }
        }
    
    def on_ev_make_changed(self):
        """Update model dropdown when make is selected"""
        self.ev_model.clear()
        self.ev_model.addItem("-- Select Model --", "")
        self.ev_configuration.clear()
        self.ev_configuration.addItem("-- Select Configuration --", "")
        self.ev_consumption_display.setText("--")
        
        make = self.ev_make.currentData()
        if make and self.ev_database:
            models = self.ev_database.get_models(make)
            for model in models:
                self.ev_model.addItem(model, model)
    
    def on_ev_model_changed(self):
        """Update configuration dropdown when model is selected"""
        self.ev_configuration.clear()
        self.ev_configuration.addItem("-- Select Configuration --", "")
        self.ev_consumption_display.setText("--")
        
        make = self.ev_make.currentData()
        model = self.ev_model.currentData()
        if make and model and self.ev_database:
            configurations = self.ev_database.get_configurations(make, model)
            for config in configurations:
                self.ev_configuration.addItem(config, config)
    
    def on_ev_configuration_changed(self):
        """Update consumption display when configuration is selected"""
        make = self.ev_make.currentData()
        model = self.ev_model.currentData()
        configuration = self.ev_configuration.currentData()
        
        if make and model and configuration and self.ev_database:
            consumption = self.ev_database.get_consumption(make, model, configuration)
            if consumption:
                self.ev_consumption_display.setText(f"{consumption:.1f}")
                self.update_ev_charging_duration()
            else:
                self.ev_consumption_display.setText("--")
        else:
            self.ev_consumption_display.setText("--")
    
    def update_ev_charging_duration(self):
        """Update EV charging duration information display"""
        try:
            # Get consumption from display
            consumption_text = self.ev_consumption_display.text()
            if not consumption_text or consumption_text == "--":
                self.ev_duration_info.setText("")
                return
            
            efficiency = float(consumption_text)
            weekly_km = float(self.ev_weekly_km.text())
            charger_power = float(self.ev_charger_power.text())
            start_hour = self.ev_charging_start.value()
            
            # Calculate daily consumption
            daily_km = weekly_km / 7.0
            daily_kwh = daily_km * efficiency / 100.0
            
            # Calculate charging duration
            duration_hours = daily_kwh / charger_power
            
            # Calculate end hour
            end_hour_decimal = (start_hour + duration_hours) % 24
            end_hour = int(end_hour_decimal)
            end_minute = int((end_hour_decimal - end_hour) * 60)
            
            # Format duration
            hours_int = int(duration_hours)
            minutes_int = int((duration_hours - hours_int) * 60)
            
            info_text = (
                f"ℹ️ Daily EV consumption: {daily_kwh:.2f} kWh | "
                f"Charging duration: {hours_int}h {minutes_int}min | "
                f"Charging period: {start_hour:02d}:00 - {end_hour:02d}:{end_minute:02d}"
            )
            self.ev_duration_info.setText(info_text)
            
        except (ValueError, ZeroDivisionError):
            self.ev_duration_info.setText("")
    
    def fetch_ev_data_from_web(self):
        """Fetch EV consumption data from enhanced ev-database.org source"""
        try:
            # Get user input from dropdowns
            make = self.ev_make.currentText().strip() if hasattr(self, 'ev_make') else ""
            model = self.ev_model.currentText().strip() if hasattr(self, 'ev_model') else ""
            
            # Skip if default/empty selections
            if not make or not model or "Select" in make or "Select" in model:
                QMessageBox.warning(self, "Input Required", "Please enter EV make and model first.")
                return
            
            self.unified_status.setText(f"🔍 Searching EV database for {make} {model}...")
            QApplication.processEvents()
            
            # Try to use enhanced EV database
            try:
                from PV_enhanced_ev_data import fetch_ev_consumption
                result = fetch_ev_consumption(make, model)
                
                if result['found']:
                    consumption = result['consumption_kwh100km']
                    self.ev_consumption_display.setText(f"{consumption:.1f}")
                    self.update_ev_charging_duration()
                    
                    QMessageBox.information(
                        self,
                        "✓ Data Found",
                        f"Found: {result['matched_name']}\n\n"
                        f"Consumption: {consumption:.1f} kWh/100km\n"
                        f"Source: {result['source']}\n\n"
                        f"⚠️ {result['note']}"
                    )
                    self.unified_status.setText("✓ EV data loaded from ev-database.org")
                    return
                else:
                    QMessageBox.warning(
                        self,
                        "Not Found", 
                        f"{result['error']}\n\n"
                        f"Available makes: {', '.join(result['available_makes'][:10])}...\n\n"
                        f"{result['suggestion']}"
                    )
                    self.unified_status.setText("✗ EV not found in database")
                    return
                    
            except ImportError:
                pass  # Fall back to built-in database
            
            # Try to fetch from EV Database API
            import urllib.request
            import urllib.parse
            import json
            
            # Comprehensive EV database (curated from multiple sources)
            ev_database = {
                # Tesla
                "tesla model 3": {"consumption": 14.5, "source": "EPA/WLTP avg"},
                "tesla model 3 long range": {"consumption": 14.8, "source": "EPA"},
                "tesla model 3 performance": {"consumption": 15.2, "source": "EPA"},
                "tesla model y": {"consumption": 16.1, "source": "EPA"},
                "tesla model y long range": {"consumption": 16.5, "source": "EPA"},
                "tesla model y performance": {"consumption": 17.0, "source": "EPA"},
                "tesla model s": {"consumption": 18.1, "source": "EPA"},
                "tesla model s plaid": {"consumption": 19.5, "source": "EPA"},
                "tesla model x": {"consumption": 20.2, "source": "EPA"},
                "tesla model x plaid": {"consumption": 21.0, "source": "EPA"},
                
                # Nissan
                "nissan leaf": {"consumption": 17.0, "source": "WLTP"},
                "nissan leaf e+": {"consumption": 16.5, "source": "WLTP"},
                "nissan ariya": {"consumption": 18.0, "source": "WLTP"},
                
                # BMW
                "bmw i3": {"consumption": 13.5, "source": "WLTP"},
                "bmw i3s": {"consumption": 14.0, "source": "WLTP"},
                "bmw i4 edrive40": {"consumption": 16.1, "source": "WLTP"},
                "bmw i4 m50": {"consumption": 18.0, "source": "WLTP"},
                "bmw ix xdrive40": {"consumption": 19.4, "source": "WLTP"},
                "bmw ix xdrive50": {"consumption": 21.4, "source": "WLTP"},
                "bmw ix3": {"consumption": 17.8, "source": "WLTP"},
                
                # Volkswagen
                "volkswagen id.3": {"consumption": 15.4, "source": "WLTP"},
                "volkswagen id.3 pro": {"consumption": 15.9, "source": "WLTP"},
                "volkswagen id.4": {"consumption": 16.9, "source": "WLTP"},
                "volkswagen id.4 pro": {"consumption": 17.5, "source": "WLTP"},
                "volkswagen id.5": {"consumption": 18.0, "source": "WLTP"},
                "volkswagen id.buzz": {"consumption": 20.0, "source": "WLTP"},
                "volkswagen e-golf": {"consumption": 14.1, "source": "WLTP"},
                
                # Audi
                "audi e-tron": {"consumption": 22.4, "source": "WLTP"},
                "audi e-tron gt": {"consumption": 19.6, "source": "WLTP"},
                "audi e-tron sportback": {"consumption": 21.8, "source": "WLTP"},
                "audi q4 e-tron": {"consumption": 17.0, "source": "WLTP"},
                "audi q4 sportback e-tron": {"consumption": 16.6, "source": "WLTP"},
                
                # Hyundai
                "hyundai kona": {"consumption": 14.7, "source": "WLTP"},
                "hyundai kona electric": {"consumption": 14.7, "source": "WLTP"},
                "hyundai ioniq 5": {"consumption": 16.8, "source": "WLTP"},
                "hyundai ioniq 6": {"consumption": 14.3, "source": "WLTP"},
                "hyundai ioniq electric": {"consumption": 13.8, "source": "WLTP"},
                
                # Kia
                "kia niro ev": {"consumption": 15.9, "source": "WLTP"},
                "kia ev6": {"consumption": 16.5, "source": "WLTP"},
                "kia ev6 gt": {"consumption": 18.0, "source": "WLTP"},
                "kia soul ev": {"consumption": 15.7, "source": "WLTP"},
                "kia e-niro": {"consumption": 15.9, "source": "WLTP"},
                
                # Porsche
                "porsche taycan": {"consumption": 20.8, "source": "WLTP"},
                "porsche taycan 4s": {"consumption": 21.5, "source": "WLTP"},
                "porsche taycan turbo": {"consumption": 23.4, "source": "WLTP"},
                
                # Mercedes
                "mercedes eqc": {"consumption": 21.3, "source": "WLTP"},
                "mercedes eqs": {"consumption": 19.1, "source": "WLTP"},
                "mercedes eqe": {"consumption": 17.3, "source": "WLTP"},
                "mercedes eqa": {"consumption": 16.9, "source": "WLTP"},
                "mercedes eqb": {"consumption": 17.6, "source": "WLTP"},
                
                # Other brands
                "jaguar i-pace": {"consumption": 22.0, "source": "WLTP"},
                "polestar 2": {"consumption": 16.5, "source": "WLTP"},
                "polestar 3": {"consumption": 19.0, "source": "WLTP"},
                "renault zoe": {"consumption": 17.2, "source": "WLTP"},
                "renault megane e-tech": {"consumption": 15.2, "source": "WLTP"},
                "chevrolet bolt": {"consumption": 16.9, "source": "EPA"},
                "chevrolet bolt euv": {"consumption": 17.2, "source": "EPA"},
                "ford mustang mach-e": {"consumption": 18.5, "source": "EPA"},
                "ford f-150 lightning": {"consumption": 25.0, "source": "EPA est"},
                "volvo xc40 recharge": {"consumption": 19.3, "source": "WLTP"},
                "volvo c40 recharge": {"consumption": 19.0, "source": "WLTP"},
                "skoda enyaq": {"consumption": 16.7, "source": "WLTP"},
                "skoda enyaq coupe": {"consumption": 16.3, "source": "WLTP"},
                "mg zs ev": {"consumption": 17.3, "source": "WLTP"},
                "mg4": {"consumption": 15.5, "source": "WLTP"},
                "mg4 xpower": {"consumption": 16.8, "source": "WLTP"},
                "byd atto 3": {"consumption": 16.0, "source": "WLTP"},
                "byd han": {"consumption": 15.5, "source": "WLTP"},
                "byd tang": {"consumption": 19.0, "source": "WLTP"},
                "citroen e-c4": {"consumption": 16.3, "source": "WLTP"},
                "peugeot e-208": {"consumption": 15.0, "source": "WLTP"},
                "peugeot e-2008": {"consumption": 15.8, "source": "WLTP"},
                "opel corsa-e": {"consumption": 15.0, "source": "WLTP"},
                "opel mokka-e": {"consumption": 15.8, "source": "WLTP"},
                "fiat 500e": {"consumption": 13.0, "source": "WLTP"},
                "mini cooper se": {"consumption": 14.8, "source": "WLTP"},
                "seat cupra born": {"consumption": 15.6, "source": "WLTP"},
                "mazda mx-30": {"consumption": 16.5, "source": "WLTP"},
                "honda e": {"consumption": 17.2, "source": "WLTP"},
                "lucid air": {"consumption": 13.5, "source": "EPA"},
                "rivian r1t": {"consumption": 24.0, "source": "EPA est"},
                "rivian r1s": {"consumption": 25.0, "source": "EPA est"},
            }
            
            # Normalize search term
            search_term = f"{make} {model}".lower().strip()
            
            # Search for match (exact and partial)
            consumption_data = None
            matched_key = None
            best_match_score = 0
            
            for key, data in ev_database.items():
                # Try exact match first
                if search_term == key:
                    consumption_data = data
                    matched_key = key
                    break
                
                # Partial matching
                make_lower = make.lower()
                model_lower = model.lower().replace(" ", "")
                key_no_spaces = key.replace(" ", "")
                
                if make_lower in key and model_lower in key_no_spaces:
                    # Calculate match quality
                    match_score = len(model_lower) / len(key_no_spaces)
                    if match_score > best_match_score:
                        best_match_score = match_score
                        consumption_data = data
                        matched_key = key
            
            if consumption_data:
                consumption = consumption_data["consumption"]
                source = consumption_data["source"]
                
                self.ev_consumption_display.setText(f"{consumption:.1f}")
                self.update_ev_charging_duration()
                
                QMessageBox.information(
                    self, 
                    "✓ Data Found", 
                    f"Found: {matched_key.title()}\n\n"
                    f"Consumption: {consumption:.1f} kWh/100km\n"
                    f"Source: {source}\n\n"
                    f"⚠️ Note: Real-world consumption varies based on:\n"
                    f"• Driving style (aggressive vs eco)\n"
                    f"• Weather conditions (heating/AC use)\n"
                    f"• Road type (highway vs city)\n"
                    f"• Tire pressure and vehicle load\n"
                    f"• Terrain (hills, mountains)\n\n"
                    f"Typical variation: ±20-30%"
                )
                self.unified_status.setText("✓ EV data loaded successfully")
            else:
                # No match found - show helpful message
                available_makes = sorted(set(k.split()[0] for k in ev_database.keys()))
                makes_list = ", ".join(available_makes[:15])
                
                QMessageBox.warning(
                    self,
                    "Not Found",
                    f"Could not find '{make} {model}' in database.\n\n"
                    f"Available makes: {makes_list}...\n\n"
                    f"Tips:\n"
                    f"• Check spelling\n"
                    f"• Try without trim level (e.g., 'Model 3' not 'Model 3 LR')\n"
                    f"• Use official model name\n\n"
                    f"Database contains {len(ev_database)} vehicles."
                )
                self.unified_status.setText("✗ EV not found in database")
        
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Error", f"Error fetching EV data:\n{str(e)}\n\n{traceback.format_exc()}")
            self.unified_status.setText("✗ Error fetching EV data")
    
    def fetch_enhanced_solar_data(self):
        """Fetch enhanced solar production data from PVGIS and weather APIs"""
        try:
            # Get current system parameters
            lat = 56.95  # Default Riga
            lon = 24.11
            
            # Try to get location from selection
            if hasattr(self, 'pv_location'):
                location_key = self.pv_location.currentData()
                if location_key and location_key in LOCATIONS:
                    location = LOCATIONS[location_key]
                    lat = location.latitude
                    lon = location.longitude
            
            peak_power = float(self.pv_size.text())
            tilt = float(self.pv_tilt.value()) if hasattr(self, 'pv_tilt') else 35.0
            azimuth = 22.5  # SSW (South-South-West) - matches typical roof orientation
            
            self.solar_data_source.setText("🔄 Fetching PVGIS data...")
            QApplication.processEvents()
            
            # Import enhanced solar calculator
            try:
                from PV_enhanced_solar import calculate_enhanced_solar_production
                
                result = calculate_enhanced_solar_production(
                    lat=lat,
                    lon=lon,
                    peak_power_kw=peak_power,
                    tilt=tilt,
                    azimuth=azimuth,
                    system_efficiency=0.8948,  # 10.52% total losses (angle of incidence, spectral, temperature)
                    use_pvgis=True,
                    use_weather=True
                )
                
                # Build result message
                data_source = result['data_source']
                message_parts = [f"✓ Successfully fetched PVGIS solar data!\n"]
                message_parts.append(f"\n📍 Location: Lat {lat:.2f}, Lon {lon:.2f}")
                message_parts.append(f"⚡ System: {peak_power:.1f} kWp")
                message_parts.append(f"🔧 Tilt: {tilt:.0f}°, Azimuth: {azimuth:.1f}° (SSW)")
                message_parts.append(f"📉 System Losses: 10.52% (realistic)")
                message_parts.append(f"🏠 Mounting: Building-integrated (overlay)")
                message_parts.append(f"\n📊 Database: {data_source}")
                
                if result.get('monthly_production'):
                    annual_production = sum(result['monthly_production'].values())
                    message_parts.append(f"\n🔆 Annual Production: {annual_production:,.0f} kWh")
                    
                    # Show monthly breakdown
                    message_parts.append(f"\n\nMonthly Production (kWh):")
                    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    for i, month_name in enumerate(months, 1):
                        production = result['monthly_production'].get(i, 0)
                        message_parts.append(f"  {month_name}: {production:>7.0f} kWh")
                
                if result.get('weather_data'):
                    weather = result['weather_data']
                    cloud_cover = weather.get('avg_cloud_cover', 0) * 100
                    message_parts.append(f"\n\n☁️ Historical Cloud Cover: {cloud_cover:.1f}%")
                    message_parts.append(f"   (for reference only)")
                
                if 'PVGIS' in data_source:
                    message_parts.append(f"\n\n✨ Using PVGIS satellite irradiance data!")
                    message_parts.append(f"📈 Based on real historical weather & cloud conditions")
                    message_parts.append(f"🎯 Typical accuracy: ±5-8%")
                    message_parts.append(f"\n✅ This data will be used in all energy flow calculations and graphs!")
                elif 'built-in' in data_source.lower():
                    message_parts.append(f"\n\n💡 Using built-in model")
                    message_parts.append(f"📈 Typical accuracy: ±15-25%")
                    message_parts.append(f"\n⚠️ PVGIS API unavailable - check internet connection")
                
                QMessageBox.information(
                    self,
                    "Enhanced Solar Data",
                    "\n".join(message_parts)
                )
                
                # Update status label
                annual_total = sum(result['monthly_production'].values()) if result.get('monthly_production') else 0
                self.solar_data_source.setText(f"📊 Using PVGIS Data: {annual_total:,.0f} kWh/year")
                self.solar_data_source.setStyleSheet("color: green; font-weight: bold; font-size: 9pt; padding: 5px;")
                
                # Store the enhanced data for use in calculations
                if not hasattr(self, 'enhanced_solar_cache'):
                    self.enhanced_solar_cache = {}
                self.enhanced_solar_cache = result
                
                # Load PVGIS data into solar generator for use in calculations
                if SOLAR_V2_AVAILABLE and result.get('monthly_production') and self.solar_generator:
                    self.solar_generator.set_pvgis_data(result['monthly_production'])
                    print("✓ PVGIS data integrated into solar generator")
                
            except ImportError as e:
                QMessageBox.warning(
                    self,
                    "Module Not Found",
                    f"Enhanced solar calculator not available.\n\n"
                    f"Error: {str(e)}\n\n"
                    f"Make sure PV_enhanced_solar.py is in the same directory."
                )
                self.solar_data_source.setText("📊 Using: Built-in solar model")
            
        except Exception as e:
            import traceback
            QMessageBox.critical(
                self,
                "Error",
                f"Error fetching enhanced solar data:\n{str(e)}\n\n{traceback.format_exc()}"
            )
            self.solar_data_source.setText("📊 Using: Built-in solar model (error occurred)")
    
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
        
        # Week selector for weekly analysis
        week_selector_layout = QHBoxLayout()
        week_label = QLabel("Select Week of Year (1-52):")
        week_selector_layout.addWidget(week_label)
        
        self.week_spinbox = QSpinBox()
        self.week_spinbox.setMinimum(1)
        self.week_spinbox.setMaximum(52)
        self.week_spinbox.setValue(1)
        self.week_spinbox.setToolTip("Week 1 = Jan 1-7, Week 26 = Late June, Week 52 = Late December")
        week_selector_layout.addWidget(self.week_spinbox)
        week_selector_layout.addStretch()
        
        button_layout.addLayout(week_selector_layout)
        
        graphs = [
            ("Weekly Energy Balance", "⭐ NEW! Hourly analysis for selected week showing day-wise patterns", self.show_weekly_graph),
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
    
    def setup_consumption_v2_tab(self):
        """Setup the consumption pattern generation tab (Version 2)"""
        layout = QVBoxLayout(self.tab_consumption_v2)
        
        if not CONSUMPTION_V2_AVAILABLE:
            warning_label = QLabel("⚠️ Consumption Pattern Generator V2 not available.\n\n"
                                  "The module files may be missing or there was an import error.\n"
                                  "Please ensure PV_consumption_generator.py and PV_consumption_graphs.py are in the same directory.")
            warning_label.setFont(QFont("Arial", 12))
            warning_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(warning_label)
            return
        
        # Header
        header_label = QLabel("⭐ Consumption Pattern Generator - Version 2")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setStyleSheet("color: darkblue; padding: 10px;")
        layout.addWidget(header_label)
        
        # Info text
        info_text = QLabel(
            "Generate and visualize realistic daily power consumption patterns with:\n"
            "• Gaussian monthly distribution (higher consumption in winter)\n"
            "• Weekday patterns with baseline during day and evening peaks\n"
            "• Weekend vs weekday differences\n"
            "• Multiple household types (working family, retired, home office, etc.)"
        )
        info_text.setWordWrap(True)
        info_text.setFont(QFont("Arial", 10))
        info_text.setStyleSheet("background-color: #e8f4f8; padding: 10px; border-radius: 5px;")
        layout.addWidget(info_text)
        
        # Scroll area for controls
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        scroll.setWidget(container)
        
        # Pattern Selection Group
        pattern_group = QGroupBox("Select Consumption Pattern")
        pattern_layout = QVBoxLayout()
        pattern_group.setLayout(pattern_layout)
        
        from PyQt5.QtWidgets import QComboBox, QTextBrowser
        
        self.pattern_combo = QComboBox()
        if self.consumption_generator:
            patterns = self.consumption_generator.get_available_patterns()
            for pattern in patterns:
                info = self.consumption_generator.get_pattern_info(pattern)
                self.pattern_combo.addItem(info['name'], pattern)
        
        pattern_layout.addWidget(QLabel("Pattern Type:"))
        pattern_layout.addWidget(self.pattern_combo)
        
        # Pattern description
        self.pattern_description = QTextBrowser()
        self.pattern_description.setMaximumHeight(80)
        self.pattern_description.setStyleSheet("background-color: #fffacd; padding: 5px;")
        pattern_layout.addWidget(QLabel("Description:"))
        pattern_layout.addWidget(self.pattern_description)
        
        # Update description when pattern changes
        self.pattern_combo.currentIndexChanged.connect(self.update_pattern_description)
        self.update_pattern_description()
        
        container_layout.addWidget(pattern_group)
        
        # Parameters Group
        params_group = QGroupBox("Pattern Parameters")
        params_layout = QFormLayout()
        params_group.setLayout(params_layout)
        
        self.v2_annual_consumption = QLineEdit("6000")
        params_layout.addRow("Annual Consumption (kWh):", self.v2_annual_consumption)
        
        from PyQt5.QtWidgets import QSlider
        
        # Seasonal strength slider
        seasonal_layout = QHBoxLayout()
        self.v2_seasonal_strength = QSlider(Qt.Horizontal)
        self.v2_seasonal_strength.setMinimum(0)
        self.v2_seasonal_strength.setMaximum(50)  # Max 0.5 instead of 1.0
        self.v2_seasonal_strength.setValue(20)  # Default 0.2 (realistic)
        self.v2_seasonal_strength.setTickPosition(QSlider.TicksBelow)
        self.v2_seasonal_strength.setTickInterval(5)
        seasonal_layout.addWidget(self.v2_seasonal_strength)
        
        self.v2_seasonal_label = QLabel("0.2")
        self.v2_seasonal_label.setMinimumWidth(50)
        seasonal_layout.addWidget(self.v2_seasonal_label)
        
        self.v2_seasonal_strength.valueChanged.connect(
            lambda v: self.v2_seasonal_label.setText(f"{v/100:.2f}")
        )
        
        # Add helpful hint
        seasonal_hint = QLabel("(0.1=minimal, 0.2=typical, 0.3=high heating)")
        seasonal_hint.setStyleSheet("color: gray; font-style: italic; font-size: 8pt;")
        seasonal_layout.addWidget(seasonal_hint)
        
        params_layout.addRow("Seasonal Variation:", seasonal_layout)
        
        # Peak hour selector
        self.v2_peak_hour = QSpinBox()
        self.v2_peak_hour.setMinimum(0)
        self.v2_peak_hour.setMaximum(23)
        self.v2_peak_hour.setValue(19)
        params_layout.addRow("Evening Peak Hour (0-23):", self.v2_peak_hour)
        
        # Month selector for heatmap
        self.v2_heatmap_month = QComboBox()
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        for i, month in enumerate(months, 1):
            self.v2_heatmap_month.addItem(month, i)
        params_layout.addRow("Month for Heatmap:", self.v2_heatmap_month)
        
        container_layout.addWidget(params_group)
        
        # Graph Selection Group
        graphs_group = QGroupBox("Available Visualizations")
        graphs_layout = QVBoxLayout()
        graphs_group.setLayout(graphs_layout)
        
        graphs = [
            ("Daily Pattern Comparison", "Compare weekday vs weekend patterns for winter and summer", 
             self.show_v2_daily_comparison),
            ("Seasonal Variation", "View Gaussian seasonal curve and monthly consumption", 
             self.show_v2_seasonal),
            ("Weekly Heatmap", "24h x 7 days heatmap of consumption patterns", 
             self.show_v2_heatmap),
            ("Pattern Type Comparison", "Compare different household pattern types", 
             self.show_v2_pattern_comparison),
            ("Annual Overview", "Comprehensive annual consumption analysis", 
             self.show_v2_annual_overview),
            ("Generate All V2 Graphs", "Create and save all consumption pattern graphs", 
             self.generate_all_v2_graphs)
        ]
        
        for name, description, command in graphs:
            row_layout = QHBoxLayout()
            
            btn = QPushButton(name)
            btn.setMinimumWidth(200)
            btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
            btn.clicked.connect(command)
            row_layout.addWidget(btn)
            
            desc_label = QLabel(description)
            desc_label.setFont(QFont("Arial", 9))
            desc_label.setStyleSheet("font-style: italic;")
            row_layout.addWidget(desc_label)
            row_layout.addStretch()
            
            graphs_layout.addLayout(row_layout)
        
        container_layout.addWidget(graphs_group)
        container_layout.addStretch()
        
        layout.addWidget(scroll)
        
        # Status label
        self.v2_status = QLabel("")
        self.v2_status.setFont(QFont("Arial", 9))
        self.v2_status.setStyleSheet("font-style: italic; color: darkgreen;")
        layout.addWidget(self.v2_status)
    
    def update_pattern_description(self):
        """Update the pattern description when selection changes"""
        if not self.consumption_generator:
            return
        
        pattern_type = self.pattern_combo.currentData()
        info = self.consumption_generator.get_pattern_info(pattern_type)
        
        if info:
            self.pattern_description.setHtml(
                f"<b>{info['name']}</b><br>"
                f"{info['description']}"
            )
    
    def get_v2_profile(self) -> HouseholdProfile:
        """Create household profile from V2 inputs"""
        if not self.consumption_generator:
            return None
        
        try:
            pattern_type = self.pattern_combo.currentData()
            annual_consumption = float(self.v2_annual_consumption.text())
            seasonal_strength = self.v2_seasonal_strength.value() / 100.0
            peak_hour = self.v2_peak_hour.value()
            
            profile = self.consumption_generator.create_household_profile(
                name=self.pattern_combo.currentText(),
                annual_consumption_kwh=annual_consumption,
                pattern_type=pattern_type,
                seasonal_strength=seasonal_strength,
                peak_hour=peak_hour
            )
            
            # Add EV profile if available and enabled (from input parameters tab)
            if hasattr(self, 'current_ev_consumption_profile') and self.current_ev_consumption_profile:
                profile.ev_profile = self.current_ev_consumption_profile
            
            return profile
        except ValueError as e:
            QMessageBox.critical(self, "Input Error", 
                               f"Invalid input value: {str(e)}")
            return None
    
    def show_v2_daily_comparison(self):
        """Show daily pattern comparison graph"""
        if not CONSUMPTION_V2_AVAILABLE:
            return
        
        profile = self.get_v2_profile()
        if not profile:
            return
        
        self.v2_status.setText("Generating daily pattern comparison...")
        QApplication.processEvents()
        
        try:
            graph_gen = ConsumptionGraphGenerator(self.consumption_generator)
            graph_gen.plot_daily_pattern_comparison(profile, show=True)
            self.v2_status.setText("✓ Daily pattern comparison graph displayed")
        except Exception as e:
            QMessageBox.critical(self, "Graph Error", f"Error generating graph: {str(e)}")
            self.v2_status.setText("✗ Error generating graph")
    
    def show_v2_seasonal(self):
        """Show seasonal variation graph"""
        if not CONSUMPTION_V2_AVAILABLE:
            return
        
        profile = self.get_v2_profile()
        if not profile:
            return
        
        self.v2_status.setText("Generating seasonal variation graph...")
        QApplication.processEvents()
        
        try:
            graph_gen = ConsumptionGraphGenerator(self.consumption_generator)
            graph_gen.plot_seasonal_variation(profile, show=True)
            self.v2_status.setText("✓ Seasonal variation graph displayed")
        except Exception as e:
            QMessageBox.critical(self, "Graph Error", f"Error generating graph: {str(e)}")
            self.v2_status.setText("✗ Error generating graph")
    
    def show_v2_heatmap(self):
        """Show weekly heatmap graph"""
        if not CONSUMPTION_V2_AVAILABLE:
            return
        
        profile = self.get_v2_profile()
        if not profile:
            return
        
        month = self.v2_heatmap_month.currentData()
        
        self.v2_status.setText(f"Generating weekly heatmap for {self.v2_heatmap_month.currentText()}...")
        QApplication.processEvents()
        
        try:
            graph_gen = ConsumptionGraphGenerator(self.consumption_generator)
            graph_gen.plot_weekly_heatmap(profile, month=month, show=True)
            self.v2_status.setText("✓ Weekly heatmap displayed")
        except Exception as e:
            QMessageBox.critical(self, "Graph Error", f"Error generating graph: {str(e)}")
            self.v2_status.setText("✗ Error generating graph")
    
    def show_v2_pattern_comparison(self):
        """Show pattern comparison graph"""
        if not CONSUMPTION_V2_AVAILABLE:
            return
        
        try:
            annual_consumption = float(self.v2_annual_consumption.text())
        except ValueError:
            QMessageBox.critical(self, "Input Error", "Invalid annual consumption value")
            return
        
        self.v2_status.setText("Generating pattern comparison...")
        QApplication.processEvents()
        
        try:
            graph_gen = ConsumptionGraphGenerator(self.consumption_generator)
            patterns = ['working_family', 'home_office', 'retired', 'student']
            graph_gen.plot_pattern_comparison(patterns, annual_consumption=annual_consumption, show=True)
            self.v2_status.setText("✓ Pattern comparison displayed")
        except Exception as e:
            QMessageBox.critical(self, "Graph Error", f"Error generating graph: {str(e)}")
            self.v2_status.setText("✗ Error generating graph")
    
    def show_v2_annual_overview(self):
        """Show annual overview graph"""
        if not CONSUMPTION_V2_AVAILABLE:
            return
        
        profile = self.get_v2_profile()
        if not profile:
            return
        
        self.v2_status.setText("Generating annual overview (this may take a moment)...")
        QApplication.processEvents()
        
        try:
            graph_gen = ConsumptionGraphGenerator(self.consumption_generator)
            graph_gen.plot_annual_overview(profile, show=True)
            self.v2_status.setText("✓ Annual overview displayed")
        except Exception as e:
            QMessageBox.critical(self, "Graph Error", f"Error generating graph: {str(e)}")
            self.v2_status.setText("✗ Error generating graph")
    
    def generate_all_v2_graphs(self):
        """Generate and save all V2 consumption pattern graphs"""
        if not CONSUMPTION_V2_AVAILABLE:
            return
        
        profile = self.get_v2_profile()
        if not profile:
            return
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        self.v2_status.setText("Generating all V2 graphs (this will take a moment)...")
        QApplication.processEvents()
        
        try:
            graph_gen = ConsumptionGraphGenerator(self.consumption_generator)
            month = self.v2_heatmap_month.currentData()
            annual_consumption = float(self.v2_annual_consumption.text())
            
            # Generate all graphs with save paths
            graph_gen.plot_daily_pattern_comparison(
                profile, 
                save_path=f"Consumption_V2_daily_comparison_{timestamp}.png",
                show=False
            )
            
            graph_gen.plot_seasonal_variation(
                profile,
                save_path=f"Consumption_V2_seasonal_{timestamp}.png",
                show=False
            )
            
            graph_gen.plot_weekly_heatmap(
                profile,
                month=month,
                save_path=f"Consumption_V2_heatmap_{timestamp}.png",
                show=False
            )
            
            patterns = ['working_family', 'home_office', 'retired', 'student']
            graph_gen.plot_pattern_comparison(
                patterns,
                annual_consumption=annual_consumption,
                save_path=f"Consumption_V2_pattern_comparison_{timestamp}.png",
                show=False
            )
            
            graph_gen.plot_annual_overview(
                profile,
                save_path=f"Consumption_V2_annual_overview_{timestamp}.png",
                show=True  # Show the last one
            )
            
            self.v2_status.setText(f"✓ All V2 graphs generated and saved with timestamp {timestamp}")
            QMessageBox.information(self, "Success", 
                                  f"All consumption pattern graphs have been generated and saved!\n\n"
                                  f"Files saved with timestamp: {timestamp}")
        
        except Exception as e:
            QMessageBox.critical(self, "Graph Error", f"Error generating graphs: {str(e)}")
            self.v2_status.setText("✗ Error generating graphs")
    
    def setup_solar_v2_tab(self):
        """Setup the solar generation tab (Version 2)"""
        layout = QVBoxLayout(self.tab_solar_v2)
        
        if not SOLAR_V2_AVAILABLE:
            warning_label = QLabel("⚠️ Solar Generation Calculator V2 not available.\n\n"
                                  "The module files may be missing or there was an import error.\n"
                                  "Please ensure PV_solar_generator.py and PV_solar_graphs.py are in the same directory.")
            warning_label.setFont(QFont("Arial", 12))
            warning_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(warning_label)
            return
        
        # Header
        header_label = QLabel("⭐ Solar Generation Calculator - Version 2")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setStyleSheet("color: darkorange; padding: 10px;")
        layout.addWidget(header_label)
        
        # Info text
        info_text = QLabel(
            "Generate and visualize solar PV generation patterns with:\n"
            "• Location-based irradiance (10 European cities)\n"
            "• Realistic hourly generation curves\n"
            "• Comparison with consumption patterns\n"
            "• Excess/deficit calculation for battery sizing"
        )
        info_text.setWordWrap(True)
        info_text.setFont(QFont("Arial", 10))
        info_text.setStyleSheet("background-color: #fff8dc; padding: 10px; border-radius: 5px;")
        layout.addWidget(info_text)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        scroll.setWidget(container)
        
        # Solar System Parameters
        from PyQt5.QtWidgets import QComboBox, QDoubleSpinBox
        
        solar_group = QGroupBox("Solar System Configuration")
        solar_layout = QFormLayout()
        solar_group.setLayout(solar_layout)
        
        # System size
        self.solar_system_size = QDoubleSpinBox()
        self.solar_system_size.setMinimum(1.0)
        self.solar_system_size.setMaximum(100.0)
        self.solar_system_size.setValue(5.0)
        self.solar_system_size.setSuffix(" kWp")
        self.solar_system_size.setDecimals(1)
        solar_layout.addRow("System Size:", self.solar_system_size)
        
        # Location selector
        self.solar_location = QComboBox()
        for key, loc in LOCATIONS.items():
            self.solar_location.addItem(f"{loc.name} ({loc.avg_daily_irradiance} kWh/m²/day)", key)
        solar_layout.addRow("Location:", self.solar_location)
        
        # Tilt angle
        self.solar_tilt = QDoubleSpinBox()
        self.solar_tilt.setMinimum(0)
        self.solar_tilt.setMaximum(90)
        self.solar_tilt.setValue(35)
        self.solar_tilt.setSuffix("°")
        solar_layout.addRow("Panel Tilt Angle:", self.solar_tilt)
        
        # System efficiency
        self.solar_efficiency = QDoubleSpinBox()
        self.solar_efficiency.setMinimum(0.5)
        self.solar_efficiency.setMaximum(1.0)
        self.solar_efficiency.setValue(0.85)
        self.solar_efficiency.setSingleStep(0.01)
        solar_layout.addRow("System Efficiency:", self.solar_efficiency)
        
        container_layout.addWidget(solar_group)
        
        # Comparison with Consumption
        comparison_group = QGroupBox("Compare with Consumption (Optional)")
        comparison_layout = QFormLayout()
        comparison_group.setLayout(comparison_layout)
        
        self.solar_compare_enabled = QCheckBox("Enable comparison with consumption patterns")
        self.solar_compare_enabled.setChecked(True)
        comparison_layout.addRow(self.solar_compare_enabled)
        
        # Link to consumption tab
        comparison_hint = QLabel("Uses settings from 'Consumption Patterns V2' tab")
        comparison_hint.setStyleSheet("color: gray; font-style: italic; font-size: 9pt;")
        comparison_layout.addRow(comparison_hint)
        
        container_layout.addWidget(comparison_group)
        
        # Available Graphs
        graphs_group = QGroupBox("Available Visualizations")
        graphs_layout = QVBoxLayout()
        graphs_group.setLayout(graphs_layout)
        
        graphs = [
            ("Daily Generation Profile", "Hourly generation curve for selected month", 
             self.show_solar_daily),
            ("Monthly Generation Profile", "Annual generation with seasonal variations", 
             self.show_solar_monthly),
            ("Generation vs Consumption", "Compare solar generation with household consumption", 
             self.show_solar_comparison),
            ("Excess/Deficit Analysis", "Calculate surplus for battery/grid export", 
             self.show_solar_excess)
        ]
        
        for name, description, command in graphs:
            row_layout = QHBoxLayout()
            
            btn = QPushButton(name)
            btn.setMinimumWidth(220)
            btn.setStyleSheet("background-color: #FF8C00; color: white; font-weight: bold; padding: 8px;")
            btn.clicked.connect(command)
            row_layout.addWidget(btn)
            
            desc_label = QLabel(description)
            desc_label.setFont(QFont("Arial", 9))
            desc_label.setStyleSheet("font-style: italic;")
            row_layout.addWidget(desc_label)
            row_layout.addStretch()
            
            graphs_layout.addLayout(row_layout)
        
        container_layout.addWidget(graphs_group)
        container_layout.addStretch()
        
        layout.addWidget(scroll)
        
        # Status label
        self.solar_status = QLabel("")
        self.solar_status.setFont(QFont("Arial", 9))
        self.solar_status.setStyleSheet("font-style: italic; color: darkorange;")
        layout.addWidget(self.solar_status)
    
    def get_solar_system(self) -> 'SolarSystemProfile':
        """Create solar system profile from inputs"""
        if not self.solar_generator:
            return None
        
        try:
            location_key = self.solar_location.currentData()
            location = LOCATIONS[location_key]
            
            system = SolarSystemProfile(
                name=f"{self.solar_system_size.value()}kW System",
                peak_power_kw=self.solar_system_size.value(),
                location=location,
                system_efficiency=self.solar_efficiency.value(),
                tilt_angle=self.solar_tilt.value()
            )
            
            return system
        except Exception as e:
            QMessageBox.critical(self, "Input Error", f"Error creating solar system: {str(e)}")
            return None
    
    def show_solar_daily(self):
        """Show daily generation profile"""
        system = self.get_solar_system()
        if not system:
            return
        
        self.solar_status.setText("Generating daily solar profile...")
        QApplication.processEvents()
        
        try:
            from PV_solar_graphs import SolarComparisonGraphs
            
            graph_gen = SolarComparisonGraphs(self.solar_generator, self.consumption_generator)
            
            # For now, just show monthly profile which includes daily curves
            graph_gen.plot_monthly_generation_profile(system, show=True)
            
            self.solar_status.setText("✓ Daily solar profile displayed")
        except Exception as e:
            QMessageBox.critical(self, "Graph Error", f"Error generating graph: {str(e)}")
            self.solar_status.setText("✗ Error generating graph")
    
    def show_solar_monthly(self):
        """Show monthly generation profile"""
        system = self.get_solar_system()
        if not system:
            return
        
        self.solar_status.setText("Generating monthly solar profile...")
        QApplication.processEvents()
        
        try:
            from PV_solar_graphs import SolarComparisonGraphs
            
            graph_gen = SolarComparisonGraphs(self.solar_generator, self.consumption_generator)
            graph_gen.plot_monthly_generation_profile(system, show=True)
            
            self.solar_status.setText("✓ Monthly solar profile displayed")
        except Exception as e:
            QMessageBox.critical(self, "Graph Error", f"Error generating graph: {str(e)}")
            self.solar_status.setText("✗ Error generating graph")
    
    def show_solar_comparison(self):
        """Show generation vs consumption comparison"""
        if not self.solar_compare_enabled.isChecked():
            QMessageBox.information(self, "Info", "Please enable 'Compare with consumption' option")
            return
        
        system = self.get_solar_system()
        household = self.get_v2_profile()
        
        if not system or not household:
            return
        
        self.solar_status.setText("Generating comparison...")
        QApplication.processEvents()
        
        try:
            from PV_solar_graphs import SolarComparisonGraphs
            
            graph_gen = SolarComparisonGraphs(self.solar_generator, self.consumption_generator)
            graph_gen.plot_annual_comparison(system, household, show=True)
            
            self.solar_status.setText("✓ Comparison displayed")
        except Exception as e:
            QMessageBox.critical(self, "Graph Error", f"Error generating graph: {str(e)}")
            self.solar_status.setText("✗ Error generating graph")
    
    def show_solar_excess(self):
        """Show excess/deficit analysis"""
        if not self.solar_compare_enabled.isChecked():
            QMessageBox.information(self, "Info", "Please enable 'Compare with consumption' option")
            return
        
        system = self.get_solar_system()
        household = self.get_v2_profile()
        
        if not system or not household:
            return
        
        self.solar_status.setText("Generating excess/deficit analysis...")
        QApplication.processEvents()
        
        try:
            from PV_solar_graphs import SolarComparisonGraphs
            
            graph_gen = SolarComparisonGraphs(self.solar_generator, self.consumption_generator)
            # Show daily comparison which includes excess/deficit
            graph_gen.plot_daily_comparison(system, household, 6, 0, show=True)
            
            self.solar_status.setText("✓ Excess/deficit analysis displayed")
        except Exception as e:
            QMessageBox.critical(self, "Graph Error", f"Error generating graph: {str(e)}")
            self.solar_status.setText("✗ Error generating graph")
    
    def setup_unified_v2_tab(self):
        """Setup the unified energy flow tab (Version 2)"""
        layout = QVBoxLayout(self.tab_unified_v2)
        
        if not INTEGRATED_V2_AVAILABLE:
            warning_label = QLabel("⚠️ Integrated Energy Flow Analysis V2 not available.\n\n"
                                  "The module files may be missing or there was an import error.\n"
                                  "Please ensure PV_battery_flow.py and PV_integrated_graphs.py are in the same directory.")
            warning_label.setFont(QFont("Arial", 12))
            warning_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(warning_label)
            return
        
        # Header
        header_label = QLabel("🔋 Unified Energy Flow Analysis - Version 2")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setStyleSheet("color: darkgreen; padding: 10px;")
        layout.addWidget(header_label)
        
        # Info text
        info_text = QLabel(
            "Complete energy system simulation combining:\n"
            "• Consumption patterns from your household profile\n"
            "• Solar generation from your PV system\n"
            "• Battery charging/discharging\n"
            "• Grid import/export flows\n"
            "• Self-sufficiency and energy balance analysis\n\n"
            "📋 Configuration is pulled from the 'Input Parameters' tab (Tab 1)"
        )
        info_text.setWordWrap(True)
        info_text.setFont(QFont("Arial", 10))
        info_text.setStyleSheet("background-color: #e8f5e9; padding: 10px; border-radius: 5px;")
        layout.addWidget(info_text)
        
        # Current Configuration Display (Read-only summary)
        config_group = QGroupBox("Current System Configuration (from Input Parameters)")
        config_layout = QVBoxLayout()
        config_group.setLayout(config_layout)
        
        self.unified_config_display = QLabel()
        self.unified_config_display.setWordWrap(True)
        self.unified_config_display.setStyleSheet(
            "background-color: white; padding: 10px; border: 1px solid #ccc; "
            "border-radius: 5px; font-family: monospace; font-size: 9pt;"
        )
        config_layout.addWidget(self.unified_config_display)
        
        refresh_btn = QPushButton("🔄 Refresh Configuration")
        refresh_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 5px;")
        refresh_btn.clicked.connect(self.update_unified_config_display)
        config_layout.addWidget(refresh_btn)
        
        layout.addWidget(config_group)
        
        # Date Selection
        from PyQt5.QtWidgets import QDateEdit
        from datetime import date
        
        date_group = QGroupBox("Select Date for Analysis")
        date_layout = QHBoxLayout()
        date_group.setLayout(date_layout)
        
        date_layout.addWidget(QLabel("Select Date:"))
        self.unified_date_picker = QDateEdit()
        self.unified_date_picker.setCalendarPopup(True)
        self.unified_date_picker.setDate(date(2024, 6, 15))  # Default to mid-June
        self.unified_date_picker.setDisplayFormat("yyyy-MM-dd (dddd)")
        self.unified_date_picker.setMinimumDate(date(2024, 1, 1))
        self.unified_date_picker.setMaximumDate(date(2030, 12, 31))  # Allow future dates
        date_layout.addWidget(self.unified_date_picker)
        
        date_hint = QLabel("(Select any date to see energy flow for that specific day)")
        date_hint.setStyleSheet("color: gray; font-style: italic; font-size: 9pt;")
        date_layout.addWidget(date_hint)
        date_layout.addStretch()
        
        layout.addWidget(date_group)
        
        # Single Graph Button
        graphs_group = QGroupBox("Energy Flow Visualization")
        graphs_layout = QVBoxLayout()
        graphs_group.setLayout(graphs_layout)
        
        row_layout = QHBoxLayout()
        
        btn = QPushButton("Generate Daily Energy Flow")
        btn.setMinimumHeight(40)
        btn.setMinimumWidth(250)
        btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; font-size: 12pt;")
        btn.clicked.connect(self.show_unified_daily_flow)
        row_layout.addWidget(btn)
        
        desc_label = QLabel("Complete 24-hour energy flow analysis with:\n"
                           "• Consumption and generation patterns\n"
                           "• Battery charging/discharging\n"
                           "• Grid import/export\n"
                           "• Self-sufficiency metrics")
        desc_label.setFont(QFont("Arial", 9))
        desc_label.setStyleSheet("font-style: italic;")
        row_layout.addWidget(desc_label)
        row_layout.addStretch()
        
        graphs_layout.addLayout(row_layout)
        
        # Annual Analysis Button
        row_layout2 = QHBoxLayout()
        
        btn2 = QPushButton("Generate Annual Analysis")
        btn2.setMinimumHeight(40)
        btn2.setMinimumWidth(250)
        btn2.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 10px; font-size: 12pt;")
        btn2.clicked.connect(self.show_annual_analysis)
        row_layout2.addWidget(btn2)
        
        desc_label2 = QLabel("Full year simulation with:\n"
                            "• Monthly import/export balance\n"
                            "• Annual energy totals\n"
                            "• Self-sufficiency by month\n"
                            "• Cost and savings analysis")
        desc_label2.setFont(QFont("Arial", 9))
        desc_label2.setStyleSheet("font-style: italic;")
        row_layout2.addWidget(desc_label2)
        row_layout2.addStretch()
        
        graphs_layout.addLayout(row_layout2)
        
        # Scenario Comparison Button
        row_layout3 = QHBoxLayout()
        
        btn3 = QPushButton("Compare Scenarios (No PV vs PV vs PV+Battery)")
        btn3.setMinimumHeight(40)
        btn3.setMinimumWidth(250)
        btn3.setStyleSheet("background-color: #9C27B0; color: white; font-weight: bold; padding: 10px; font-size: 12pt;")
        btn3.clicked.connect(self.show_scenario_comparison)
        row_layout3.addWidget(btn3)
        
        desc_label3 = QLabel("Compare three scenarios:\n"
                            "• No PV, No Battery (baseline)\n"
                            "• PV Only (no storage)\n"
                            "• PV + Battery (full system)\n"
                            "• ROI and payback analysis")
        desc_label3.setFont(QFont("Arial", 9))
        desc_label3.setStyleSheet("font-style: italic;")
        row_layout3.addWidget(desc_label3)
        row_layout3.addStretch()
        
        graphs_layout.addLayout(row_layout3)
        
        layout.addWidget(graphs_group)
        
        # Status label
        self.unified_status = QLabel("")
        self.unified_status.setFont(QFont("Arial", 9))
        self.unified_status.setStyleSheet("font-style: italic; color: darkgreen;")
        layout.addWidget(self.unified_status)
        
        layout.addStretch()
        
        # Initial config display
        self.update_unified_config_display()
    
    def update_unified_config_display(self):
        """Update the configuration display with current values from Tab 1"""
        # Clear battery SOC cache when configuration changes
        self.battery_soc_cache.clear()
        
        try:
            # Get values from Tab 1
            monthly_consumption = float(self.monthly_consumption.text())
            annual_consumption = monthly_consumption * 12
            pattern_type = self.consumption_pattern_type.currentData() if hasattr(self, 'consumption_pattern_type') else 'working_family'
            seasonal_strength = self.consumption_seasonal.value() / 100.0 if hasattr(self, 'consumption_seasonal') else 0.2
            
            pv_size = float(self.pv_size.text()) if self.pv_enabled.isChecked() else 0.0
            location_key = self.pv_location.currentData() if hasattr(self, 'pv_location') else 'riga_latvia'
            location_name = LOCATIONS[location_key].name if SOLAR_V2_AVAILABLE and location_key in LOCATIONS else "Unknown"
            tilt = self.pv_tilt.value() if hasattr(self, 'pv_tilt') else 35.0
            
            battery_capacity = float(self.battery_capacity.text()) if self.battery_enabled.isChecked() else 0.0
            
            # Format display
            config_text = f"""CONSUMPTION:
  Annual:           {annual_consumption:.0f} kWh  ({monthly_consumption:.0f} kWh/month)
  Pattern Type:     {pattern_type.replace('_', ' ').title()}
  Seasonal Var:     {seasonal_strength:.2f}

SOLAR SYSTEM:
  Size:             {pv_size:.1f} kWp
  Location:         {location_name}
  Panel Tilt:       {tilt:.0f}°
  Status:           {'Enabled' if self.pv_enabled.isChecked() else 'Disabled'}

BATTERY:
  Capacity:         {battery_capacity:.1f} kWh
  Status:           {'Enabled' if self.battery_enabled.isChecked() else 'Disabled'}
  Efficiency:       95% (default)
  Min SOC:          10% (default)

💡 To change these values, go to the 'Input Parameters' tab and click 'Refresh Configuration'
"""
            self.unified_config_display.setText(config_text)
            
        except Exception as e:
            self.unified_config_display.setText(f"Error reading configuration: {str(e)}\n\nPlease check Input Parameters tab.")
    
    def get_unified_config(self):
        """Get unified configuration from Tab 1 inputs"""
        try:
            # Household profile from Tab 1
            monthly_consumption = float(self.monthly_consumption.text())
            annual_consumption = monthly_consumption * 12
            pattern_type = self.consumption_pattern_type.currentData() if hasattr(self, 'consumption_pattern_type') else 'working_family'
            seasonal_strength = self.consumption_seasonal.value() / 100.0 if hasattr(self, 'consumption_seasonal') else 0.2
            
            household = HouseholdProfile(
                name='My Household',
                annual_consumption_kwh=annual_consumption,
                pattern_type=pattern_type,
                seasonal_strength=seasonal_strength,
                peak_evening_hour=19  # Default
            )
            
            # Create EV profile directly from input fields if enabled
            if self.ev_enabled.isChecked() and CONSUMPTION_V2_AVAILABLE:
                try:
                    # Get consumption
                    consumption_text = self.ev_consumption_display.text()
                    efficiency = float(consumption_text) if consumption_text and consumption_text != "--" else 18.0
                    
                    # Get other parameters
                    weekly_km = float(self.ev_weekly_km.text())
                    charger_power = float(self.ev_charger_power.text())
                    start_hour = self.ev_charging_start.value()
                    
                    # Calculate daily consumption and duration
                    daily_km = weekly_km / 7.0
                    daily_kwh = daily_km * efficiency / 100.0
                    duration_hours = daily_kwh / charger_power
                    
                    # Generate charging hours list
                    charging_hours = []
                    current_hour = start_hour
                    hours_to_add = int(duration_hours) + 1
                    for _ in range(hours_to_add):
                        charging_hours.append(current_hour % 24)
                        current_hour += 1
                    
                    # Create EV profile
                    household.ev_profile = EVConsumptionProfile(
                        enabled=True,
                        weekly_distance_km=weekly_km,
                        consumption_per_100km=efficiency,
                        charging_days=[True] * 7,
                        charging_hours=charging_hours
                    )
                except (ValueError, AttributeError):
                    pass  # If EV inputs are invalid, just skip EV
            
            # Solar system from Tab 1
            if not self.pv_enabled.isChecked():
                QMessageBox.warning(self, "PV System Disabled", 
                                  "Please enable PV System in the Input Parameters tab to use this feature.")
                return None, None, None
            
            pv_size = float(self.pv_size.text())
            location_key = self.pv_location.currentData() if hasattr(self, 'pv_location') else 'riga_latvia'
            
            if not SOLAR_V2_AVAILABLE or location_key not in LOCATIONS:
                QMessageBox.warning(self, "Location Error", 
                                  "Solar V2 location data not available. Using default Riga location.")
                location_key = 'riga_latvia'
            
            location = LOCATIONS[location_key]
            tilt = self.pv_tilt.value() if hasattr(self, 'pv_tilt') else 35.0
            
            solar_system = SolarSystemProfile(
                name='My Solar System',
                peak_power_kw=pv_size,
                location=location,
                tilt_angle=tilt,
                system_efficiency=0.85  # Default
            )
            
            # Battery from Tab 1
            if not self.battery_enabled.isChecked():
                QMessageBox.warning(self, "Battery Disabled", 
                                  "Please enable Battery Storage in the Input Parameters tab to use this feature.")
                return None, None, None
            
            battery_capacity = float(self.battery_capacity.text())
            
            battery_calc = BatteryFlowCalculator(
                battery_capacity_kwh=battery_capacity,
                battery_efficiency=0.95,  # Default
                min_soc_percent=10.0  # Default
            )
            
            return household, solar_system, battery_calc
            
        except ValueError as e:
            QMessageBox.critical(self, "Input Error", 
                               f"Invalid input values in Input Parameters tab:\n{str(e)}\n\n"
                               "Please check all numeric fields.")
            return None, None, None
        except Exception as e:
            QMessageBox.critical(self, "Configuration Error", 
                               f"Error reading configuration from Input Parameters tab:\n{str(e)}")
            return None, None, None
    
    def show_unified_daily_flow(self):
        """Show complete daily energy flow for selected date with SOC continuity"""
        household, solar_system, battery_calc = self.get_unified_config()
        if not household or not solar_system or not battery_calc:
            return
        
        # Get selected date
        selected_date = self.unified_date_picker.date().toPyDate()
        year = selected_date.year
        day_of_year = selected_date.timetuple().tm_yday
        month = selected_date.month
        day_of_week = selected_date.weekday()  # Monday=0, Sunday=6
        
        self.unified_status.setText(f"Calculating battery state for {selected_date.strftime('%Y-%m-%d (%A)')}...")
        QApplication.processEvents()
        
        try:
            # Get initial SOC for this day (from previous day or default)
            initial_soc = self.get_battery_soc_for_date(
                year, day_of_year, household, solar_system, battery_calc
            )
            
            # Get pricing parameters
            selling_price = float(self.nordpool_price.text()) if hasattr(self, 'nordpool_price') else 0.06  # EUR/kWh
            transfer_cost = float(self.transfer_cost.text()) if hasattr(self, 'transfer_cost') else 0.04  # EUR/kWh
            electricity_cost = float(self.electricity_cost.text()) if hasattr(self, 'electricity_cost') else 0.08  # EUR/kWh
            service_cost = float(self.service_cost.text()) if hasattr(self, 'service_cost') else 0.01  # EUR/kWh
            vat_rate = float(self.vat_rate.text()) / 100.0 if hasattr(self, 'vat_rate') else 0.21
            
            # Calculate effective rates
            import_rate = (electricity_cost + transfer_cost + service_cost) * (1 + vat_rate)  # Total cost per kWh imported
            export_rate = selling_price - transfer_cost * (1 + vat_rate)  # Net revenue per kWh exported
            export_rate = max(0, export_rate)  # Can't be negative
            
            # Generate the daily flow with correct initial SOC
            graph_gen = IntegratedEnergyGraphs(
                self.consumption_generator, self.solar_generator, battery_calc,
                household, solar_system
            )
            
            # Show selected date with initial SOC and pricing
            fig = graph_gen.plot_daily_energy_flow(
                month=month, day_of_week=day_of_week, initial_soc=initial_soc,
                import_rate=import_rate, export_rate=export_rate
            )
            fig.show()
            
            self.unified_status.setText(f"✓ Energy flow displayed for {selected_date.strftime('%Y-%m-%d (%A)')}")
        except Exception as e:
            QMessageBox.critical(self, "Graph Error", f"Error generating graph: {str(e)}")
            self.unified_status.setText("✗ Error generating graph")
    
    def show_annual_analysis(self):
        """Generate annual energy analysis with monthly and yearly totals"""
        household, solar_system, battery_calc = self.get_unified_config()
        if not household or not solar_system or not battery_calc:
            return
        
        self.unified_status.setText("Simulating full year (365 days)... This may take a moment...")
        QApplication.processEvents()
        
        try:
            import matplotlib.pyplot as plt
            from datetime import datetime, timedelta
            
            # Get pricing parameters
            selling_price = float(self.nordpool_price.text()) if hasattr(self, 'nordpool_price') else 0.06  # EUR/kWh
            transfer_cost = float(self.transfer_cost.text()) if hasattr(self, 'transfer_cost') else 0.04  # EUR/kWh
            electricity_cost = float(self.electricity_cost.text()) if hasattr(self, 'electricity_cost') else 0.08  # EUR/kWh
            service_cost = float(self.service_cost.text()) if hasattr(self, 'service_cost') else 0.01  # EUR/kWh
            vat_rate = float(self.vat_rate.text()) / 100.0 if hasattr(self, 'vat_rate') else 0.21
            
            # Calculate effective rates
            import_rate = (electricity_cost + transfer_cost + service_cost) * (1 + vat_rate)  # Total cost per kWh imported
            export_rate = selling_price - transfer_cost * (1 + vat_rate)  # Net revenue per kWh exported
            export_rate = max(0, export_rate)  # Can't be negative
            
            # Simulate entire year
            year = 2024
            monthly_data = {}
            
            for month in range(1, 13):
                monthly_data[month] = {
                    'consumption': 0,
                    'generation': 0,
                    'grid_import': 0,
                    'grid_export': 0,
                    'self_consumption': 0,
                    'money_from_export': 0,
                    'money_for_import': 0,
                    'days': 0
                }
            
            # Start SOC and monetary balance
            current_soc = battery_calc.battery_capacity * 0.5
            money_balance = 0.0  # Cumulative money balance (positive = credit, negative = debt)
            
            # Simulate each day
            for day_of_year in range(1, 366):
                date_obj = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
                month = date_obj.month
                day_of_week = date_obj.weekday()
                
                # Simulate this day
                result = battery_calc.simulate_daily_flow(
                    self.consumption_generator, self.solar_generator,
                    household, solar_system,
                    month, day_of_week, initial_soc=current_soc
                )
                
                # Update SOC for next day
                current_soc = result.hourly_battery_soc[-1]
                
                # Calculate monetary flows
                daily_export_revenue = result.total_grid_export * export_rate
                
                # For imports, use saved balance first
                daily_import_cost = 0.0
                if result.total_grid_import > 0:
                    import_value = result.total_grid_import * import_rate
                    if money_balance >= import_value:
                        # Use saved balance to cover import
                        money_balance -= import_value
                    else:
                        # Use all saved balance and pay the rest
                        daily_import_cost = import_value - money_balance
                        money_balance = 0.0
                
                # Add export revenue to balance
                money_balance += daily_export_revenue
                
                # Accumulate monthly data
                monthly_data[month]['consumption'] += result.total_consumption
                monthly_data[month]['generation'] += result.total_generation
                monthly_data[month]['grid_import'] += result.total_grid_import
                monthly_data[month]['grid_export'] += result.total_grid_export
                monthly_data[month]['self_consumption'] += result.total_self_consumption
                monthly_data[month]['money_from_export'] += daily_export_revenue
                monthly_data[month]['money_for_import'] += daily_import_cost
                monthly_data[month]['days'] += 1
                
                # Update progress every 30 days
                if day_of_year % 30 == 0:
                    self.unified_status.setText(f"Simulating day {day_of_year}/365...")
                    QApplication.processEvents()
            
            # Calculate annual totals
            annual_consumption = sum(m['consumption'] for m in monthly_data.values())
            annual_generation = sum(m['generation'] for m in monthly_data.values())
            annual_import = sum(m['grid_import'] for m in monthly_data.values())
            annual_export = sum(m['grid_export'] for m in monthly_data.values())
            annual_self_consumption = sum(m['self_consumption'] for m in monthly_data.values())
            annual_export_revenue = sum(m['money_from_export'] for m in monthly_data.values())
            annual_import_cost = sum(m['money_for_import'] for m in monthly_data.values())
            
            net_balance = annual_export - annual_import
            net_money_balance = annual_export_revenue - annual_import_cost
            final_credit = money_balance  # Money still in the "bank"
            self_sufficiency = (annual_self_consumption / annual_consumption * 100) if annual_consumption > 0 else 0
            
            # Create visualization
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Annual Energy Analysis', fontsize=16, fontweight='bold')
            
            months = list(range(1, 13))
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            # Plot 1: Monthly consumption vs generation
            ax1 = axes[0, 0]
            consumption_vals = [monthly_data[m]['consumption'] for m in months]
            generation_vals = [monthly_data[m]['generation'] for m in months]
            
            x = range(len(months))
            width = 0.35
            ax1.bar([i - width/2 for i in x], consumption_vals, width, label='Consumption', alpha=0.8, color='steelblue')
            ax1.bar([i + width/2 for i in x], generation_vals, width, label='Generation', alpha=0.8, color='orange')
            ax1.set_xlabel('Month')
            ax1.set_ylabel('Energy (kWh)')
            ax1.set_title('Monthly Consumption vs Generation')
            ax1.set_xticks(x)
            ax1.set_xticklabels(month_names)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Plot 2: Monthly monetary balance
            ax2 = axes[0, 1]
            export_money = [monthly_data[m]['money_from_export'] for m in months]
            import_money = [monthly_data[m]['money_for_import'] for m in months]
            money_balance_vals = [export_money[i] - import_money[i] for i in range(len(months))]
            
            colors = ['green' if b >= 0 else 'red' for b in money_balance_vals]
            ax2.bar(x, money_balance_vals, color=colors, alpha=0.7)
            ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            ax2.set_xlabel('Month')
            ax2.set_ylabel('Monetary Balance (EUR)')
            ax2.set_title('Monthly Monetary Balance (Revenue - Cost)')
            ax2.set_xticks(x)
            ax2.set_xticklabels(month_names)
            ax2.grid(True, alpha=0.3)
            
            # Plot 3: Monthly self-sufficiency
            ax3 = axes[1, 0]
            self_suff_vals = [(monthly_data[m]['self_consumption'] / monthly_data[m]['consumption'] * 100) 
                             if monthly_data[m]['consumption'] > 0 else 0 
                             for m in months]
            ax3.plot(x, self_suff_vals, marker='o', linewidth=2, markersize=8, color='green')
            ax3.fill_between(x, self_suff_vals, alpha=0.3, color='green')
            ax3.set_xlabel('Month')
            ax3.set_ylabel('Self-Sufficiency (%)')
            ax3.set_title('Monthly Self-Sufficiency')
            ax3.set_xticks(x)
            ax3.set_xticklabels(month_names)
            ax3.set_ylim(0, 100)
            ax3.grid(True, alpha=0.3)
            ax3.axhline(y=self_sufficiency, color='red', linestyle='--', alpha=0.5, label=f'Annual Avg: {self_sufficiency:.1f}%')
            ax3.legend()
            
            # Plot 4: Annual summary text
            ax4 = axes[1, 1]
            ax4.axis('off')
            
            summary_text = f"""
ANNUAL ENERGY SUMMARY

Total Consumption:      {annual_consumption:>10,.0f} kWh
Total Generation:       {annual_generation:>10,.0f} kWh
─────────────────────────────────────────

Grid Import:            {annual_import:>10,.0f} kWh
Grid Export:            {annual_export:>10,.0f} kWh
Net Energy Balance:     {net_balance:>10,.0f} kWh

Self-Consumption:       {annual_self_consumption:>10,.0f} kWh
Self-Sufficiency:       {self_sufficiency:>10.1f} %
─────────────────────────────────────────

MONETARY BALANCE

Export Revenue:         {annual_export_revenue:>10,.2f} EUR
Import Cost (paid):     {annual_import_cost:>10,.2f} EUR
Net Monetary Balance:   {net_money_balance:>10,.2f} EUR
Credit Remaining:       {final_credit:>10,.2f} EUR

Total Savings:          {net_money_balance + final_credit:>10,.2f} EUR
─────────────────────────────────────────

Battery Capacity:       {battery_calc.battery_capacity:>10.1f} kWh
PV System Size:         {solar_system.peak_power_kw:>10.1f} kWp
─────────────────────────────────────────

PRICING (incl. VAT)
Import Rate:            {import_rate:>10.4f} EUR/kWh
Export Rate:            {export_rate:>10.4f} EUR/kWh
─────────────────────────────────────────

{'✓ Net EXPORTER' if net_balance >= 0 else '✗ Net IMPORTER'}
{f'Surplus: {net_balance:,.0f} kWh' if net_balance >= 0 else f'Deficit: {-net_balance:,.0f} kWh'}
            """
            
            ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes,
                    fontsize=11, verticalalignment='top', family='monospace',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            plt.tight_layout()
            fig.show()
            
            self.unified_status.setText("✓ Annual analysis complete")
            
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Analysis Error", f"Error generating annual analysis:\n{str(e)}\n\n{traceback.format_exc()}")
            self.unified_status.setText("✗ Error generating analysis")
    
    def show_scenario_comparison(self):
        """Compare three scenarios: No PV, PV Only, PV+Battery"""
        household, solar_system, battery_calc = self.get_unified_config()
        if not household or not solar_system or not battery_calc:
            return
        
        self.unified_status.setText("Calculating three scenarios... This will take a moment...")
        QApplication.processEvents()
        
        try:
            import matplotlib.pyplot as plt
            from datetime import datetime, timedelta
            
            # Get pricing parameters
            selling_price = float(self.nordpool_price.text()) if hasattr(self, 'nordpool_price') else 0.06
            transfer_cost = float(self.transfer_cost.text()) if hasattr(self, 'transfer_cost') else 0.04
            electricity_cost = float(self.electricity_cost.text()) if hasattr(self, 'electricity_cost') else 0.08
            service_cost = float(self.service_cost.text()) if hasattr(self, 'service_cost') else 0.01
            vat_rate = float(self.vat_rate.text()) / 100.0 if hasattr(self, 'vat_rate') else 0.21
            
            import_rate = (electricity_cost + transfer_cost + service_cost) * (1 + vat_rate)
            export_rate = selling_price - transfer_cost * (1 + vat_rate)
            export_rate = max(0, export_rate)
            
            year = 2024
            
            # Get system costs for ROI calculation
            pv_cost = float(self.pv_cost.text()) if hasattr(self, 'pv_cost') else solar_system.peak_power_kw * 1000
            battery_cost = float(self.battery_cost.text()) if hasattr(self, 'battery_cost') else battery_calc.battery_capacity * 500
            
            # SCENARIO 1: No PV, No Battery (Baseline)
            self.unified_status.setText("Scenario 1/3: Calculating baseline (no PV)...")
            QApplication.processEvents()
            
            scenario1_cost = 0.0
            total_consumption_kwh = 0.0
            
            for day_of_year in range(1, 366):
                date_obj = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
                month = date_obj.month
                day_of_week = date_obj.weekday()
                is_weekday = day_of_week < 5
                
                # Generate consumption pattern using the generator
                daily_consumption = self.consumption_generator.get_daily_consumption(
                    household, month, is_weekday, day_of_week, include_ev=True
                )
                total_consumption_kwh += daily_consumption
                
                # All consumption comes from grid
                scenario1_cost += daily_consumption * import_rate
            
            # SCENARIO 2: PV Only (No Battery)
            self.unified_status.setText("Scenario 2/3: Calculating PV without battery...")
            QApplication.processEvents()
            
            scenario2_import = 0.0
            scenario2_export = 0.0
            scenario2_self_consumption = 0.0
            
            for day_of_year in range(1, 366):
                date_obj = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
                month = date_obj.month
                day_of_week = date_obj.weekday()
                
                # Generate hourly patterns using the generators
                for hour in range(24):
                    consumption = self.consumption_generator.get_hourly_consumption(
                        household, month, day_of_week, hour, include_ev=True
                    )
                    generation = self.solar_generator.get_hourly_generation(
                        solar_system, month, hour
                    )
                    
                    if generation >= consumption:
                        # Self-consume all, export excess
                        scenario2_self_consumption += consumption
                        scenario2_export += (generation - consumption)
                    else:
                        # Self-consume what's available, import rest
                        scenario2_self_consumption += generation
                        scenario2_import += (consumption - generation)
            
            scenario2_cost = scenario2_import * import_rate - scenario2_export * export_rate
            
            # SCENARIO 3: PV + Battery (Full System)
            self.unified_status.setText("Scenario 3/3: Calculating PV with battery...")
            QApplication.processEvents()
            
            scenario3_import = 0.0
            scenario3_export = 0.0
            scenario3_self_consumption = 0.0
            current_soc = battery_calc.battery_capacity * 0.5
            
            for day_of_year in range(1, 366):
                date_obj = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
                month = date_obj.month
                day_of_week = date_obj.weekday()
                
                result = battery_calc.simulate_daily_flow(
                    self.consumption_generator, self.solar_generator,
                    household, solar_system,
                    month, day_of_week, initial_soc=current_soc
                )
                
                current_soc = result.hourly_battery_soc[-1]
                
                scenario3_import += result.total_grid_import
                scenario3_export += result.total_grid_export
                scenario3_self_consumption += result.total_self_consumption
            
            scenario3_cost = scenario3_import * import_rate - scenario3_export * export_rate
            
            # Calculate savings
            savings_pv_only = scenario1_cost - scenario2_cost
            savings_pv_battery = scenario1_cost - scenario3_cost
            additional_savings_battery = scenario2_cost - scenario3_cost
            
            # Calculate payback periods
            payback_pv_only = pv_cost / savings_pv_only if savings_pv_only > 0 else float('inf')
            payback_pv_battery = (pv_cost + battery_cost) / savings_pv_battery if savings_pv_battery > 0 else float('inf')
            
            # Self-sufficiency ratios
            ss_pv_only = (scenario2_self_consumption / total_consumption_kwh * 100) if total_consumption_kwh > 0 else 0
            ss_pv_battery = (scenario3_self_consumption / total_consumption_kwh * 100) if total_consumption_kwh > 0 else 0
            
            # Create visualization
            fig = plt.figure(figsize=(18, 14))
            gs = fig.add_gridspec(4, 2, hspace=0.35, wspace=0.3)
            
            # Plot 1: Annual Cost Comparison
            ax1 = fig.add_subplot(gs[0, 0])
            scenarios = ['No PV\nNo Battery', 'PV Only\nNo Battery', 'PV +\nBattery']
            costs = [scenario1_cost, scenario2_cost, scenario3_cost]
            colors = ['red', 'orange', 'green']
            
            bars = ax1.bar(scenarios, costs, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
            ax1.set_ylabel('Annual Cost (EUR)', fontsize=11, fontweight='bold')
            ax1.set_title('Annual Electricity Cost Comparison', fontsize=12, fontweight='bold')
            ax1.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for bar, cost in zip(bars, costs):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{cost:,.0f} EUR',
                        ha='center', va='bottom', fontweight='bold', fontsize=10)
            
            # Plot 2: Savings Comparison
            ax2 = fig.add_subplot(gs[0, 1])
            savings_labels = ['PV Only\nvs Baseline', 'PV + Battery\nvs Baseline', 'Battery\nAdded Value']
            savings_values = [savings_pv_only, savings_pv_battery, additional_savings_battery]
            colors2 = ['orange', 'green', 'blue']
            
            bars2 = ax2.bar(savings_labels, savings_values, color=colors2, alpha=0.7, edgecolor='black', linewidth=2)
            ax2.set_ylabel('Annual Savings (EUR)', fontsize=11, fontweight='bold')
            ax2.set_title('Annual Savings Comparison', fontsize=12, fontweight='bold')
            ax2.grid(True, alpha=0.3, axis='y')
            
            for bar, saving in zip(bars2, savings_values):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{saving:,.0f} EUR',
                        ha='center', va='bottom', fontweight='bold', fontsize=10)
            
            # Plot 3: Self-Sufficiency Comparison
            ax3 = fig.add_subplot(gs[1, 0])
            ss_labels = ['No PV', 'PV Only', 'PV + Battery']
            ss_values = [0, ss_pv_only, ss_pv_battery]
            colors3 = ['red', 'orange', 'green']
            
            bars3 = ax3.bar(ss_labels, ss_values, color=colors3, alpha=0.7, edgecolor='black', linewidth=2)
            ax3.set_ylabel('Self-Sufficiency (%)', fontsize=11, fontweight='bold')
            ax3.set_title('Energy Self-Sufficiency', fontsize=12, fontweight='bold')
            ax3.set_ylim(0, 100)
            ax3.grid(True, alpha=0.3, axis='y')
            ax3.axhline(y=100, color='black', linestyle='--', alpha=0.3)
            
            for bar, ss in zip(bars3, ss_values):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{ss:.1f}%',
                        ha='center', va='bottom', fontweight='bold', fontsize=10)
            
            # Plot 4: Payback Period
            ax4 = fig.add_subplot(gs[1, 1])
            payback_labels = ['PV Only', 'PV + Battery']
            payback_values = [payback_pv_only if payback_pv_only != float('inf') else 0,
                             payback_pv_battery if payback_pv_battery != float('inf') else 0]
            colors4 = ['orange', 'green']
            
            bars4 = ax4.bar(payback_labels, payback_values, color=colors4, alpha=0.7, edgecolor='black', linewidth=2)
            ax4.set_ylabel('Years to Payback', fontsize=11, fontweight='bold')
            ax4.set_title('Investment Payback Period', fontsize=12, fontweight='bold')
            ax4.grid(True, alpha=0.3, axis='y')
            
            for bar, years in zip(bars4, payback_values):
                if years > 0:
                    height = bar.get_height()
                    ax4.text(bar.get_x() + bar.get_width()/2., height,
                            f'{years:.1f} yrs',
                            ha='center', va='bottom', fontweight='bold', fontsize=10)
            
            # Plot 5: Energy Flow Comparison (Grid Import/Export)
            ax5 = fig.add_subplot(gs[2, 0])
            x_pos = range(3)
            width = 0.35
            
            import_vals = [total_consumption_kwh, scenario2_import, scenario3_import]
            export_vals = [0, scenario2_export, scenario3_export]
            
            ax5.bar([p - width/2 for p in x_pos], import_vals, width, label='Grid Import', 
                   color='red', alpha=0.7, edgecolor='black')
            ax5.bar([p + width/2 for p in x_pos], export_vals, width, label='Grid Export', 
                   color='green', alpha=0.7, edgecolor='black')
            
            ax5.set_xlabel('Scenario', fontsize=11, fontweight='bold')
            ax5.set_ylabel('Energy (kWh)', fontsize=11, fontweight='bold')
            ax5.set_title('Grid Import vs Export', fontsize=12, fontweight='bold')
            ax5.set_xticks(x_pos)
            ax5.set_xticklabels(['No PV', 'PV Only', 'PV + Battery'])
            ax5.legend()
            ax5.grid(True, alpha=0.3, axis='y')
            
            # Plot 6: Payback Time Graph (Cumulative Cost Over Time)
            ax6 = fig.add_subplot(gs[3, 0])
            
            # Calculate cumulative costs over time (20 years)
            years = list(range(0, 21))
            
            # Scenario 1: No PV - just annual costs accumulating
            cumulative_no_pv = [scenario1_cost * year for year in years]
            
            # Scenario 2: PV Only - upfront cost + annual electricity costs
            cumulative_pv_only = [pv_cost + scenario2_cost * year for year in years]
            
            # Scenario 3: PV + Battery - upfront cost + annual electricity costs
            cumulative_pv_battery = [pv_cost + battery_cost + scenario3_cost * year for year in years]
            
            ax6.plot(years, cumulative_no_pv, 'r-', linewidth=3, label='No PV (Baseline)', marker='o', markersize=4)
            ax6.plot(years, cumulative_pv_only, 'orange', linewidth=3, label='PV Only', marker='s', markersize=4)
            ax6.plot(years, cumulative_pv_battery, 'g-', linewidth=3, label='PV + Battery', marker='^', markersize=4)
            
            # Add breakeven points
            if payback_pv_only < 20:
                ax6.axvline(x=payback_pv_only, color='orange', linestyle='--', alpha=0.5, linewidth=2)
                ax6.text(payback_pv_only, max(cumulative_no_pv) * 0.8, 
                        f'PV payback\n{payback_pv_only:.1f} yr', 
                        ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='orange', alpha=0.3))
            
            if payback_pv_battery < 20:
                ax6.axvline(x=payback_pv_battery, color='green', linestyle='--', alpha=0.5, linewidth=2)
                ax6.text(payback_pv_battery, max(cumulative_no_pv) * 0.6, 
                        f'PV+Battery payback\n{payback_pv_battery:.1f} yr', 
                        ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='green', alpha=0.3))
            
            ax6.set_xlabel('Years', fontsize=11, fontweight='bold')
            ax6.set_ylabel('Cumulative Cost (EUR)', fontsize=11, fontweight='bold')
            ax6.set_title('Payback Analysis - Cumulative Cost Over Time', fontsize=12, fontweight='bold')
            ax6.legend(loc='upper left', fontsize=10)
            ax6.grid(True, alpha=0.3)
            ax6.set_xlim(0, 20)
            
            # Plot 7: Summary Text
            ax7 = fig.add_subplot(gs[3, 1])
            ax7.axis('off')
            
            summary_text = f"""
SCENARIO COMPARISON SUMMARY

═══════════════════════════════════════════════════════

SCENARIO 1: No PV, No Battery (BASELINE)
  Annual Cost:           {scenario1_cost:>10,.2f} EUR
  Self-Sufficiency:      {0:>10.1f} %
  Grid Import:           {total_consumption_kwh:>10,.0f} kWh
  Grid Export:           {0:>10,.0f} kWh

───────────────────────────────────────────────────────

SCENARIO 2: PV Only (No Battery)
  Annual Cost:           {scenario2_cost:>10,.2f} EUR
  Annual Savings:        {savings_pv_only:>10,.2f} EUR
  Self-Sufficiency:      {ss_pv_only:>10.1f} %
  Grid Import:           {scenario2_import:>10,.0f} kWh
  Grid Export:           {scenario2_export:>10,.0f} kWh
  
  Investment:            {pv_cost:>10,.2f} EUR
  Payback Period:        {payback_pv_only:>10.1f} years

───────────────────────────────────────────────────────

SCENARIO 3: PV + Battery (FULL SYSTEM)
  Annual Cost:           {scenario3_cost:>10,.2f} EUR
  Annual Savings:        {savings_pv_battery:>10,.2f} EUR
  Self-Sufficiency:      {ss_pv_battery:>10.1f} %
  Grid Import:           {scenario3_import:>10,.0f} kWh
  Grid Export:           {scenario3_export:>10,.0f} kWh
  
  Investment:            {pv_cost + battery_cost:>10,.2f} EUR
  Payback Period:        {payback_pv_battery:>10.1f} years

───────────────────────────────────────────────────────

BATTERY VALUE-ADD
  Additional Savings:    {additional_savings_battery:>10,.2f} EUR/year
  Battery Investment:    {battery_cost:>10,.2f} EUR
  Battery Payback:       {battery_cost/additional_savings_battery if additional_savings_battery > 0 else float('inf'):>10.1f} years

═══════════════════════════════════════════════════════

System Configuration:
  PV System:             {solar_system.peak_power_kw:>10.1f} kWp
  Battery Capacity:      {battery_calc.battery_capacity:>10.1f} kWh
  Annual Consumption:    {total_consumption_kwh:>10,.0f} kWh

Pricing (incl. VAT):
  Import Rate:           {import_rate:>10.4f} EUR/kWh
  Export Rate:           {export_rate:>10.4f} EUR/kWh
            """
            
            ax7.text(0.05, 0.95, summary_text, transform=ax7.transAxes,
                    fontsize=9, verticalalignment='top', family='monospace',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
            
            fig.suptitle('PV System Scenario Comparison - Financial Analysis', 
                        fontsize=16, fontweight='bold', y=0.995)
            
            plt.tight_layout()
            fig.show()
            
            self.unified_status.setText("✓ Scenario comparison complete")
            
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Analysis Error", f"Error generating scenario comparison:\n{str(e)}\n\n{traceback.format_exc()}")
            self.unified_status.setText("✗ Error generating comparison")
    
    def get_battery_soc_for_date(self, year: int, day_of_year: int, 
                                  household, solar_system, battery_calc) -> float:
        """
        Get the battery SOC at the start of a given day, simulating all previous days if needed
        
        Args:
            year: Year
            day_of_year: Day of year (1-365/366)
            household: HouseholdProfile
            solar_system: SolarSystemProfile
            battery_calc: BatteryFlowCalculator
        
        Returns:
            Initial SOC for the requested day (kWh)
        """
        # If it's day 1, start at 50%
        if day_of_year == 1:
            initial_soc = battery_calc.battery_capacity * 0.5
            self.battery_soc_cache[(year, 1)] = initial_soc
            return initial_soc
        
        # Check if we already have this day's initial SOC
        if (year, day_of_year) in self.battery_soc_cache:
            return self.battery_soc_cache[(year, day_of_year)]
        
        # Find the last cached day before this one
        last_cached_day = 0
        last_cached_soc = battery_calc.battery_capacity * 0.5  # Default 50%
        
        for cached_day in range(day_of_year - 1, 0, -1):
            if (year, cached_day) in self.battery_soc_cache:
                last_cached_day = cached_day
                last_cached_soc = self.battery_soc_cache[(year, cached_day)]
                break
        
        # Simulate all days from last cached day to the day before target
        current_soc = last_cached_soc
        
        for day in range(last_cached_day + 1, day_of_year):
            # Convert day_of_year to month and day_of_week
            from datetime import datetime, timedelta
            date_obj = datetime(year, 1, 1) + timedelta(days=day - 1)
            month = date_obj.month
            day_of_week = date_obj.weekday()
            
            # Simulate this day
            result = battery_calc.simulate_daily_flow(
                self.consumption_generator, self.solar_generator,
                household, solar_system,
                month, day_of_week, initial_soc=current_soc
            )
            
            # Store the final SOC for next day
            current_soc = result.final_soc
            self.battery_soc_cache[(year, day)] = current_soc
        
        # Return the SOC at start of target day (= end of previous day)
        return current_soc
    
    def show_unified_weekly_comparison(self):
        """Show weekly energy comparison"""
        household, solar_system, battery_calc = self.get_unified_config()
        if not household or not solar_system or not battery_calc:
            return
        
        self.unified_status.setText("Generating weekly comparison...")
        QApplication.processEvents()
        
        try:
            graph_gen = IntegratedEnergyGraphs(
                self.consumption_generator, self.solar_generator, battery_calc,
                household, solar_system
            )
            
            fig = graph_gen.plot_weekly_comparison(month=6)
            fig.show()
            
            self.unified_status.setText("✓ Weekly comparison displayed")
        except Exception as e:
            QMessageBox.critical(self, "Graph Error", f"Error generating graph: {str(e)}")
            self.unified_status.setText("✗ Error generating graph")
    
    def show_unified_seasonal_comparison(self):
        """Show seasonal energy comparison"""
        household, solar_system, battery_calc = self.get_unified_config()
        if not household or not solar_system or not battery_calc:
            return
        
        self.unified_status.setText("Generating seasonal comparison...")
        QApplication.processEvents()
        
        try:
            graph_gen = IntegratedEnergyGraphs(
                self.consumption_generator, self.solar_generator, battery_calc,
                household, solar_system
            )
            
            fig = graph_gen.plot_seasonal_comparison()
            fig.show()
            
            self.unified_status.setText("✓ Seasonal comparison displayed")
        except Exception as e:
            QMessageBox.critical(self, "Graph Error", f"Error generating graph: {str(e)}")
            self.unified_status.setText("✗ Error generating graph")
    
    def show_unified_annual_summary(self):
        """Show annual energy summary"""
        household, solar_system, battery_calc = self.get_unified_config()
        if not household or not solar_system or not battery_calc:
            return
        
        self.unified_status.setText("Generating annual summary (this may take a moment)...")
        QApplication.processEvents()
        
        try:
            graph_gen = IntegratedEnergyGraphs(
                self.consumption_generator, self.solar_generator, battery_calc,
                household, solar_system
            )
            
            fig = graph_gen.plot_annual_summary()
            fig.show()
            
            self.unified_status.setText("✓ Annual summary displayed")
        except Exception as e:
            QMessageBox.critical(self, "Graph Error", f"Error generating graph: {str(e)}")
            self.unified_status.setText("✗ Error generating graph")
    
    def show_unified_all_graphs(self):
        """Generate all energy flow graphs"""
        household, solar_system, battery_calc = self.get_unified_config()
        if not household or not solar_system or not battery_calc:
            return
        
        self.unified_status.setText("Generating all graphs (this will take a moment)...")
        QApplication.processEvents()
        
        try:
            graph_gen = IntegratedEnergyGraphs(
                self.consumption_generator, self.solar_generator, battery_calc,
                household, solar_system
            )
            
            # Generate all graphs
            fig1 = graph_gen.plot_daily_energy_flow(month=6, day_of_week=0)
            fig2 = graph_gen.plot_weekly_comparison(month=6)
            fig3 = graph_gen.plot_seasonal_comparison()
            fig4 = graph_gen.plot_annual_summary()
            
            # Save them
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fig1.savefig(f'Unified_Daily_Flow_{timestamp}.png', dpi=150, bbox_inches='tight')
            fig2.savefig(f'Unified_Weekly_Comparison_{timestamp}.png', dpi=150, bbox_inches='tight')
            fig3.savefig(f'Unified_Seasonal_Comparison_{timestamp}.png', dpi=150, bbox_inches='tight')
            fig4.savefig(f'Unified_Annual_Summary_{timestamp}.png', dpi=150, bbox_inches='tight')
            
            # Show the last one
            fig4.show()
            
            self.unified_status.setText(f"✓ All graphs generated and saved with timestamp {timestamp}")
            QMessageBox.information(self, "Success", 
                                  f"All graphs generated successfully!\n\n"
                                  f"Saved as:\n"
                                  f"• Unified_Daily_Flow_{timestamp}.png\n"
                                  f"• Unified_Weekly_Comparison_{timestamp}.png\n"
                                  f"• Unified_Seasonal_Comparison_{timestamp}.png\n"
                                  f"• Unified_Annual_Summary_{timestamp}.png")
        except Exception as e:
            QMessageBox.critical(self, "Graph Error", f"Error generating graphs: {str(e)}")
            self.unified_status.setText("✗ Error generating graphs")
    
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
                # Get irradiance from selected location
                location_key = self.pv_location.currentData() if hasattr(self, 'pv_location') else 'riga_latvia'
                if SOLAR_V2_AVAILABLE and location_key in LOCATIONS:
                    irradiance = LOCATIONS[location_key].avg_daily_irradiance
                else:
                    irradiance = 2.9  # Default fallback
                
                pv_system = PVSystemSpecs(
                    peak_power_kw=float(self.pv_size.text()),
                    installation_cost=float(self.pv_cost.text()),
                    avg_daily_irradiance=irradiance
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
            
            # EV Profile (for PV calculator V1)
            ev_profile = EVProfile(enabled=False)
            if self.ev_enabled.isChecked():
                # Get consumption from display or calculate from weekly distance
                consumption_text = self.ev_consumption_display.text()
                if consumption_text and consumption_text != "--":
                    efficiency = float(consumption_text)
                else:
                    efficiency = 20.0  # Default fallback
                
                weekly_km = float(self.ev_weekly_km.text())
                daily_km = weekly_km / 7.0
                daily_kwh = daily_km * efficiency / 100.0
                
                ev_profile = EVProfile(
                    enabled=True,
                    daily_driving_kwh=daily_kwh,
                    charging_power_kw=float(self.ev_charger_power.text())
                )
            
            # EV Consumption Profile (for consumption generator V2)
            ev_consumption_profile = None
            if CONSUMPTION_V2_AVAILABLE and self.ev_enabled.isChecked():
                # Get consumption and weekly distance
                consumption_text = self.ev_consumption_display.text()
                if consumption_text and consumption_text != "--":
                    efficiency = float(consumption_text)
                else:
                    efficiency = 18.0  # Default fallback
                
                weekly_km = float(self.ev_weekly_km.text())
                charger_power = float(self.ev_charger_power.text())
                start_hour = self.ev_charging_start.value()
                
                # Calculate daily consumption
                daily_km = weekly_km / 7.0
                daily_kwh = daily_km * efficiency / 100.0
                
                # Calculate charging duration in hours
                duration_hours = daily_kwh / charger_power
                
                # Generate charging hours list
                charging_hours = []
                current_hour = start_hour
                hours_to_add = int(duration_hours) + 1  # Add extra hour to ensure full charge
                
                for _ in range(hours_to_add):
                    charging_hours.append(current_hour % 24)
                    current_hour += 1
                
                # Charge every day by default (simplified approach)
                charging_days = [True] * 7
                
                ev_consumption_profile = EVConsumptionProfile(
                    enabled=True,
                    weekly_distance_km=weekly_km,
                    consumption_per_100km=efficiency,
                    charging_days=charging_days,
                    charging_hours=charging_hours
                )
            
            return tariff, consumption, pv_system, battery, nord_pool, ev_profile, ev_consumption_profile
        except ValueError as e:
            QMessageBox.critical(self, "Input Error", 
                               f"Invalid input value: {str(e)}\nPlease check all fields contain valid numbers.")
            return None
    
    def calculate(self):
        """Perform calculation and display results"""
        inputs = self.get_inputs()
        if not inputs:
            return
        
        tariff, consumption, pv_system, battery, nord_pool, ev_profile, ev_consumption_profile = inputs
        
        # Store EV consumption profile for use in graphs/analysis
        self.current_ev_consumption_profile = ev_consumption_profile
        
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
                'location': self.pv_location.currentData() if hasattr(self, 'pv_location') else 'riga_latvia'
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
                'make': self.ev_make.currentData() if hasattr(self, 'ev_make') else '',
                'model': self.ev_model.currentData() if hasattr(self, 'ev_model') else '',
                'configuration': self.ev_configuration.currentData() if hasattr(self, 'ev_configuration') else '',
                'consumption': self.ev_consumption_display.text() if hasattr(self, 'ev_consumption_display') else '--',
                'weekly_km': self.ev_weekly_km.text() if hasattr(self, 'ev_weekly_km') else '420',
                'charger_power': self.ev_charger_power.text(),
                'charging_start': self.ev_charging_start.value() if hasattr(self, 'ev_charging_start') else 22
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
            # Load location if available
            if 'location' in config['pv'] and hasattr(self, 'pv_location'):
                location_key = config['pv']['location']
                index = self.pv_location.findData(location_key)
                if index >= 0:
                    self.pv_location.setCurrentIndex(index)
            
            # Load battery
            self.battery_enabled.setChecked(config['battery']['enabled'])
            self.battery_capacity.setText(str(config['battery']['capacity']))
            self.battery_cost.setText(str(config['battery']['cost']))
            
            # Load Nord Pool
            self.nordpool_price.setText(str(config['nordpool']['price']))
            
            # Load EV (if exists in config)
            if 'ev' in config:
                self.ev_enabled.setChecked(config['ev']['enabled'])
                
                # Load EV make/model/configuration if available
                if 'make' in config['ev'] and hasattr(self, 'ev_make'):
                    make_key = config['ev']['make']
                    make_index = self.ev_make.findData(make_key)
                    if make_index >= 0:
                        self.ev_make.setCurrentIndex(make_index)
                        
                        # Load model
                        if 'model' in config['ev'] and hasattr(self, 'ev_model'):
                            model_key = config['ev']['model']
                            model_index = self.ev_model.findData(model_key)
                            if model_index >= 0:
                                self.ev_model.setCurrentIndex(model_index)
                                
                                # Load configuration
                                if 'configuration' in config['ev'] and hasattr(self, 'ev_configuration'):
                                    config_key = config['ev']['configuration']
                                    config_index = self.ev_configuration.findData(config_key)
                                    if config_index >= 0:
                                        self.ev_configuration.setCurrentIndex(config_index)
                
                # Load weekly distance
                if 'weekly_km' in config['ev'] and hasattr(self, 'ev_weekly_km'):
                    self.ev_weekly_km.setText(str(config['ev']['weekly_km']))
                elif 'daily_km' in config['ev'] and hasattr(self, 'ev_weekly_km'):
                    # Convert old daily to weekly
                    daily = float(config['ev']['daily_km'])
                    self.ev_weekly_km.setText(str(daily * 7))
                
                self.ev_charger_power.setText(str(config['ev']['charger_power']))
                
                # Load charging start time
                if 'charging_start' in config['ev'] and hasattr(self, 'ev_charging_start'):
                    self.ev_charging_start.setValue(int(config['ev']['charging_start']))
            
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
        # Set default location
        if hasattr(self, 'pv_location'):
            self.pv_location.setCurrentIndex(0)  # Default to first location
        self.battery_enabled.setChecked(True)
        self.battery_capacity.setText("7.0")
        self.battery_cost.setText("4000")
        self.nordpool_price.setText("0.06")
        self.ev_enabled.setChecked(False)
        # Reset EV to defaults
        if hasattr(self, 'ev_make'):
            self.ev_make.setCurrentIndex(0)  # "Select Make"
        if hasattr(self, 'ev_weekly_km'):
            self.ev_weekly_km.setText("420")
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
        
        tariff, consumption, pv_system, battery, nord_pool, ev_profile, ev_consumption_profile = inputs
        
        # Store EV consumption profile for use in graphs/analysis
        self.current_ev_consumption_profile = ev_consumption_profile
        
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
            ev_weekly_km = float(self.ev_weekly_km.text()) if hasattr(self, 'ev_weekly_km') else 420
            ev_daily_km = ev_weekly_km / 7.0
            report.append(f"SCENARIO B: HOUSEHOLD WITH EV ({ev_daily_km:.0f} km/day, {ev_weekly_km:.0f} km/week)")
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
                # Get consumption from display or use default
                consumption_text = self.ev_consumption_display.text() if hasattr(self, 'ev_consumption_display') else "20"
                if consumption_text and consumption_text != "--":
                    efficiency = float(consumption_text)
                else:
                    efficiency = 20.0  # Default
                
                weekly_km = float(self.ev_weekly_km.text()) if hasattr(self, 'ev_weekly_km') else 420
                daily_km = weekly_km / 7.0
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
    
    def show_weekly_graph(self):
        """Show weekly energy balance graph"""
        if not self.check_calculator():
            return
        
        week_number = self.week_spinbox.value()
        
        self.graph_status.setText(f"Generating weekly analysis for week {week_number}...")
        QApplication.processEvents()
        
        try:
            graph_gen = PVGraphGenerator(self.current_calculator)
            has_battery = self.current_calculator.battery is not None
            graph_gen.plot_weekly_energy_balance(week_number=week_number, with_battery=has_battery, show=True)
            self.graph_status.setText(f"✓ Weekly energy balance for week {week_number} displayed")
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

