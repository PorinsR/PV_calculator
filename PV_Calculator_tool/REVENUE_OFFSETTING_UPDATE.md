# Revenue Offsetting & EV Self-Sufficiency Update

## Overview

Two major improvements have been made to provide more accurate and comprehensive analysis:

1. **EV-Inclusive Self-Sufficiency Calculation** - Self-sufficiency now includes EV consumption
2. **Monthly Revenue Offsetting Graph** - New visualization showing how summer revenue offsets winter costs

---

## 1. ✅ EV-Inclusive Self-Sufficiency

### What Changed

**Previous Behavior:**

- Self-sufficiency calculated as: `PV Production / Household Consumption`
- EV consumption was excluded from the calculation
- Graph title: "Monthly Self-Sufficiency Ratio (Household Only)"

**New Behavior:**

- Self-sufficiency calculated as: `PV Production / (Household + EV Consumption)`
- EV consumption now included in total consumption
- Graph title dynamically changes:
  - "Monthly Self-Sufficiency Ratio (Household Only)" - when no EV
  - "Monthly Self-Sufficiency Ratio (Including EV)" - when EV enabled

### Why This Matters

**More Realistic Assessment:**

- If you have an EV consuming 450 kWh/month, it's a significant part of your total load
- Previous calculation overstated self-sufficiency by ignoring EV
- New calculation shows **actual** percentage of total consumption covered by PV

**Example Impact:**

```
System: 6 kWp PV producing 600 kWh/month in summer
Household: 500 kWh/month
EV: 450 kWh/month

OLD Calculation:
Self-Sufficiency = 600 / 500 = 120% (overstated)

NEW Calculation:
Self-Sufficiency = 600 / (500 + 450) = 63% (realistic)
```

### Visual Changes

The graph now clearly indicates whether EV is included:

- Orange bars: PV Production
- Blue bars: Household Consumption
- Purple stacked bars: EV Charging (when enabled)
- Self-sufficiency line: Calculated against **total** (blue + purple)

---

## 2. 🆕 Monthly Revenue Offsetting Graph

### What It Shows

A new comprehensive graph demonstrating how **summer export revenue offsets winter import costs**.

### Two-Panel Visualization

#### Panel 1: Monthly Grid Costs vs Export Revenue

**Shows:**

- 🔴 Red bars (upward): Grid import costs each month
- 🟢 Green bars (downward): Export revenue earned each month
- Gray dashed line: Monthly fixed costs
- Blue/yellow shading: Winter/summer periods

**Key insights:**

- Which months you're buying electricity (winter)
- Which months you're selling electricity (summer)
- Peak import and export months highlighted with annotations

#### Panel 2: Net Cost with Cumulative Balance

**Shows:**

- Bar chart: Net monthly cost (red = paying, green = earning)
- Blue line: Cumulative balance over the year
- Shows how summer credits accumulate and offset winter deficits

**Key insights:**

- Monthly cash flow (positive or negative)
- Year-round balance tracking
- Whether summer revenue fully covers winter costs
- Net annual electricity cost after all offsetting

### The Revenue Offsetting Concept

**How It Works:**

1. **Summer Months (May-August):**

   - PV produces MORE than you consume
   - Excess energy sold to grid at Nord Pool price (e.g., €0.06/kWh)
   - Earn revenue (shown as negative cost)

2. **Winter Months (November-February):**

   - PV produces LESS than you consume
   - Import energy from grid at retail price (e.g., €0.15/kWh)
   - Pay for imports

3. **Net Effect:**
   - Summer revenue = credit that offsets winter costs
   - Annual cost = Winter imports - Summer exports + Fixed costs
   - Graph shows this month-by-month

### Example Scenario

```
Month    | PV    | Consumption | Balance | Cost/Revenue
---------|-------|-------------|---------|-------------
January  | 120   | 500         | -380    | €60 (import)
February | 150   | 500         | -350    | €55 (import)
...
June     | 650   | 500         | +150    | -€9 (revenue)
July     | 650   | 500         | +150    | -€9 (revenue)
...
December | 100   | 500         | -400    | €63 (import)
---------|-------|-------------|---------|-------------
Annual   | 5200  | 6000        | -800    | €450 net cost
```

**The graph shows:**

- Import cost: €600 (winter months)
- Export revenue: €150 (summer months)
- Fixed costs: €200
- **Net annual: €650**

### Summary Statistics Box

Each graph includes a summary showing:

- **Import Cost**: Total spent buying from grid
- **Export Revenue**: Total earned selling to grid
- **Fixed Costs**: Annual connection and service fees
- **Net Annual**: Final yearly cost after all offsetting

### Why This Graph is Critical

1. **Price Asymmetry Reality**

   - Buying: €0.15/kWh
   - Selling: €0.06/kWh
   - You need to sell 2.5x more than you buy to break even!

2. **Seasonal Cash Flow**

   - See monthly payment patterns
   - Plan for high-cost winter months
   - Understand summer "earnings"

3. **Investment Validation**

   - Does summer revenue meaningfully offset winter costs?
   - Is the price asymmetry too severe?
   - Are fixed costs eating into savings?

4. **System Sizing Decisions**
   - Oversized system = more summer excess at low price
   - Undersized system = expensive winter imports
   - Sweet spot = maximize self-consumption, minimize excess

