# Quick Start: Battery SOC Continuity

## What's New? 🎉

Your PV Calculator now tracks battery charge **realistically across days**! 

Previously: Every day started at 50% battery charge (unrealistic)  
Now: Battery charge carries over from one day to the next (realistic!)

---

## How to Use It

### Step 1: Configure Your System
In the **Input Parameters** tab:
1. Set your monthly consumption
2. Enable and configure PV system
3. Enable and configure battery
4. Click "Refresh Configuration"

### Step 2: Select a Date
In the **Energy Flow Analysis** tab:
1. Click the date picker
2. Select any date from 2024 to 2030
3. See the day of the week

### Step 3: Generate Graph
1. Click **"Generate Daily Energy Flow"**
2. Wait a moment (first time may take a few seconds)
3. View the energy flow graph

### Step 4: Explore Different Days
- Try consecutive days to see battery charge evolution
- Compare winter (January) vs summer (June)
- Check weekdays vs weekends

---

## What You'll See

### Winter Days (Example: January)
```
Day 1: Battery starts at 5.0 kWh, ends at 1.8 kWh
Day 2: Battery starts at 1.8 kWh, ends at 1.0 kWh
Day 3: Battery starts at 1.0 kWh, ends at 1.0 kWh
```
**Insight**: Battery depletes in winter due to low solar generation

### Summer Days (Example: June)
```
Day 1: Battery starts at 5.0 kWh, ends at 8.8 kWh
Day 2: Battery starts at 8.8 kWh, ends at 8.8 kWh
Day 3: Battery starts at 8.8 kWh, ends at 8.8 kWh
```
**Insight**: Battery stays full in summer due to high solar generation

---

## Quick Tips

### 💡 Tip 1: Start with January 1st
- This day always starts at 50% battery charge
- Good baseline for comparison

### 💡 Tip 2: View Consecutive Days
- Select Jan 1, then Jan 2, then Jan 3
- Watch how battery charge evolves
- Identify patterns

### 💡 Tip 3: Compare Seasons
- View a Monday in January
- View a Monday in June
- See the dramatic difference!

### 💡 Tip 4: Check Weekends
- Weekends have different consumption patterns
- Battery behavior changes accordingly
- Compare Saturday vs Monday

### 💡 Tip 5: Refresh After Changes
- Changed battery size? Click "Refresh Configuration"
- This ensures accurate simulation
- Cache is automatically cleared

---

## Common Questions

### Q: Why does it take a few seconds the first time?
**A**: The system simulates all days from January 1st to your selected date. After that, it's instant (cached).

### Q: Why is my battery starting at 30% instead of 50%?
**A**: Because the previous day ended at 30%! This is realistic. To see 50% start, view January 1st.

### Q: My battery is always at minimum in winter. Is that normal?
**A**: Yes! This means your battery is too small for winter consumption, or your solar system is undersized. Try increasing battery or solar capacity.

### Q: My battery is always full in summer. Is that normal?
**A**: Yes! This means you have excess solar generation. You're exporting a lot to the grid. Consider if a smaller battery would be more cost-effective.

### Q: Results changed after I modified settings. Why?
**A**: The cache was automatically cleared to reflect your new configuration. This is expected and ensures accuracy.

---

## Example Workflow: Battery Sizing

**Goal**: Determine optimal battery size for your home

### Step 1: Try 5 kWh Battery
1. Set battery capacity to 5 kWh
2. View January 15-20 (winter week)
3. Observe: Battery hits minimum every day
4. **Conclusion**: Too small

### Step 2: Try 10 kWh Battery
1. Set battery capacity to 10 kWh
2. Click "Refresh Configuration"
3. View January 15-20 again
4. Observe: Battery fluctuates 20-60%
5. **Conclusion**: Good size

### Step 3: Try 15 kWh Battery
1. Set battery capacity to 15 kWh
2. Click "Refresh Configuration"
3. View January 15-20 again
4. Observe: Battery never drops below 50%
5. **Conclusion**: Possibly oversized

### Step 4: Verify in Summer
1. Keep 10 kWh battery
2. View June 15-20
3. Observe: Battery stays 80-100%
4. **Conclusion**: 10 kWh is optimal

---

## Troubleshooting

### Issue: "Takes forever to load"
**Solution**: You're viewing a day late in the year (e.g., December). First time takes 15-20 seconds. After that, instant.

### Issue: "Battery SOC looks wrong"
**Solution**: Click "Refresh Configuration" to clear cache and recalculate.

### Issue: "Different from before"
**Solution**: This is expected! The new system is more realistic. Old system always started at 50%.

---

## Learn More

- **Full Documentation**: See `SOC_CONTINUITY_FEATURE.md`
- **Technical Details**: See `BATTERY_FLOW_IMPROVEMENTS.md`
- **Update Summary**: See `UPDATE_SUMMARY_v2.7.md`

---

## Need Help?

If you encounter issues:
1. Click "Refresh Configuration"
2. Try viewing January 1st first
3. Check that all parameters are filled in
4. Restart the application if needed

---

**Enjoy realistic battery simulations! 🔋⚡**

