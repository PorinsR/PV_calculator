# PV System Optimization Feature - Implementation Plan

## Overview

Automated optimization tool to find the optimal PV and battery configuration based on user-defined criteria.

## Goals

Find the best system sizing that maximizes:

1. **ROI (Return on Investment)** - Total profit over system lifetime
2. **Payback Speed** - Fastest time to recover initial investment
3. **Self-Sufficiency** - Highest percentage of energy independence
4. **Cost/Benefit Ratio** - Best value for money

## Algorithm Design

### Input Parameters

- **PV Size Range**: Min/Max kWp (e.g., 3-15 kWp, step 0.5 kWp)
- **Battery Size Range**: Min/Max kWh (e.g., 0-20 kWh, step 1 kWh)
- **Optimization Criterion**: ROI, Payback, Self-Sufficiency, or Balanced
- **Budget Constraint** (optional): Maximum investment amount
- **Time Horizon**: Analysis period (default: 25 years for PV lifetime)

### Search Strategy

#### Option 1: Grid Search (Simple, Comprehensive)

```python
for pv_size in range(min_pv, max_pv, step_pv):
    for battery_size in range(min_battery, max_battery, step_battery):
        # Calculate full year simulation
        result = simulate_scenario(pv_size, battery_size)

        # Score based on optimization criterion
        score = calculate_score(result, criterion)

        # Track best configuration
        if score > best_score:
            best_config = (pv_size, battery_size)
            best_score = score
```

**Pros**:

- Simple to implement
- Guaranteed to find global optimum within grid
- Can visualize entire solution space

**Cons**:

- Computationally expensive (N_pv × N_battery simulations)
- Example: 25 PV sizes × 20 battery sizes = 500 full-year simulations

#### Option 2: Coarse-to-Fine Search (Faster)

```python
# Stage 1: Coarse grid (large steps)
coarse_best = grid_search(min_pv, max_pv, step=2.0,
                          min_battery, max_battery, step=5.0)

# Stage 2: Fine grid around best (small steps)
fine_best = grid_search(coarse_best_pv - 2, coarse_best_pv + 2, step=0.5,
                        coarse_best_battery - 5, coarse_best_battery + 5, step=1.0)
```

**Pros**:

- Much faster (e.g., 50 + 50 = 100 simulations vs 500)
- Still thorough

**Cons**:

- Might miss global optimum if solution space is multimodal

#### Option 3: Gradient-Based (Advanced)

Use scipy.optimize with intelligent starting points and constraints.

**Pros**:

- Very fast convergence
- Handles constraints elegantly

**Cons**:

- May get stuck in local optima
- Requires differentiable objective function (or numerical gradients)

### Recommended: Hybrid Approach

1. **Coarse grid search** to identify promising regions
2. **Fine grid search** around top 3 candidates
3. Display **all Pareto-optimal solutions** (trade-off frontier)

## Scoring Functions

### 1. ROI Optimization

```python
def score_roi(result):
    """Maximize total profit over system lifetime"""
    total_savings = sum(annual_savings[year] * degradation_factor[year]
                       for year in range(lifetime))
    total_cost = pv_cost + battery_cost
    roi = (total_savings - total_cost) / total_cost * 100
    return roi
```

### 2. Payback Optimization

```python
def score_payback(result):
    """Minimize payback period (invert for maximization)"""
    payback_years = total_cost / annual_savings
    # Return negative payback (lower is better becomes higher is better)
    return -payback_years
```

### 3. Self-Sufficiency Optimization

```python
def score_self_sufficiency(result):
    """Maximize energy independence percentage"""
    return result.self_sufficiency_percentage
```

### 4. Balanced Score (Multi-Objective)

```python
def score_balanced(result):
    """Weighted combination of all factors"""
    # Normalize each metric to 0-100 scale
    roi_norm = normalize(result.roi, min_roi=0, max_roi=200)
    payback_norm = normalize(15 - result.payback_years, min=0, max=15)
    ss_norm = result.self_sufficiency_percentage

    # Weighted combination (user-configurable)
    weights = {'roi': 0.4, 'payback': 0.3, 'self_sufficiency': 0.3}

    score = (roi_norm * weights['roi'] +
             payback_norm * weights['payback'] +
             ss_norm * weights['self_sufficiency'])

    return score
```

## Constraints Handling

### Budget Constraint

```python
if pv_cost + battery_cost > max_budget:
    skip  # Don't evaluate this configuration
```

### Physical Constraints

- **Min PV Size**: Must be at least 2 kWp (practical minimum)
- **Max PV Size**: Limited by roof space or budget
- **Battery/PV Ratio**: Battery should be 0.5x to 2x of PV daily production
  - Too small battery: Limited benefit
  - Too large battery: Never fully charged, wasted investment

## Output Visualization

### 1. Heatmap: Solution Space

```
         Battery Size (kWh)
         0    5    10   15   20
PV   3  [score_00 score_01 ...]
kWp  5  [score_10 score_11 ...]
     7  [score_20 score_21 ...]
     ...
```

- Color intensity = optimization score
- Star marker = optimal configuration
- Contour lines for payback periods

### 2. Pareto Frontier

Plot showing trade-offs between competing objectives:

- X-axis: Payback period (years)
- Y-axis: ROI (%)
- Point size: Self-sufficiency (%)
- Color: Total investment (EUR)

### 3. Sensitivity Analysis

Show how optimal solution changes with:

- Electricity price variations (±20%)
- Battery cost changes (future price drops)
- Consumption pattern changes

### 4. Top 5 Configurations Table

