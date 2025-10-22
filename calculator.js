// PV Calculator - Calculation Engine

// Solar irradiance data by location (kWh/m²/day average)
const SOLAR_IRRADIANCE = {
  riga_latvia: 3.2,
  vilnius_lithuania: 3.3,
  tallinn_estonia: 3.0,
  helsinki_finland: 2.8,
  stockholm_sweden: 2.9,
  oslo_norway: 2.7,
  copenhagen_denmark: 3.0,
};

// Seasonal multipliers for solar generation (by month, 1-12)
const SEASONAL_SOLAR_MULTIPLIERS = [
  0.35,
  0.55,
  0.85,
  1.15,
  1.3,
  1.35, // Jan-Jun
  1.3,
  1.2,
  1.0,
  0.7,
  0.4,
  0.3, // Jul-Dec
];

// Seasonal multipliers for consumption (by month, 1-12)
const SEASONAL_CONSUMPTION_MULTIPLIERS = [
  1.25,
  1.2,
  1.1,
  1.0,
  0.9,
  0.85, // Jan-Jun (higher in winter)
  0.85,
  0.85,
  0.9,
  1.0,
  1.1,
  1.2, // Jul-Dec
];

// Hourly consumption patterns
const HOURLY_PATTERNS = {
  working_family: {
    weekday: [
      0.3, 0.3, 0.3, 0.3, 0.4, 0.6, 1.2, 1.5, 0.7, 0.5, 0.4, 0.4, 0.5, 0.5, 0.5,
      0.6, 0.8, 1.5, 2.0, 2.2, 1.8, 1.4, 1.0, 0.6,
    ],
    weekend: [
      0.4, 0.4, 0.4, 0.4, 0.5, 0.7, 1.0, 1.3, 1.5, 1.4, 1.3, 1.2, 1.2, 1.2, 1.2,
      1.2, 1.3, 1.4, 1.6, 1.5, 1.4, 1.2, 0.8, 0.6,
    ],
  },
  retired_couple: {
    weekday: [
      0.4, 0.4, 0.4, 0.5, 0.7, 1.0, 1.4, 1.5, 1.3, 1.2, 1.1, 1.2, 1.3, 1.2, 1.1,
      1.2, 1.3, 1.5, 1.8, 1.6, 1.3, 1.0, 0.7, 0.5,
    ],
    weekend: [
      0.4, 0.4, 0.4, 0.5, 0.7, 1.0, 1.4, 1.5, 1.3, 1.2, 1.1, 1.2, 1.3, 1.2, 1.1,
      1.2, 1.3, 1.5, 1.8, 1.6, 1.3, 1.0, 0.7, 0.5,
    ],
  },
  home_office: {
    weekday: [
      0.4, 0.4, 0.4, 0.5, 0.7, 1.0, 1.3, 1.4, 1.5, 1.6, 1.6, 1.5, 1.4, 1.5, 1.6,
      1.6, 1.5, 1.6, 1.8, 1.7, 1.5, 1.2, 0.8, 0.6,
    ],
    weekend: [
      0.5, 0.5, 0.5, 0.5, 0.6, 0.9, 1.2, 1.4, 1.3, 1.2, 1.1, 1.2, 1.2, 1.2, 1.2,
      1.3, 1.4, 1.5, 1.6, 1.5, 1.3, 1.0, 0.7, 0.6,
    ],
  },
  minimal: {
    weekday: [
      0.2, 0.2, 0.2, 0.2, 0.3, 0.5, 1.0, 0.4, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3,
      0.4, 0.5, 1.2, 1.8, 1.5, 1.2, 0.8, 0.5, 0.3,
    ],
    weekend: [
      0.3, 0.3, 0.3, 0.3, 0.4, 0.6, 1.1, 1.4, 1.2, 1.0, 0.9, 1.0, 1.0, 1.0, 1.0,
      1.1, 1.2, 1.4, 1.5, 1.3, 1.1, 0.8, 0.5, 0.4,
    ],
  },
};

// Solar generation pattern (hourly, 0-23)
function getSolarGenerationPattern(month) {
  // Solar generation follows a bell curve during daylight hours
  // Adjusted by month for day length
  const dayLengthFactors = [8, 10, 12, 14, 15, 16, 16, 15, 13, 11, 9, 8]; // hours by month
  const dayLength = dayLengthFactors[month - 1];
  const sunrise = 12 - dayLength / 2;
  const sunset = 12 + dayLength / 2;

  const pattern = [];
  for (let hour = 0; hour < 24; hour++) {
    if (hour < sunrise || hour >= sunset) {
      pattern.push(0);
    } else {
      // Bell curve centered at noon
      const hourFromNoon = Math.abs(hour - 12);
      const maxHoursFromNoon = dayLength / 2;
      const factor = Math.cos(
        ((hourFromNoon / maxHoursFromNoon) * Math.PI) / 2
      );
      pattern.push(Math.max(0, factor));
    }
  }

  return pattern;
}

