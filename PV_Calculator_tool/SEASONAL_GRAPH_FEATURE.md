# Monthly Seasonal Analysis Graph - New Feature

## Overview

A new comprehensive graph has been added to visualize **monthly PV generation and consumption patterns** throughout the year. This graph clearly shows the dramatic differences between winter and summer solar production.

## 📊 What the Graph Shows

The graph consists of **two panels**:

### Panel 1: Monthly Energy Production vs Consumption

**Side-by-side bar chart showing:**

- 🟠 **PV Production** (orange bars) - Monthly solar energy generated
- 🔵 **Household Consumption** (blue bars) - Monthly household electricity use
- 🟣 **EV Charging** (purple stacked bars) - Additional EV consumption if enabled

**Visual highlights:**

- 🔵 Blue shaded area = Winter months (Dec-Feb) - Low solar production
- 🟡 Yellow shaded area = Summer months (Jun-Aug) - Peak solar production
- Annotations marking the lowest winter and highest summer production

### Panel 2: Monthly Self-Sufficiency Ratio

**Line graph with area fill showing:**

- Self-sufficiency percentage by month (PV production / household consumption)
- Clear visualization of which months you're most/least self-sufficient
- 100% reference line (green dashed)
- Seasonal shading (winter/summer)

**Statistics box shows:**

- Annual average self-sufficiency
- Winter average (Dec-Feb)
- Summer average (Jun-Aug)

## 🎯 Why This Graph is Important

### 1. **Reveals Seasonal Reality**

- Winter production can be 5-10x lower than summer
- Average annual values hide this critical variation
- Shows if you'll need grid power in winter even with oversized system

### 2. **Sizing Decisions**

- See if your system is too small (low summer production)
- Or too large (excess in summer but still dependent in winter)
- Understand the trade-offs of different system sizes

### 3. **Battery Planning**

- Shows monthly consumption patterns
- Helps determine if battery can cover evening peaks year-round
- Reveals months where battery is most/least useful

### 4. **EV Integration**

- If EV charging is enabled, see stacked bars showing total load
- Understand how EV affects self-sufficiency throughout the year
- Plan for grid dependence in winter months

### 5. **Financial Reality**

- Higher grid dependence in winter = higher costs those months
- Self-sufficiency percentage directly impacts annual savings
- More accurate payback period expectations

## 🖥️ How to Use in GUI

### Access the Graph:

1. **Calculate your scenario** first (click "Calculate" or "Compare Scenarios")
2. Go to the **"Graphs"** tab
3. Click **"Monthly Seasonal Analysis"** button
4. Or click **"Generate All Graphs"** to create all graphs including this one

### What You'll See:

```
┌─────────────────────────────────────────┐
│  Monthly Energy Production vs Consumption│
│                                         │
│  [Bar Chart: PV vs Consumption]        │
│  - Orange bars: PV Production          │
│  - Blue bars: Household Use            │
│  - Purple bars: EV (if enabled)        │
│  - Winter/Summer shaded regions        │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Monthly Self-Sufficiency Ratio         │
│                                         │
│  [Line Graph with % values]             │
│  - Shows self-sufficiency by month     │
│  - Statistics: Annual, Winter, Summer  │
│  - 100% reference line                 │
└─────────────────────────────────────────┘
```

## 📈 Example Insights

### Typical Central Europe (3.5 kWh/m²/day average):

**January (Winter Low):**

- PV Production: ~120 kWh/month
- Household: ~500 kWh/month
- Self-Sufficiency: ~24%
- **Insight:** Heavy grid dependence in winter

**June (Summer Peak):**

- PV Production: ~650 kWh/month
- Household: ~500 kWh/month
- Self-Sufficiency: ~100%+ (excess to grid)
- **Insight:** Fully self-sufficient, selling excess

**Annual Average:**

- Self-Sufficiency: ~65%
- But this hides the 24% (winter) to 100%+ (summer) variation!

## 🔍 Key Takeaways from This Graph

1. **No Single Number Tells the Story**

   - Annual averages are misleading
   - Seasonal variations are extreme in most climates
   - Monthly analysis is essential for realistic expectations

2. **Winter is the Challenge**

   - Even oversized systems struggle in winter
   - Battery can't solve seasonal (only daily) variations
   - Grid dependence in winter is inevitable in most climates

3. **Summer Excess Doesn't Equal Year-Round Coverage**

   - Selling excess in summer at €0.06/kWh
   - Buying in winter at €0.15+/kWh
   - Net result: still paying for electricity year-round

4. **System Sizing Strategy**
   - Size for average needs (not winter) to avoid excessive summer waste
   - Accept grid dependence in winter
   - Focus on maximizing summer self-consumption

## 📁 File Output

When saved, the graph is named:

```
PV_Analysis_monthly_seasonal_YYYYMMDD_HHMMSS.png
```

High resolution (300 DPI) suitable for:

- Reports and presentations
- Sharing with installers
- Investment decision documentation
- Long-term reference

## 🔧 Technical Details

### Data Sources:

- PV production uses realistic monthly irradiance factors
- Based on Central/Northern Europe patterns by default
- Consumption includes seasonal variations (10% higher in winter)
- EV consumption assumed constant year-round

### Calculations:

- Self-sufficiency = min(100%, PV_production / Household_consumption \* 100%)
- Monthly values calculated with actual days per month
- Winter average: Dec, Jan, Feb
- Summer average: Jun, Jul, Aug

## 💡 Tips for Interpretation

### If self-sufficiency is...

**Below 30% in winter:**

- System may be undersized
- Or completely normal for northern climates
- Battery won't help with this (seasonal issue, not daily)

**Above 100% in summer:**

- Good sign! Selling excess to grid
- Consider if more panels would just create more excess
- Check if Nord Pool prices make excess worthwhile

**Annual average above 70%:**

- Excellent system performance
- Good investment
- Realistic expectations for grid use

**Wide variation (20% winter, 120% summer):**

- Normal for solar! This is expected
- Shows why battery alone doesn't solve grid dependence
- Highlights need for grid connection year-round

## 🎨 Graph Features

- **Professional styling** with color-coded energy types
- **Clear annotations** for key data points
- **Seasonal shading** to highlight winter/summer periods
- **Statistics box** with annual and seasonal averages
- **Value labels** on all bars and points
- **Grid lines** for easy reading
- **High-resolution** output for printing/presentations

---

## Summary

This graph is essential for understanding the **reality of solar power** in seasonal climates. It clearly shows:

✅ When you'll be self-sufficient (summer)  
✅ When you'll need the grid (winter)  
✅ How much excess you'll produce (summer)  
✅ Whether your system size is appropriate  
✅ Realistic expectations for annual savings

**Don't make PV investment decisions without viewing this graph!** 🌞❄️

---

**Added**: October 2025  
**Version**: 2.4 (PyQt5 with Monthly Seasonal Analysis)
