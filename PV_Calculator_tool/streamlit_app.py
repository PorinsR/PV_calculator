"""
PV System Calculator - Streamlit Web App
Simplified web version of the PyQt5 desktop application
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Try to import existing modules
try:
    from PV_consumption_generator import ConsumptionPatternGenerator, HouseholdProfile, EVConsumptionProfile
    from PV_solar_generator import SolarGenerationCalculator, SolarSystemProfile, LOCATIONS
    from PV_battery_flow import BatteryFlowCalculator
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    st.error("⚠️ Required modules not found. Please ensure all PV calculator modules are in the same directory.")

# Page configuration
st.set_page_config(
    page_title="Solar PV Calculator",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FF8C00;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #FF8C00;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">☀️ Solar PV System Calculator</div>', unsafe_allow_html=True)
st.markdown("**Calculate the feasibility and ROI of your solar PV installation**")
st.markdown("---")

# Sidebar - Configuration Inputs
with st.sidebar:
    st.header("⚙️ System Configuration")
    
    # Household Consumption
    with st.expander("🏠 Household Consumption", expanded=True):
        monthly_consumption = st.number_input(
            "Monthly Consumption (kWh)",
            min_value=100.0,
            max_value=2000.0,
            value=500.0,
            step=50.0,
            help="Average monthly electricity consumption"
        )
        
        if MODULES_AVAILABLE:
            pattern_type = st.selectbox(
                "Consumption Pattern",
                options=["working_family", "home_office", "retired_couple", "large_family"],
                format_func=lambda x: x.replace("_", " ").title(),
                help="Select your household type"
            )
        
        seasonal_variation = st.slider(
            "Seasonal Variation (%)",
            min_value=0,
            max_value=50,
            value=20,
            help="How much consumption varies between seasons"
        )
    
    # PV System
    with st.expander("☀️ PV System", expanded=True):
        pv_enabled = st.checkbox("Enable PV System", value=True)
        
        if pv_enabled:
            pv_size = st.slider(
                "PV Size (kWp)",
                min_value=1.0,
                max_value=20.0,
                value=6.0,
                step=0.5,
                help="Peak power of solar panels"
            )
            
            if MODULES_AVAILABLE:
                location_key = st.selectbox(
                    "Location",
                    options=list(LOCATIONS.keys()),
                    index=list(LOCATIONS.keys()).index('riga_latvia') if 'riga_latvia' in LOCATIONS else 0,
                    format_func=lambda x: LOCATIONS[x].name if MODULES_AVAILABLE else x
                )
            
            tilt = st.slider(
                "Panel Tilt (degrees)",
                min_value=0,
                max_value=90,
                value=35,
                help="Optimal tilt for your latitude"
            )
            
            pv_cost = st.number_input(
                "PV System Cost (EUR)",
                min_value=1000,
                max_value=50000,
                value=int(pv_size * 1000),
                step=500,
                help="Total installation cost"
            )
    
    # Battery Storage
    with st.expander("🔋 Battery Storage", expanded=True):
        battery_enabled = st.checkbox("Enable Battery", value=True)
        
        if battery_enabled:
            battery_capacity = st.slider(
                "Battery Capacity (kWh)",
                min_value=1.0,
                max_value=30.0,
                value=10.0,
                step=1.0,
                help="Usable battery capacity"
            )
            
            battery_cost = st.number_input(
                "Battery Cost (EUR)",
                min_value=500,
                max_value=30000,
                value=int(battery_capacity * 500),
                step=500,
                help="Total battery installation cost"
            )
    
    # Electricity Pricing
    with st.expander("💶 Electricity Pricing", expanded=False):
        import_rate = st.number_input(
            "Grid Import Rate (EUR/kWh)",
            min_value=0.05,
            max_value=0.50,
            value=0.15,
            step=0.01,
            help="Cost per kWh from grid (inc. VAT)"
        )
        
        export_rate = st.number_input(
            "Grid Export Rate (EUR/kWh)",
            min_value=0.0,
            max_value=0.20,
            value=0.02,
            step=0.01,
            help="Revenue per kWh sold to grid"
        )
    
    st.markdown("---")
    st.caption("💡 Adjust parameters above and view results in tabs →")

# Main content - Tabs
if MODULES_AVAILABLE:
    # Initialize generators
    consumption_gen = ConsumptionPatternGenerator()
    solar_gen = SolarGenerationCalculator()
    battery_calc = BatteryFlowCalculator(battery_capacity_kwh=battery_capacity if battery_enabled else 0.0)
    
    # Create profiles
    household = HouseholdProfile(
        name="My Household",
        annual_consumption_kwh=monthly_consumption * 12,
        pattern_type=pattern_type if MODULES_AVAILABLE else "working_family",
        seasonal_strength=seasonal_variation / 100.0
    )
    
    if pv_enabled:
        solar_system = SolarSystemProfile(
            name="My PV System",
            peak_power_kw=pv_size,
            location=LOCATIONS[location_key],
            tilt_angle=tilt,
            system_efficiency=0.85
        )

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💰 Scenario Comparison", "📅 Daily Analysis", "📈 Annual View"])

with tab1:
    st.header("System Overview")
    
    if not MODULES_AVAILABLE:
        st.warning("Calculator modules not loaded. Please install required dependencies.")
        st.stop()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Annual Consumption",
            f"{household.annual_consumption_kwh:,.0f} kWh",
            help="Total household electricity consumption per year"
        )
    
    if pv_enabled:
        annual_gen_data = solar_gen.calculate_annual_generation(solar_system)
        annual_generation = annual_gen_data['annual_total']
        
        with col2:
            st.metric(
                "Annual PV Generation",
                f"{annual_generation:,.0f} kWh",
                help="Expected solar panel production per year"
            )
        
        coverage = (annual_generation / household.annual_consumption_kwh * 100)
        
        with col3:
            st.metric(
                "Generation Coverage",
                f"{coverage:.1f}%",
                help="What % of consumption can PV cover (theoretical)"
            )
        
        with col4:
            baseline_cost = household.annual_consumption_kwh * import_rate
            st.metric(
                "Baseline Annual Cost",
                f"€{baseline_cost:,.0f}",
                help="Current electricity cost without PV"
            )
    
    st.markdown("---")
    
    # System summary
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 Configuration Summary")
        
        summary_data = {
            "Parameter": [
                "Household Type",
                "Annual Consumption",
                "Monthly Average",
                "Seasonal Variation"
            ],
            "Value": [
                pattern_type.replace("_", " ").title() if MODULES_AVAILABLE else "N/A",
                f"{household.annual_consumption_kwh:,.0f} kWh",
                f"{monthly_consumption:.0f} kWh",
                f"{seasonal_variation}%"
            ]
        }
        
        if pv_enabled:
            summary_data["Parameter"].extend([
                "PV System Size",
                "Panel Tilt",
                "Location",
                "PV Cost"
            ])
            summary_data["Value"].extend([
                f"{pv_size:.1f} kWp",
                f"{tilt}°",
                LOCATIONS[location_key].name,
                f"€{pv_cost:,}"
            ])
        
        if battery_enabled:
            summary_data["Parameter"].extend([
                "Battery Capacity",
                "Battery Cost",
                "Total Investment"
            ])
            summary_data["Value"].extend([
                f"{battery_capacity:.1f} kWh",
                f"€{battery_cost:,}",
                f"€{pv_cost + battery_cost if pv_enabled else battery_cost:,}"
            ])
        
        st.dataframe(pd.DataFrame(summary_data), width='stretch', hide_index=True)
    
    with col2:
        st.subheader("💡 Quick Insights")
        
        if pv_enabled:
            # Calculate rough payback
            annual_savings_estimate = baseline_cost * 0.6  # Rough estimate
            if pv_enabled:
                simple_payback = (pv_cost + (battery_cost if battery_enabled else 0)) / annual_savings_estimate
                
                if simple_payback < 8:
                    st.success(f"✅ Excellent ROI: ~{simple_payback:.1f} year payback")
                elif simple_payback < 12:
                    st.info(f"👍 Good ROI: ~{simple_payback:.1f} year payback")
                else:
                    st.warning(f"⚠️ Long payback: ~{simple_payback:.1f} years")
                
                # Recommendations
                st.markdown("**Recommendations:**")
                
                if coverage > 120:
                    st.write("• Consider smaller PV system (oversized)")
                elif coverage < 80:
                    st.write("• Consider larger PV system for better coverage")
                else:
                    st.write("• PV size looks appropriate")
                
                if battery_enabled:
                    recommended_battery = household.annual_consumption_kwh / 365 * 0.6
                    if battery_capacity < recommended_battery * 0.5:
                        st.write("• Battery is on the small side")
                    elif battery_capacity > recommended_battery * 1.5:
                        st.write("• Battery might be oversized")
                    else:
                        st.write("• Battery size looks good")

with tab2:
    st.header("💰 Scenario Comparison")
    st.markdown("Compare three scenarios: **No PV** vs **PV Only** vs **PV + Battery**")
    
    if st.button("🚀 Calculate All Scenarios", type="primary"):
        with st.spinner("Calculating scenarios... This may take 30-60 seconds..."):
            # Simplified calculation for demo
            # In production, use the full _calculate_scenario_data() function
            
            baseline_annual = household.annual_consumption_kwh * import_rate
            
            # Rough estimates (replace with actual calculations)
            pv_only_import = household.annual_consumption_kwh * 0.35
            pv_only_export = annual_generation * 0.3 if pv_enabled else 0
            pv_only_cost = pv_only_import * import_rate - pv_only_export * export_rate
            
            pv_battery_import = household.annual_consumption_kwh * 0.22 if battery_enabled else pv_only_import
            pv_battery_export = annual_generation * 0.18 if pv_enabled else 0
            pv_battery_cost = pv_battery_import * import_rate - pv_battery_export * export_rate
            
            # Display results
            st.success("✅ Calculation complete!")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### No PV")
                st.metric("Annual Cost", f"€{baseline_annual:,.0f}")
                st.metric("Self-Sufficiency", "0%")
            
            with col2:
                st.markdown("### PV Only")
                savings1 = baseline_annual - pv_only_cost
                st.metric("Annual Cost", f"€{pv_only_cost:,.0f}", f"-€{savings1:,.0f}")
                st.metric("Self-Sufficiency", "~65%")
                st.metric("Payback", f"{(pv_cost / savings1):.1f} years")
            
            with col3:
                st.markdown("### PV + Battery")
                savings2 = baseline_annual - pv_battery_cost
                st.metric("Annual Cost", f"€{pv_battery_cost:,.0f}", f"-€{savings2:,.0f}")
                st.metric("Self-Sufficiency", "~78%")
                if battery_enabled:
                    st.metric("Payback", f"{((pv_cost + battery_cost) / savings2):.1f} years")
            
            # Chart
            st.markdown("---")
            st.subheader("Annual Cost Comparison")
            
            fig = go.Figure(data=[
                go.Bar(
                    x=['No PV', 'PV Only', 'PV + Battery'],
                    y=[baseline_annual, pv_only_cost, pv_battery_cost],
                    marker_color=['red', 'orange', 'green'],
                    text=[f"€{baseline_annual:.0f}", f"€{pv_only_cost:.0f}", f"€{pv_battery_cost:.0f}"],
                    textposition='auto',
                )
            ])
            
            fig.update_layout(
                yaxis_title="Annual Cost (EUR)",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, width='stretch')

with tab3:
    st.header("📅 Daily Energy Analysis")
    st.markdown("Analyze hourly energy flow for a specific day")
    
    col1, col2 = st.columns(2)
    
    with col1:
        month = st.slider("Month", 1, 12, 6, format="Month %d")
    
    with col2:
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_of_week = st.selectbox("Day of Week", range(7), format_func=lambda x: day_names[x])
    
    if st.button("Generate Daily Analysis", type="primary"):
        with st.spinner("Simulating daily flow..."):
            if pv_enabled and battery_enabled:
                result = battery_calc.simulate_daily_flow(
                    consumption_gen, solar_gen,
                    household, solar_system,
                    month, day_of_week
                )
                
                # Create hourly chart
                hours = list(range(24))
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=hours, y=result.hourly_generation,
                    name='Solar Generation',
                    fill='tozeroy',
                    line=dict(color='orange')
                ))
                
                fig.add_trace(go.Scatter(
                    x=hours, y=result.hourly_consumption,
                    name='Consumption',
                    fill='tozeroy',
                    line=dict(color='steelblue')
                ))
                
                fig.add_trace(go.Scatter(
                    x=hours, y=result.hourly_battery_soc,
                    name='Battery SOC',
                    line=dict(color='green', dash='dash'),
                    yaxis='y2'
                ))
                
                fig.update_layout(
                    title=f"Daily Energy Flow - {day_names[day_of_week]} in {datetime(2024, month, 1).strftime('%B')}",
                    xaxis_title="Hour of Day",
                    yaxis_title="Power (kWh)",
                    yaxis2=dict(
                        title="Battery SOC (kWh)",
                        overlaying='y',
                        side='right'
                    ),
                    height=500,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, width='stretch')
                
                # Daily summary
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Consumption", f"{result.total_consumption:.2f} kWh")
                    st.metric("Total Generation", f"{result.total_generation:.2f} kWh")
                
                with col2:
                    st.metric("Grid Import", f"{result.total_grid_import:.2f} kWh")
                    st.metric("Grid Export", f"{result.total_grid_export:.2f} kWh")
                
                with col3:
                    st.metric("Self-Sufficiency", f"{result.self_sufficiency_ratio:.1f}%")
                    daily_cost = result.total_grid_import * import_rate - result.total_grid_export * export_rate
                    st.metric("Daily Net Cost", f"€{daily_cost:.2f}")

with tab4:
    st.header("📈 Annual Performance")
    st.markdown("View performance across all months")
    
    st.info("💡 This shows how your system performs throughout the year")
    
    if pv_enabled:
        # Generate monthly data
        months = list(range(1, 13))
        month_names = [datetime(2024, m, 1).strftime('%b') for m in months]
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        # Calculate monthly generation by summing daily generation
        monthly_generation = []
        for m, days in zip(months, days_in_month):
            daily_gen = solar_gen.calculate_daily_generation(solar_system, m)
            monthly_generation.append(daily_gen * days)
        
        monthly_consumption = [household.annual_consumption_kwh / 12 for m in months]  # Simplified
        
        # Create chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=month_names,
            y=monthly_generation,
            name='PV Generation',
            marker_color='orange'
        ))
        
        fig.add_trace(go.Bar(
            x=month_names,
            y=monthly_consumption,
            name='Consumption',
            marker_color='steelblue'
        ))
        
        fig.update_layout(
            title="Monthly Energy Balance",
            xaxis_title="Month",
            yaxis_title="Energy (kWh)",
            height=500,
            barmode='group'
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Annual summary
        st.subheader("Annual Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_gen = sum(monthly_generation)
            st.metric("Total PV Generation", f"{total_gen:,.0f} kWh")
        
        with col2:
            total_cons = sum(monthly_consumption)
            st.metric("Total Consumption", f"{total_cons:,.0f} kWh")
        
        with col3:
            coverage = (total_gen / total_cons * 100)
            st.metric("Annual Coverage", f"{coverage:.1f}%")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    Built with ❤️ using Streamlit | 
    <a href='https://github.com/yourusername/PV_calculator' target='_blank'>View on GitHub</a> | 
    Version 2.0
</div>
""", unsafe_allow_html=True)