// Calculate hourly consumption for a given date
function getHourlyConsumption(date, config) {
  const dayOfWeek = date.getDay(); // 0 = Sunday, 6 = Saturday
  const month = date.getMonth() + 1; // 1-12
  const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;

  const patternType = config.consumption.pattern_type || "working_family";
  const pattern = isWeekend
    ? HOURLY_PATTERNS[patternType].weekend
    : HOURLY_PATTERNS[patternType].weekday;

  // Calculate daily average consumption
  const monthlyConsumption =
    parseFloat(config.consumption.monthly_consumption) || 500;
  const annualConsumption = monthlyConsumption * 12;
  const dailyBase = annualConsumption / 365;

  // Apply seasonal multiplier
  const seasonalStrength =
    parseFloat(config.consumption.seasonal_strength) || 0.2;
  const seasonalMultiplier =
    1 + (SEASONAL_CONSUMPTION_MULTIPLIERS[month - 1] - 1) * seasonalStrength;
  const dailyConsumption = dailyBase * seasonalMultiplier;

  // Weekend adjustment (15% higher)
  const weekendFactor = isWeekend ? 1.15 : 1.0;
  const adjustedDaily = dailyConsumption * weekendFactor;

  // Normalize pattern and scale to daily consumption
  const patternSum = pattern.reduce((a, b) => a + b, 0);
  const hourlyConsumption = pattern.map(
    (p) => (p / patternSum) * adjustedDaily
  );

  // Add EV charging if enabled
  if (
    config.ev.enabled &&
    config.ev.consumption !== "--" &&
    config.ev.consumption > 0
  ) {
    const weeklyKm = parseFloat(config.ev.weekly_km) || 0;
    const evConsumption = parseFloat(config.ev.consumption) || 0;
    const chargerPower = parseFloat(config.ev.charger_power) || 7.0;
    const startHour = parseInt(config.ev.charging_start) || 22;

    const dailyKm = weeklyKm / 7;
    const dailyEvKwh = (dailyKm * evConsumption) / 100;
    const chargingHours = Math.ceil(dailyEvKwh / chargerPower);

    // Distribute EV charging
    for (let i = 0; i < chargingHours; i++) {
      const hour = (startHour + i) % 24;
      hourlyConsumption[hour] += dailyEvKwh / chargingHours;
    }
  }

  return hourlyConsumption;
}

// Calculate hourly solar generation for a given date
function getHourlySolarGeneration(date, config) {
  const month = date.getMonth() + 1; // 1-12
  const pvSize = parseFloat(config.pv.size) || 5.0;

  // Check if PVGIS data is available
  if (config.pv.pvgisData && config.pv.pvgisData.monthly) {
    const pvgisData = config.pv.pvgisData;

    // Get the monthly data for this month
    const monthData = pvgisData.monthly.find((m) => m.month === month);

    if (monthData) {
      // Use PVGIS daily average energy (E_d) for this month
      // Scale to current system size if different from when PVGIS was fetched
      const scaleFactor = pvSize / pvgisData.systemSize;
      const dailyGeneration = monthData.E_d * scaleFactor;

      // Get hourly pattern and distribute daily generation
      const pattern = getSolarGenerationPattern(month);
      const patternSum = pattern.reduce((a, b) => a + b, 0);

      const hourlyGeneration = pattern.map(
        (p) => (p / patternSum) * dailyGeneration
      );

      return hourlyGeneration;
    }
  }

  // Fallback to built-in solar model if PVGIS data not available
  const location = config.pv.location || "riga_latvia";
  const baseIrradiance = SOLAR_IRRADIANCE[location] || 3.2;
  const seasonalMultiplier = SEASONAL_SOLAR_MULTIPLIERS[month - 1];
  const dailyIrradiance = baseIrradiance * seasonalMultiplier;

  // Get hourly pattern
  const pattern = getSolarGenerationPattern(month);
  const patternSum = pattern.reduce((a, b) => a + b, 0);

  // Calculate hourly generation
  const dailyGeneration = pvSize * dailyIrradiance * 0.85; // 85% system efficiency
  const hourlyGeneration = pattern.map(
    (p) => (p / patternSum) * dailyGeneration
  );

  return hourlyGeneration;
}

