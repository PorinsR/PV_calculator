# Web Deployment Guide - Making PV Calculator Web-Accessible

## Problem Statement

The current PV Calculator uses **PyQt5** (desktop GUI framework), which cannot run on GitHub Pages or in a web browser. To make it web-accessible, we need to either:

1. Convert the frontend to web technologies
2. Use a Python web framework
3. Deploy as a web service

---

## 🎯 Solution 1: Streamlit (RECOMMENDED)

**Best for**: Quick deployment, keeping Python code mostly intact

### What is Streamlit?

Streamlit is a Python framework that turns data scripts into web apps automatically. Perfect for your use case!

### Advantages

- ✅ Keep 95% of existing Python calculation logic
- ✅ Simple syntax: `st.slider()`, `st.button()`, `st.plotly_chart()`
- ✅ Free hosting on Streamlit Cloud (no GitHub Pages needed)
- ✅ Automatic reactivity (no manual event handling)
- ✅ Built-in caching for performance
- ✅ Mobile-responsive out of the box

### Example Conversion

**Before (PyQt5):**

```python
self.pv_size = QLineEdit()
self.pv_size.setText("6.0")
layout.addWidget(QLabel("PV Size (kWp):"))
layout.addWidget(self.pv_size)

pv_btn = QPushButton("Calculate")
pv_btn.clicked.connect(self.calculate_results)
```

**After (Streamlit):**

```python
pv_size = st.number_input("PV Size (kWp)", value=6.0, min_value=0.0, max_value=30.0)

if st.button("Calculate"):
    results = calculate_results(pv_size)
    st.write(results)
```

### Step-by-Step Migration

#### 1. Install Streamlit

```bash
pip install streamlit plotly
```

#### 2. Create `streamlit_app.py`