| Rank | PV (kWp) | Battery (kWh) | Cost (EUR) | Payback (yr) | ROI (%) | Self-Suff (%) |
| ---- | -------- | ------------- | ---------- | ------------ | ------- | ------------- |
| 1    | 6.5      | 10            | 11,500     | 8.2          | 145     | 78            |
| 2    | 8.0      | 8             | 12,000     | 8.5          | 140     | 74            |
| ...  | ...      | ...           | ...        | ...          | ...     | ...           |

## Implementation Phases

### Phase 1: Core Algorithm (Week 1)

- [x] Plan architecture
- [ ] Implement grid search function
- [ ] Integrate with existing simulation engine
- [ ] Add basic scoring functions

### Phase 2: UI Integration (Week 1-2)

- [ ] Add optimization tab/dialog
- [ ] Parameter input widgets (ranges, constraints)
- [ ] Progress bar for long calculations
- [ ] Enable/disable optimization button

### Phase 3: Visualization (Week 2)

- [ ] Heatmap visualization
- [ ] Results table
- [ ] Export optimal configuration to main input fields
- [ ] Save/load optimization results

### Phase 4: Advanced Features (Week 3)

- [ ] Pareto frontier analysis
- [ ] Sensitivity analysis
- [ ] What-if scenarios
- [ ] Multi-year price projections

## Performance Optimization

### Caching Strategy

```python
# Cache annual simulations at each configuration
simulation_cache = {}

def simulate_with_cache(pv_size, battery_size):
    key = (pv_size, battery_size)
    if key in simulation_cache:
        return simulation_cache[key]

    result = run_full_year_simulation(pv_size, battery_size)
    simulation_cache[key] = result
    return result
```

### Parallel Processing

```python
from multiprocessing import Pool

def optimize_parallel(configurations):
    with Pool(processes=cpu_count()) as pool:
        results = pool.starmap(simulate_with_cache, configurations)
    return results
```

- Can reduce 500 simulations from ~15 minutes to ~2 minutes on 8-core CPU

### Progress Reporting

```python
total_configs = len(pv_range) * len(battery_range)
completed = 0

for config in configurations:
    result = simulate(config)
    completed += 1
    progress = (completed / total_configs) * 100
    update_progress_bar(progress)
    QApplication.processEvents()  # Keep UI responsive
```

## Code Structure

```
PV_Calculator_tool/
├── PV_optimizer.py              # New: Core optimization engine
│   ├── class PVOptimizer
│   │   ├── __init__(consumption_gen, solar_gen, battery_calc)
│   │   ├── optimize(pv_range, battery_range, criterion, constraints)
│   │   ├── grid_search(...)
│   │   ├── evaluate_configuration(pv_size, battery_size)
│   │   └── score_configuration(result, criterion)
│   │
│   └── class OptimizationResult
│       ├── best_pv_size
│       ├── best_battery_size
│       ├── all_results_grid
│       ├── pareto_frontier
│       └── top_n_configurations
│
├── PV_optimization_graphs.py    # New: Visualization
│   ├── plot_optimization_heatmap(results)
│   ├── plot_pareto_frontier(results)
│   └── plot_sensitivity_analysis(results)
│
└── PV_calculator_gui.py         # Modified: Add optimization tab
    └── show_system_optimization()  # Replace placeholder with real implementation
```

## Example Usage

```python
# User input from GUI
pv_range = (3.0, 15.0, 0.5)  # min, max, step
battery_range = (0, 20, 1.0)
criterion = "balanced"
max_budget = 15000  # EUR

# Run optimization
optimizer = PVOptimizer(consumption_gen, solar_gen, battery_calc)
result = optimizer.optimize(
    pv_range=pv_range,
    battery_range=battery_range,
    criterion=criterion,
    constraints={'max_budget': max_budget}
)

# Display results
print(f"Optimal Configuration:")
print(f"  PV Size: {result.best_pv_size} kWp")
print(f"  Battery Size: {result.best_battery_size} kWh")
print(f"  Total Cost: {result.best_total_cost} EUR")
print(f"  Payback Period: {result.best_payback} years")
print(f"  ROI: {result.best_roi}%")
print(f"  Self-Sufficiency: {result.best_self_sufficiency}%")

# Visualize
plot_optimization_heatmap(result)
plot_pareto_frontier(result)
```

## Validation & Testing

### Test Cases

1. **Small system** (3 kWp, no battery) - Ensure payback makes sense
2. **Oversized system** (20 kWp, 30 kWh) - Should show diminishing returns
3. **Budget constraint** - Verify solutions respect budget limit
4. **Zero PV** - Edge case handling
5. **Extreme prices** - Robustness to unusual tariff structures

### Performance Benchmarks

- **Target**: < 30 seconds for 200 configurations
- **Acceptable**: < 2 minutes for 500 configurations
- **Monitor**: Memory usage (caching can be expensive)

## Future Enhancements

### Machine Learning Approach (Advanced)

- Train model on thousands of simulations
- Use ML to predict optimal configuration instantly
- Active learning: Simulate only most informative configurations

### Cloud Integration

- Offload heavy computations to cloud
- Access historical weather data for better predictions
- Share optimization results with community

### Dynamic Pricing

- Integrate real-time electricity price forecasts
- Optimize for time-of-use tariffs
- Include demand charges in optimization

## Conclusion

This optimization feature will transform the calculator from a "what-if" tool into a "what-should-I-do" recommendation engine. Users can confidently invest in the right-sized system without manual trial-and-error.

**Estimated Development Time**: 2-3 weeks for full implementation
**Complexity**: Medium (requires careful performance optimization)
**Value**: High (major differentiator vs other calculators)