// Battery simulation
class BatterySimulator {
  constructor(capacity, efficiency = 0.95, minSoc = 0.1) {
    this.capacity = capacity;
    this.efficiency = efficiency;
    this.minSoc = minSoc;
    this.soc = capacity * 0.5; // Start at 50%
  }

  charge(power) {
    const availableSpace = this.capacity - this.soc;
    const actualCharge = Math.min(power * this.efficiency, availableSpace);
    this.soc += actualCharge;
    return actualCharge / this.efficiency; // Return actual power used
  }

  discharge(power) {
    const availableEnergy = this.soc - this.capacity * this.minSoc;
    const actualDischarge = Math.min(power, availableEnergy);
    this.soc -= actualDischarge;
    return actualDischarge * this.efficiency; // Return actual power delivered
  }

  getSoc() {
    return this.soc;
  }

  getSocPercent() {
    return (this.soc / this.capacity) * 100;
  }
}

// Calculate daily energy flow
function calculateDailyEnergyFlow(config, date) {
  const consumption = getHourlyConsumption(date, config);
  const generation = config.pv.enabled
    ? getHourlySolarGeneration(date, config)
    : new Array(24).fill(0);

  const batteryEnabled = config.battery.enabled;
  const batteryCapacity = parseFloat(config.battery.capacity) || 7.0;
  const battery = batteryEnabled ? new BatterySimulator(batteryCapacity) : null;

  const results = {
    hours: [],
    consumption: [],
    generation: [],
    batteryCharge: [],
    batterySoc: [],
    gridImport: [],
    gridExport: [],
    selfConsumption: [],
  };

  for (let hour = 0; hour < 24; hour++) {
    const cons = consumption[hour];
    const gen = generation[hour];

    let gridImport = 0;
    let gridExport = 0;
    let batteryCharge = 0;
    let selfConsumption = Math.min(cons, gen);

    const surplus = gen - cons;

    if (surplus > 0) {
      // Excess generation
      if (battery && batteryEnabled) {
        batteryCharge = battery.charge(surplus);
        const remainingSurplus = surplus - batteryCharge;
        if (remainingSurplus > 0) {
          gridExport = remainingSurplus;
        }
      } else {
        gridExport = surplus;
      }
    } else if (surplus < 0) {
      // Deficit
      const deficit = -surplus;
      if (battery && batteryEnabled) {
        const fromBattery = battery.discharge(deficit);
        batteryCharge = -fromBattery;
        const remainingDeficit = deficit - fromBattery;
        if (remainingDeficit > 0) {
          gridImport = remainingDeficit;
        }
      } else {
        gridImport = deficit;
      }
    }

    results.hours.push(hour);
    results.consumption.push(cons);
    results.generation.push(gen);
    results.batteryCharge.push(batteryCharge);
    results.batterySoc.push(battery ? battery.getSocPercent() : 0);
    results.gridImport.push(gridImport);
    results.gridExport.push(gridExport);
    results.selfConsumption.push(selfConsumption);
  }

  // Calculate daily totals
  results.totals = {
    consumption: results.consumption.reduce((a, b) => a + b, 0),
    generation: results.generation.reduce((a, b) => a + b, 0),
    gridImport: results.gridImport.reduce((a, b) => a + b, 0),
    gridExport: results.gridExport.reduce((a, b) => a + b, 0),
    selfConsumption: results.selfConsumption.reduce((a, b) => a + b, 0),
    selfSufficiency: 0,
  };

  // Self-sufficiency = (Consumption covered by non-grid sources) / Total consumption
  // = (Total consumption - Grid import) / Total consumption
  const consumptionFromOwnSources =
    results.totals.consumption - results.totals.gridImport;
  results.totals.selfSufficiency =
    results.totals.consumption > 0
      ? (consumptionFromOwnSources / results.totals.consumption) * 100
      : 0;

  return results;
}