```python
import streamlit as st
import plotly.graph_objects as go
from PV_calculator import *  # Your existing modules

# Page config
st.set_page_config(
    page_title="PV System Calculator",
    page_icon="☀️",
    layout="wide"
)

st.title("☀️ Solar PV System Feasibility Calculator")

# Sidebar for inputs
with st.sidebar:
    st.header("System Configuration")

    # Consumption inputs
    st.subheader("Household Consumption")
    monthly_consumption = st.number_input(
        "Monthly Consumption (kWh)",
        value=500.0,
        min_value=100.0,
        max_value=2000.0,
        step=50.0
    )

    pattern_type = st.selectbox(
        "Consumption Pattern",
        ["working_family", "home_office", "retired_couple", "large_family"]
    )

    # PV System inputs
    st.subheader("PV System")
    pv_enabled = st.checkbox("Enable PV System", value=True)

    if pv_enabled:
        pv_size = st.slider("PV Size (kWp)", 0.0, 20.0, 6.0, 0.5)
        location = st.selectbox("Location", list(LOCATIONS.keys()))
        tilt = st.slider("Panel Tilt (degrees)", 0, 90, 35)

    # Battery inputs
    st.subheader("Battery Storage")
    battery_enabled = st.checkbox("Enable Battery", value=True)

    if battery_enabled:
        battery_capacity = st.slider("Battery Capacity (kWh)", 0.0, 30.0, 10.0, 1.0)

# Main area - tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Scenarios", "📅 Daily Flow", "🎯 Optimization"])

with tab1:
    st.header("System Overview")

    # Create household profile
    household = HouseholdProfile(
        name="My Household",
        annual_consumption_kwh=monthly_consumption * 12,
        pattern_type=pattern_type
    )

    if pv_enabled:
        solar_system = SolarSystemProfile(
            name="My PV System",
            peak_power_kw=pv_size,
            location=LOCATIONS[location],
            tilt_angle=tilt
        )

        # Display key metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Annual Consumption", f"{household.annual_consumption_kwh:,.0f} kWh")

        with col2:
            annual_gen = solar_system.estimate_annual_generation()
            st.metric("Annual PV Generation", f"{annual_gen:,.0f} kWh")

        with col3:
            coverage = (annual_gen / household.annual_consumption_kwh * 100)
            st.metric("Coverage Ratio", f"{coverage:.1f}%")

with tab2:
    st.header("Scenario Comparison")

    if st.button("Calculate All Scenarios", type="primary"):
        with st.spinner("Calculating scenarios... This may take 30-60 seconds..."):
            # Run your existing calculation logic
            data = calculate_scenario_data(household, solar_system, battery_capacity)

        # Display results
        st.subheader("Annual Costs")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "No PV",
                f"€{data['scenario1_cost']:,.0f}",
                help="Baseline cost without any solar"
            )

        with col2:
            savings = data['scenario1_cost'] - data['scenario2_cost']
            st.metric(
                "PV Only",
                f"€{data['scenario2_cost']:,.0f}",
                f"-€{savings:,.0f}",
                delta_color="inverse"
            )

        with col3:
            savings = data['scenario1_cost'] - data['scenario3_cost']
            st.metric(
                "PV + Battery",
                f"€{data['scenario3_cost']:,.0f}",
                f"-€{savings:,.0f}",
                delta_color="inverse"
            )

        # Plotly chart for cost comparison
        fig = go.Figure(data=[
            go.Bar(name='Annual Cost', x=['No PV', 'PV Only', 'PV+Battery'],
                   y=[data['scenario1_cost'], data['scenario2_cost'], data['scenario3_cost']],
                   marker_color=['red', 'orange', 'green'])
        ])

        fig.update_layout(
            title="Annual Electricity Cost Comparison",
            yaxis_title="Cost (EUR/year)",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Daily Energy Flow")

    month = st.slider("Month", 1, 12, 6, format="Month %d")
    day_of_week = st.selectbox("Day of Week",
                                ["Monday", "Tuesday", "Wednesday", "Thursday",
                                 "Friday", "Saturday", "Sunday"])

    if st.button("Generate Daily Flow", type="primary"):
        # Generate your daily flow graph
        # Convert matplotlib to plotly for better web interaction
        pass

with tab4:
    st.header("🎯 System Optimization")

    st.info("Find the optimal PV and battery size for your needs!")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("PV Size Range")
        pv_min = st.number_input("Min PV (kWp)", 2.0, 15.0, 3.0)
        pv_max = st.number_input("Max PV (kWp)", 3.0, 30.0, 15.0)
        pv_step = st.number_input("Step (kWp)", 0.5, 2.0, 0.5)

    with col2:
        st.subheader("Battery Size Range")
        bat_min = st.number_input("Min Battery (kWh)", 0.0, 20.0, 0.0)
        bat_max = st.number_input("Max Battery (kWh)", 0.0, 50.0, 20.0)
        bat_step = st.number_input("Step (kWh)", 1.0, 5.0, 1.0)

    criterion = st.radio(
        "Optimization Goal",
        ["Best ROI", "Fastest Payback", "Highest Self-Sufficiency", "Balanced"]
    )

    if st.button("🚀 Run Optimization", type="primary"):
        st.warning("⏳ This will take 2-5 minutes depending on the range...")

        progress_bar = st.progress(0)
        status_text = st.empty()

        # Run optimization with progress updates
        # (Implementation needed)

        st.success("✅ Optimization complete!")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit | [View on GitHub](https://github.com/yourusername/PV_calculator)")
```

#### 3. Run Locally

```bash
streamlit run streamlit_app.py
```

Opens at `http://localhost:8501`

#### 4. Deploy to Streamlit Cloud (FREE)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub repo
4. Deploy (takes 2 minutes)
5. Get URL like: `https://yourusername-pv-calculator.streamlit.app`

**No configuration needed! Just works!**

---

## 🌐 Solution 2: GitHub Pages + Python Backend (More Complex)

If you specifically want GitHub Pages, you need a two-tier architecture:

### Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  GitHub Pages   │  HTTP   │   Python API     │
│  (HTML/JS/CSS)  │ ◄─────► │   (Flask/FastAPI)│
│  Frontend UI    │  HTTPS  │   Calculations   │
└─────────────────┘         └──────────────────┘
     Static Site            Heroku/Railway/PythonAnywhere
