# PV Calculator - Graphs Quick Reference Guide

## Installation

Before using the graphing features, install required packages:

```bash
pip install matplotlib numpy
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

## Using Graphs in the GUI

1. **Launch the GUI**:

   ```bash
   python PV_calculator_gui.py
   ```

2. **Enter your parameters** in the "Input Parameters" tab

3. **Click "Calculate"** to run the analysis

4. **Go to the "Graphs" tab** where you'll find 5 buttons:

### Available Graph Types

#### 1. Break-Even Analysis 📈

**Shows:** When your PV investment pays for itself

**What you'll see:**

- **Cumulative Cash Flow Chart**: Starts negative (your investment), rises over time
  - The point where the line crosses zero = break-even
  - Marked with a dot and annotation showing exact year
  - Green shaded area = profit region
  - Accounts for all costs including battery replacements
- **Annual Operational Savings Chart**: Year-by-year ongoing savings
  - Shows smooth decline due to degradation (typically ~0.5%/year)
  - Red X markers indicate when battery replacements occur
  - Annotations show the cost of battery replacement
  - The curve itself shows your regular annual savings (without one-time costs)

**Use this to:**

- Understand how long until you're in profit
- See the impact of system degradation over time
- Identify when battery replacements are needed
- Distinguish between ongoing savings and one-time replacement costs

---

#### 2. Cost Comparison 💰

**Shows:** Annual electricity costs compared side-by-side

**What you'll see:**

- Three bars: Current (no PV), PV Only, PV + Battery
- Exact annual cost on each bar
- Savings amount and percentage shown

**Use this to:** Quickly see potential annual savings

---

#### 3. Energy Flow 🔋

**Shows:** Where your energy comes from and goes to

**What you'll see:**

- Two scenarios side-by-side (with/without battery)
- Stacked bars showing:
  - **Consumption Sources**: How much from PV vs. Grid
  - **PV Production Use**: How much you use vs. sell
- Self-sufficiency percentage

**Use this to:** Understand your energy independence level

---

#### 4. ROI Comparison 📊

**Shows:** Return on investment metrics

**What you'll see:**

- **Pie Chart**: Investment breakdown (PV vs. Battery costs)
- **Bar Chart**: Payback periods
  - Green line at 10 years = "Excellent"
  - Orange line at 15 years = "Good"

**Use this to:** Evaluate if the investment makes financial sense

---

#### 5. Generate All Graphs 🎨

**Does:** Creates all 4 graphs above at once and saves them as PNG files

**Files created:**

- `PV_Analysis_breakeven_YYYYMMDD_HHMMSS.png`
- `PV_Analysis_cost_comparison_YYYYMMDD_HHMMSS.png`
- `PV_Analysis_energy_flow_YYYYMMDD_HHMMSS.png`
- `PV_Analysis_roi_comparison_YYYYMMDD_HHMMSS.png`

**Use this to:** Create a complete visual report you can share or print

---

## Using Graphs from Command Line

Run the standalone graph generator:

```bash
python PV_calculator_graphs.py
```

This uses example values and generates all 4 graphs.

To customize, edit the `main()` function in `PV_calculator_graphs.py`.

---

## Understanding the Break-Even Point

### What is Break-Even?

The break-even point is when your **cumulative savings equal your initial investment**.

**Example:**

- You invest €10,000 in a PV system
- You save €1,200/year on electricity
- Break-even occurs at ~8.3 years
- After that, it's all profit!

### Good Break-Even Times

| Payback Period | Assessment     | Notes                                          |
| -------------- | -------------- | ---------------------------------------------- |
| < 8 years      | **Excellent**  | Very attractive investment                     |
| 8-12 years     | **Good**       | Solid investment for most people               |
| 12-15 years    | **Acceptable** | Consider if motivated by sustainability        |
| > 15 years     | **Marginal**   | May want to reconsider or optimize system size |

### Factors Affecting Break-Even

✅ **Faster Payback:**

- High electricity prices
- Good solar irradiance location
- High self-consumption (using energy when produced)
- Lower installation costs
- Government subsidies

❌ **Slower Payback:**

- Low electricity prices
- Poor solar conditions
- High installation costs
- Oversized system (too much excess energy)
- Expensive battery (if not well-matched to usage)

---

## Reading the Graphs

### Break-Even Analysis Graph

```
Cumulative Cash Flow
  €
  ^
  |         ╱╱╱╱╱╱ (Profit region)