// Calculate annual analysis
function calculateAnnualAnalysis(config) {
  const results = {
    months: [],
    monthlyGeneration: [],
    monthlyConsumption: [],
    monthlyGridImport: [],
    monthlyGridExport: [],
    monthlySelfSufficiency: [],
    monthlyCost: [],
    monthlySavings: [],
  };

  const electricityCost = parseFloat(config.tariff.electricity_cost) || 0.08;
  const transferCost = parseFloat(config.tariff.transfer_cost) || 0.04;
  const serviceCost = parseFloat(config.tariff.service_cost) || 0.01;
  const vatRate = parseFloat(config.tariff.vat_rate) || 21;
  const sellPrice = parseFloat(config.nordpool.price) || 0.06;

  const importRate =
    (electricityCost + transferCost + serviceCost) * (1 + vatRate / 100);

  const monthNames = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];

  for (let month = 1; month <= 12; month++) {
    // Simulate representative days for each month
    const daysInMonth = new Date(2024, month, 0).getDate();
    const midMonthDate = new Date(2024, month - 1, 15);

    const dayResult = calculateDailyEnergyFlow(config, midMonthDate);

    // Scale to month
    const monthlyGen = dayResult.totals.generation * daysInMonth;
    const monthlyCons = dayResult.totals.consumption * daysInMonth;
    const monthlyImport = dayResult.totals.gridImport * daysInMonth;
    const monthlyExport = dayResult.totals.gridExport * daysInMonth;
    const selfSuff = dayResult.totals.selfSufficiency;

    // Calculate costs (import minus export income)
    const costImport = monthlyImport * importRate;
    const incomeExport = monthlyExport * sellPrice;
    const netCost = costImport - incomeExport;

    // Savings vs no PV (monthly fees not included - they're the same for all scenarios)
    const costWithoutPV = monthlyCons * importRate;
    const savings = costWithoutPV - netCost;

    results.months.push(monthNames[month - 1]);
    results.monthlyGeneration.push(monthlyGen);
    results.monthlyConsumption.push(monthlyCons);
    results.monthlyGridImport.push(monthlyImport);
    results.monthlyGridExport.push(monthlyExport);
    results.monthlySelfSufficiency.push(selfSuff);
    results.monthlyCost.push(netCost);
    results.monthlySavings.push(savings);
  }

  // Calculate annual totals
  results.annualTotals = {
    generation: results.monthlyGeneration.reduce((a, b) => a + b, 0),
    consumption: results.monthlyConsumption.reduce((a, b) => a + b, 0),
    gridImport: results.monthlyGridImport.reduce((a, b) => a + b, 0),
    gridExport: results.monthlyGridExport.reduce((a, b) => a + b, 0),
    cost: results.monthlyCost.reduce((a, b) => a + b, 0),
    savings: results.monthlySavings.reduce((a, b) => a + b, 0),
    selfSufficiency:
      results.monthlySelfSufficiency.reduce((a, b) => a + b, 0) / 12,
  };

  return results;
}

// Calculate energy distribution
function calculateEnergyDistribution(config) {
  const annual = calculateAnnualAnalysis(config);

  const totalGeneration = annual.annualTotals.generation;
  const selfConsumption = totalGeneration - annual.annualTotals.gridExport;
  const directUse = selfConsumption * 0.7; // Approximate
  const batteryUse = selfConsumption * 0.3; // Approximate

  return {
    labels: [
      "Direct Self-Consumption",
      "Battery Storage",
      "Grid Export",
      "Grid Import",
    ],
    values: [
      directUse,
      batteryUse,
      annual.annualTotals.gridExport,
      annual.annualTotals.gridImport,
    ],
    annual: annual,
  };
}

// Helper function to calculate full year simulation (matching Python GUI)
function calculateFullYearSimulation(config) {
  let totalConsumption = 0;
  let totalGridImport = 0;
  let totalGridExport = 0;

  // Simulate every day of the year
  for (let dayOfYear = 1; dayOfYear <= 365; dayOfYear++) {
    const date = new Date(2024, 0, dayOfYear);
    const dayResult = calculateDailyEnergyFlow(config, date);

    totalConsumption += dayResult.totals.consumption;
    totalGridImport += dayResult.totals.gridImport;
    totalGridExport += dayResult.totals.gridExport;
  }

  return {
    consumption: totalConsumption,
    gridImport: totalGridImport,
    gridExport: totalGridExport,
  };
}