---

## Technical Details

### Self-Sufficiency Calculation

**Code Location:** `PV_calculator_graphs.py` - `plot_monthly_seasonal_analysis()`

```python
# Total consumption includes both household and EV
total_consumption_month = household_month + ev_monthly[-1]
if total_consumption_month > 0:
    self_suff = min(100, (pv_month / total_consumption_month) * 100)
```

### Monthly Revenue Calculation

**Code Location:** `PV_calculator_graphs.py` - `calculate_monthly_costs_with_revenue()`

```python
# Calculate energy balance
energy_balance = pv_monthly - total_consumption

if energy_balance >= 0:
    # Surplus month - selling to grid
    excess_to_grid = energy_balance
    export_revenue = excess_to_grid * selling_price
    net_cost = -export_revenue + monthly_fixed
else:
    # Deficit month - buying from grid
    grid_import = -energy_balance
    import_cost = grid_import * total_cost_per_kwh
    net_cost = import_cost + monthly_fixed
```

### Cumulative Balance Tracking

```python
cumulative += (export_revenue - import_cost - monthly_fixed)
```

This shows running total: positive = net revenue, negative = net cost.

---

## How to Use

### In GUI:

1. Enter your parameters and click **"Calculate"**
2. Go to **"Graphs"** tab
3. Click one of:
   - **"Monthly Seasonal Analysis"** - See EV-inclusive self-sufficiency
   - **"Monthly Revenue Offsetting"** - See summer credits vs winter costs
4. Or click **"Generate All Graphs"** to create all visualizations

### Files Created:

- `PV_Analysis_monthly_seasonal_YYYYMMDD_HHMMSS.png` - Updated with EV self-sufficiency
- `PV_Analysis_monthly_revenue_offsetting_YYYYMMDD_HHMMSS.png` - New revenue graph

---

## Interpretation Guide

### Self-Sufficiency Values

**If self-sufficiency WITH EV is:**

- **Below 50%**: PV system undersized for your total load (household + EV)
- **50-70%**: Good balance, realistic for most climates
- **70-90%**: Excellent coverage, well-sized system
- **Above 100% (summer)**: Excess production, earning revenue

### Revenue Offsetting Insights

**Cumulative Balance Line:**

- **Ends positive**: Summer revenue exceeded winter costs (rare)
- **Ends near zero**: Revenue almost covered costs (excellent)
- **Ends negative**: Still paying annually, but less than without PV

**Net Monthly Cost Bars:**

- **Green (negative)**: Earning money that month
- **Red (positive)**: Paying for electricity
- **Height**: Magnitude of cost or revenue

---

## Real-World Impact Examples

### Example 1: Well-Balanced System

```
Configuration:
- 6 kWp PV system
- 500 kWh/month household
- 450 kWh/month EV
- Central Europe (3.5 kWh/m²/day)

Results:
- Self-sufficiency (with EV): 58% annual average
- Summer revenue: €120
- Winter import costs: €480
- Net annual cost: €560
- Savings vs no PV: €900/year (62% reduction)
```

### Example 2: Oversized System

```
Configuration:
- 10 kWp PV system
- 500 kWh/month household
- No EV
- Central Europe

Results:
- Self-sufficiency (household): 95% annual average
- Summer revenue: €280 (lots of excess)
- Winter import costs: €180
- But: Revenue at €0.06/kWh, imports at €0.15/kWh
- Price asymmetry limits benefit of excess
```

### Example 3: Undersized with EV

```
Configuration:
- 4 kWp PV system
- 500 kWh/month household
- 450 kWh/month EV
- Central Europe

Results:
- Self-sufficiency (with EV): 42% annual average
- Summer revenue: €0 (no excess)
- Winter import costs: €720
- Heavy grid dependence
- May need larger system for future-proofing
```

---

## Key Takeaways

### 1. EV Impact is Significant

- Adding EV can reduce self-sufficiency by 20-40 percentage points
- Must be included in calculations for realistic assessment
- Graph now shows true total energy independence

### 2. Revenue Offsetting Has Limits

- Price asymmetry (buying €0.15, selling €0.06) heavily favors utilities
- Summer excess doesn't fully offset winter imports
- Focus on maximizing self-consumption, not oversizing for exports

### 3. Fixed Costs Matter

- Monthly connection fees continue regardless of usage
- Can be significant portion of annual costs
- Shows why going fully off-grid is challenging

### 4. Sweet Spot Sizing

- Aim for high summer self-consumption without excessive export
- Accept winter grid dependence (it's inevitable in most climates)
- Balance investment cost vs. realistic savings

---

## Summary

These updates provide a **more accurate and complete picture** of PV system economics:

✅ **Self-sufficiency** now includes EV for realistic total energy independence assessment  
✅ **Revenue offsetting** clearly shows how summer credits offset winter costs  
✅ **Monthly breakdown** reveals cash flow patterns throughout the year  
✅ **Price asymmetry** impact is visualized and quantified  
✅ **Investment validation** based on real annual net costs, not just peak production

**Make informed decisions with complete data!** 💡

---

**Updated**: October 2025  
**Version**: 2.5 (Revenue Offsetting & EV Self-Sufficiency)
