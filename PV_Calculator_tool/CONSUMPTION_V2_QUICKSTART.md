# Consumption Pattern Generator V2 - Quick Start

## 🚀 Quick Start (2 Minutes)

### Launch the GUI
```bash
cd PV_Calculator_tool
python PV_calculator_gui.py
```

### Select the V2 Tab
Click on **"⭐ Consumption Patterns V2"** tab

### Configure (30 seconds)
1. **Pattern Type**: "Working Family" (default)
2. **Annual Consumption**: 6000 kWh (typical household)
3. **Seasonal Strength**: 0.6 (moderate seasonal variation)
4. **Peak Hour**: 19:00 (7 PM)

### Generate Graph (10 seconds)
Click **"Daily Pattern Comparison"** button

### 🎉 Done!
You now see your consumption pattern visualization!

---

## 📊 What Each Graph Shows

### 1. Daily Pattern Comparison
**What**: Weekday vs weekend, winter vs summer  
**Use for**: Understanding when you consume most electricity  
**Time**: 2 seconds

### 2. Seasonal Variation  
**What**: Monthly consumption with Gaussian curve  
**Use for**: Planning for seasonal changes  
**Time**: 2 seconds

### 3. Weekly Heatmap
**What**: 24h × 7 days consumption intensity  
**Use for**: Identifying optimal times for high-power activities  
**Time**: 2 seconds

### 4. Pattern Comparison
**What**: Compare 4 different household types  
**Use for**: Finding which pattern matches you best  
**Time**: 3 seconds

### 5. Annual Overview
**What**: Complete year analysis with statistics  
**Use for**: Comprehensive understanding  
**Time**: 5 seconds (generates 365 days)

---

## 💡 Most Common Scenarios

### Scenario: "I want to size my solar panels"
1. Set your **annual consumption**
2. Click **"Daily Pattern Comparison"**
3. Note your **evening peak** (when sun is down)
4. Click **"Seasonal Variation"**
5. See **winter vs summer** consumption
6. ➡️ **Action**: Size solar to cover summer, battery for evening

### Scenario: "I need a battery, what size?"
1. Click **"Weekly Heatmap"** for January
2. Find **evening hours** (18:00-22:00)
3. Note consumption values (typically 2-3 kWh/hour)
4. Multiply by 4-5 hours
5. ➡️ **Action**: Battery capacity = 10-15 kWh

### Scenario: "Is solar worth it for my household type?"
1. Try different **pattern types**
2. Click **"Pattern Comparison"**
3. See which matches your lifestyle
4. Generate **"Annual Overview"**
5. ➡️ **Action**: Use annual total in V1 calculator

---

## 🎯 Best Practices

### ✅ Do:
- Use your **actual annual consumption** from bills
- Try **different pattern types** to find your match
- Generate **"Generate All V2 Graphs"** for complete analysis
- Save the PNG files for your solar installer

### ❌ Don't:
- Don't use default values without checking
- Don't ignore weekend vs weekday differences
- Don't forget seasonal variation in winter

---

## 🔧 Common Issues

**Q: Annual total doesn't match exactly?**  
A: Normal. Within 2-3% is fine due to weekend distribution.

**Q: My pattern doesn't match any type?**  
A: Use closest match and adjust seasonal strength.

**Q: Graphs not showing?**  
A: Install matplotlib: `pip install matplotlib numpy`

---

## 📈 Example: Real Family Scenario

**Family**: 2 adults + 2 kids, both parents work outside home  
**Annual**: 7,200 kWh from electricity bill  
**Pattern**: "Working Family"  
**Seasonal**: 0.7 (electric heating)  
**Peak**: 19:00 (dinner + evening activities)

**Result**:
- January daily: 31 kWh/day (winter peak)
- July daily: 9 kWh/day (summer low)
- Evening peak: 3.5 kWh/hour at 19:00
- **Recommendation**: 6 kWp solar + 12 kWh battery

---

## 📞 Next Steps

1. ✅ Run test: `python test_consumption_v2.py`
2. ✅ Open GUI and explore patterns
3. ✅ Generate your consumption graphs
4. ✅ Use insights in V1 calculator for ROI analysis
5. ✅ Share graphs with solar installer

---

## 📚 Full Documentation

For complete details, see: `CONSUMPTION_V2_USER_GUIDE.md`

---

**Ready to start?** Just run `python PV_calculator_gui.py` and click the ⭐ tab!