// Calculate cumulative payback
function calculateCumulativePayback(config) {
  const pvCost = parseFloat(config.pv.cost) || 7000;
  const batteryCost = config.battery.enabled
    ? parseFloat(config.battery.cost) || 4000
    : 0;
  const totalInvestment = pvCost + batteryCost;

  // Calculate pricing rates (matching Python GUI exactly)
  const electricityCost = parseFloat(config.tariff.electricity_cost) || 0.08;
  const transferCost = parseFloat(config.tariff.transfer_cost) || 0.04;
  const serviceCost = parseFloat(config.tariff.service_cost) || 0.01;
  const vatRate = parseFloat(config.tariff.vat_rate) || 21;
  const nordPoolPrice = parseFloat(config.nordpool.price) || 0.06;

  const importRate =
    (electricityCost + transferCost + serviceCost) * (1 + vatRate / 100);
  const exportRate = Math.max(
    0,
    nordPoolPrice - transferCost * (1 + vatRate / 100)
  );

  // SCENARIO 1: No PV, No Battery (Baseline)
  // Calculate total consumption for the year with all variations
  const config1 = JSON.parse(JSON.stringify(config));
  config1.pv.enabled = false;
  config1.battery.enabled = false;
  const results1 = calculateFullYearSimulation(config1);
  const scenario1AnnualCost = results1.consumption * importRate;

  // SCENARIO 2: PV Only (No Battery)
  // Calculate import/export with PV but no battery
  const config2 = JSON.parse(JSON.stringify(config));
  config2.pv.enabled = true;
  config2.battery.enabled = false;
  const results2 = calculateFullYearSimulation(config2);
  const scenario2AnnualCost =
    results2.gridImport * importRate - results2.gridExport * exportRate;

  // SCENARIO 3: PV + Battery (Full System)
  // Calculate import/export with both PV and battery
  const config3 = JSON.parse(JSON.stringify(config));
  config3.pv.enabled = true;
  config3.battery.enabled = config.battery.enabled;
  const results3 = calculateFullYearSimulation(config3);
  const scenario3AnnualCost =
    results3.gridImport * importRate - results3.gridExport * exportRate;

  const scenarios = {
    noPV: { costs: [], label: "No PV System" },
    pvOnly: { costs: [], label: "PV Only" },
    pvBattery: { costs: [], label: "PV + Battery" },
  };

  const years = 20;

  // Build cumulative cost arrays (matching Python GUI exactly)
  for (let year = 0; year <= years; year++) {
    // Scenario 1: No PV - just annual costs accumulating
    scenarios.noPV.costs.push(scenario1AnnualCost * year);

    // Scenario 2: PV Only - upfront cost + annual electricity costs
    scenarios.pvOnly.costs.push(pvCost + scenario2AnnualCost * year);

    // Scenario 3: PV + Battery - upfront cost + annual electricity costs
    scenarios.pvBattery.costs.push(
      totalInvestment + scenario3AnnualCost * year
    );
  }

  // Calculate savings and breakeven periods
  const savings_pv_only = scenario1AnnualCost - scenario2AnnualCost;
  const savings_pv_battery = scenario1AnnualCost - scenario3AnnualCost;

  return {
    years: Array.from({ length: years + 1 }, (_, i) => i),
    scenarios: scenarios,
    breakeven: {
      pvOnly: savings_pv_only > 0 ? Math.ceil(pvCost / savings_pv_only) : 999,
      pvBattery:
        savings_pv_battery > 0
          ? Math.ceil(totalInvestment / savings_pv_battery)
          : 999,
    },
    annualCosts: {
      scenario1: scenario1AnnualCost,
      scenario2: scenario2AnnualCost,
      scenario3: scenario3AnnualCost,
    },
  };
}

// Generate comparison summary
function generateComparisonSummary(config) {
  const annual = calculateAnnualAnalysis(config);
  const payback = calculateCumulativePayback(config);

  const pvCost = parseFloat(config.pv.cost) || 7000;
  const batteryCost = config.battery.enabled
    ? parseFloat(config.battery.cost) || 4000
    : 0;

  // Use the correctly calculated scenario costs from payback calculation
  const scenario1Cost = payback.annualCosts.scenario1;
  const scenario2Cost = payback.annualCosts.scenario2;
  const scenario3Cost = payback.annualCosts.scenario3;

  return {
    scenarios: {
      noPV: {
        annualCost: scenario1Cost,
        twentyYearCost: scenario1Cost * 20,
        selfSufficiency: 0,
        gridDependency: 100,
      },
      pvOnly: {
        initialInvestment: pvCost,
        annualCost: scenario2Cost,
        twentyYearCost: payback.scenarios.pvOnly.costs[20],
        annualSavings: scenario1Cost - scenario2Cost,
        breakeven: payback.breakeven.pvOnly,
        selfSufficiency: annual.annualTotals.selfSufficiency * 0.7, // Estimate ~70% of PV+Battery
        gridDependency: 100 - annual.annualTotals.selfSufficiency * 0.7,
      },
      pvBattery: {
        initialInvestment: pvCost + batteryCost,
        annualCost: scenario3Cost,
        twentyYearCost: payback.scenarios.pvBattery.costs[20],
        annualSavings: scenario1Cost - scenario3Cost,
        breakeven: payback.breakeven.pvBattery,
        selfSufficiency: annual.annualTotals.selfSufficiency,
        gridDependency: 100 - annual.annualTotals.selfSufficiency,
      },
    },
    annual: annual,
  };
}