0 |-------●------------ (Break-even point)
  |     ╱
  |   ╱
  | ╱ (Investment recovery)
-10k|●
  └─────────────────> Years
    0  5  10  15  20
```

**Key Points:**

- Starts at negative (your investment)
- Slope = annual savings
- Crosses zero = break-even
- Continues up = cumulative profit

### Cost Comparison Graph

```
Annual Cost (€)
  ^
  |  ████
  |  ████
  |  ████  ███
  |  ████  ███  ██
  └──────────────────
     Now   PV   PV+Bat
```

**Lower bars = better!**

---

## Tips for Better Results

### 1. Optimize System Size

- Don't oversize! Aim for 80-100% of annual consumption
- Excess energy sells for less than you save by self-consuming

### 2. Battery Decision

- Check if battery significantly improves payback
- Often battery adds 3-5 years to payback period
- Most economical when:
  - High daytime production
  - High evening consumption
  - Large gap between retail and export prices

### 3. Maximize Self-Consumption

- Run appliances during sunny hours
- Charge electric vehicles during day
- Use timers for water heaters, washing machines
- This improves economics more than adding battery!

### 4. Get Multiple Quotes

- Installation costs vary dramatically
- Lower cost = faster payback
- Same quality can cost ±30% depending on installer

---

## Troubleshooting

### "Graphing functionality not available"

**Solution:** Install matplotlib and numpy

```bash
pip install matplotlib numpy
```

### Graphs don't match my expectations

**Check:**

- ☑ Entered correct monthly consumption (not annual!)
- ☑ Solar irradiance matches your location
- ☑ PV system size is realistic (5-8 kWp typical for homes)
- ☑ Installation cost is reasonable (€1,200-1,500 per kWp)

### Break-even never reached

**Possible reasons:**

- System too expensive for the savings
- System oversized for consumption
- Very low electricity prices
- **Try:** Reduce system size or installation cost

### Why do I see red X markers on the savings chart?

**These mark battery replacement years.**

- By default, batteries need replacement every 10 years
- The red markers show when this happens
- The annotation shows the replacement cost
- The **cumulative cash flow** chart accounts for these costs
- The **annual savings** chart shows smooth operational savings (the curve) plus markers for one-time costs

### Battery seems not worth it

**This is common!** Batteries often:

- Add significant cost
- Provide limited additional benefit
- Have shorter lifetime than PV panels
- **Consider:** Start without battery, add later if needed

---

## Export and Share

### From GUI:

1. Click "Generate All Graphs"
2. Graphs saved as PNG files in current directory
3. Share these with family, installers, or financial advisors

### High-Quality Exports:

Graphs are saved at 300 DPI - suitable for:

- Printing
- Presentations
- Grant applications
- Sharing with installers

---

## Advanced: Customizing Graphs

All graph functions are in `PV_calculator_graphs.py`.

You can modify:

- Colors: Change hex codes in plotting functions
- Time periods: Adjust `years` parameter (default: 25)
- Chart types: Modify matplotlib parameters
- Additional metrics: Add your own calculations

**Example:** Change break-even graph to 30 years:

```python
graph_gen.calculate_cashflow_over_time(with_battery=False, years=30)
```

---

## Quick Start Checklist

- [ ] Install matplotlib and numpy
- [ ] Run `python PV_calculator_gui.py`
- [ ] Enter your electricity costs
- [ ] Enter your consumption
- [ ] Enter PV system specs (or get quote first)
- [ ] Click "Calculate"
- [ ] Go to "Graphs" tab
- [ ] Click "Generate All Graphs"
- [ ] Review break-even point
- [ ] Check if battery is worth it
- [ ] Save graphs for reference
- [ ] Make informed decision!

---

## Need Help?

1. **Check the main README** for parameter explanations
2. **Review example scenarios** for realistic values
3. **Try the default values** first to understand output
4. **Compare multiple scenarios** (different system sizes)
5. **Get professional quotes** for accurate cost data

---

**Remember:** These graphs are for planning purposes. Actual results depend on many factors including weather, consumption patterns, and electricity price changes. Use them as a guide, not a guarantee!

---

_Last Updated: October 2025_
_Version: 1.0_