```

### Frontend (GitHub Pages)

Create `index.html`:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>PV Calculator</title>
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
  </head>
  <body>
    <div class="container mt-5">
      <h1>☀️ Solar PV Calculator</h1>

      <div class="row mt-4">
        <div class="col-md-4">
          <h3>Configuration</h3>
          <div class="mb-3">
            <label>Monthly Consumption (kWh)</label>
            <input
              type="number"
              class="form-control"
              id="consumption"
              value="500"
            />
          </div>
          <div class="mb-3">
            <label>PV Size (kWp)</label>
            <input type="number" class="form-control" id="pvSize" value="6" />
          </div>
          <div class="mb-3">
            <label>Battery Capacity (kWh)</label>
            <input type="number" class="form-control" id="battery" value="10" />
          </div>
          <button class="btn btn-primary" onclick="calculate()">
            Calculate
          </button>
        </div>

        <div class="col-md-8">
          <h3>Results</h3>
          <div id="results"></div>
          <div id="chart"></div>
        </div>
      </div>
    </div>

    <script>
      const API_URL = "https://your-backend.herokuapp.com"; // Your Python API

      async function calculate() {
        const data = {
          consumption: document.getElementById("consumption").value,
          pv_size: document.getElementById("pvSize").value,
          battery: document.getElementById("battery").value,
        };

        const response = await fetch(`${API_URL}/calculate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });

        const results = await response.json();

        // Display results
        document.getElementById("results").innerHTML = `
                <div class="alert alert-success">
                    <h4>Annual Savings: €${results.annual_savings.toFixed(
                      0
                    )}</h4>
                    <p>Payback Period: ${results.payback_years.toFixed(
                      1
                    )} years</p>
                    <p>Self-Sufficiency: ${results.self_sufficiency.toFixed(
                      1
                    )}%</p>
                </div>
            `;

        // Create chart
        Plotly.newPlot("chart", [
          {
            x: ["No PV", "PV Only", "PV+Battery"],
            y: [
              results.baseline_cost,
              results.pv_cost,
              results.pv_battery_cost,
            ],
            type: "bar",
          },
        ]);
      }
    </script>
  </body>
</html>
```

### Backend (Flask API)

Create `api.py`:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from PV_calculator import *

app = Flask(__name__)
CORS(app)  # Allow GitHub Pages to call this API

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json

    # Your existing calculation logic
    household = HouseholdProfile(
        annual_consumption_kwh=float(data['consumption']) * 12
    )

    solar_system = SolarSystemProfile(
        peak_power_kw=float(data['pv_size'])
    )

    # Calculate scenarios
    results = {
        'annual_savings': 950.0,
        'payback_years': 9.5,
        'self_sufficiency': 75.5,
        'baseline_cost': 2000,
        'pv_cost': 1200,
        'pv_battery_cost': 1050
    }

    return jsonify(results)

if __name__ == '__main__':
    app.run()
```

Deploy backend to:

- **Heroku** (free tier available)
- **Railway** (free tier)
- **PythonAnywhere** (free tier)
- **Render** (free tier)

Deploy frontend to GitHub Pages as usual.

---

## 🐍 Solution 3: PyScript (Experimental)

Run Python directly in browser using PyScript.

**Pros**: No backend needed
**Cons**: Very slow, limited libraries, experimental

Not recommended for production.

---

## 📊 Solution 4: Dash by Plotly

Similar to Streamlit, but more customizable.

```python
import dash
from dash import dcc, html, Input, Output

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("PV Calculator"),
    dcc.Slider(id='pv-size', min=0, max=20, value=6, step=0.5),
    html.Div(id='output')
])

@app.callback(
    Output('output', 'children'),
    Input('pv-size', 'value')
)
def update_output(pv_size):
    # Your calculation logic
    return f"PV Size: {pv_size} kWp"

if __name__ == '__main__':
    app.run_server(debug=True)
```

Deploy to Render or Heroku.

---

## 🎯 Recommended Path Forward

### For Quick Demo (1-2 days):

**Use Streamlit** - Easiest conversion, free hosting, professional look

### For Production App (1-2 weeks):

**GitHub Pages + Flask API** - Full control, scalable, can monetize

### For Maximum Performance (2-4 weeks):

**React Frontend + FastAPI Backend** - Modern, fast, best UX

---

## Comparison Table

| Solution         | Effort      | Hosting Cost | Performance | Customization |
| ---------------- | ----------- | ------------ | ----------- | ------------- |
| Streamlit        | ⭐ Low      | Free         | Good        | Medium        |
| GH Pages + Flask | ⭐⭐ Medium | Free         | Good        | High          |
| React + FastAPI  | ⭐⭐⭐ High | Free         | Excellent   | Maximum       |
| Dash             | ⭐⭐ Medium | Free         | Good        | High          |

---

## Next Steps

1. **Choose your approach** (I recommend Streamlit)
2. **Install dependencies**: `pip install streamlit plotly`
3. **Create `streamlit_app.py`** using the template above
4. **Test locally**: `streamlit run streamlit_app.py`
5. **Push to GitHub**
6. **Deploy to Streamlit Cloud** (free, 2-minute setup)

Would you like me to create a complete Streamlit conversion for you?
