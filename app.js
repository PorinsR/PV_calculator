// PV Calculator - Main Application Logic

// Initialize application
document.addEventListener("DOMContentLoaded", function () {
  initializeTabs();
  initializeFormElements();
  initializeEVDatabase();
  loadConfiguration();

  // Add event listeners for buttons
  document
    .getElementById("save-config-btn")
    .addEventListener("click", saveConfiguration);
  document
    .getElementById("load-config-btn")
    .addEventListener("click", loadConfiguration);
  document
    .getElementById("reset-config-btn")
    .addEventListener("click", resetToDefaults);
  document
    .getElementById("battery-recommendation-btn")
    .addEventListener("click", showBatteryRecommendation);
  document
    .getElementById("fetch-pvgis-btn")
    .addEventListener("click", fetchPVGISData);

  // Analysis tab buttons
  document
    .getElementById("daily-flow-btn")
    .addEventListener("click", generateDailyFlow);
  document
    .getElementById("annual-analysis-btn")
    .addEventListener("click", generateAnnualAnalysis);
  document
    .getElementById("energy-distribution-btn")
    .addEventListener("click", generateEnergyDistribution);
  document
    .getElementById("cumulative-payback-btn")
    .addEventListener("click", generateCumulativePayback);
  document
    .getElementById("summary-report-btn")
    .addEventListener("click", generateSummaryReport);

  // Modal close
  document.querySelector(".close").addEventListener("click", closeModal);
  window.addEventListener("click", function (event) {
    const modal = document.getElementById("modal");
    if (event.target === modal) {
      closeModal();
    }
  });
});

// Tab management
function initializeTabs() {
  const tabButtons = document.querySelectorAll(".tab-button");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const targetTab = button.dataset.tab;

      // Remove active class from all tabs and contents
      tabButtons.forEach((btn) => btn.classList.remove("active"));
      tabContents.forEach((content) => content.classList.remove("active"));

      // Add active class to clicked tab and corresponding content
      button.classList.add("active");
      document.getElementById(`${targetTab}-tab`).classList.add("active");
    });
  });
}

// Initialize form element interactions
function initializeFormElements() {
  // Consumption seasonal slider
  const seasonalSlider = document.getElementById("consumption-seasonal");
  const seasonalValue = document.getElementById("consumption-seasonal-value");
  seasonalSlider.addEventListener("input", function () {
    seasonalValue.textContent = (this.value / 100).toFixed(2);
  });

  // EV duration info update
  const evWeeklyKm = document.getElementById("ev-weekly-km");
  const evConsumption = document.getElementById("ev-consumption");
  const evChargerPower = document.getElementById("ev-charger-power");
  const evChargingStart = document.getElementById("ev-charging-start");

  [evWeeklyKm, evConsumption, evChargerPower, evChargingStart].forEach(
    (element) => {
      element.addEventListener("input", updateEVChargingDuration);
    }
  );
}

// Initialize EV database
function initializeEVDatabase() {
  const evMakeSelect = document.getElementById("ev-make");
  const evModelSelect = document.getElementById("ev-model");
  const evConfigSelect = document.getElementById("ev-configuration");

  // Populate makes
  const makes = getEVMakes();
  makes.forEach((make) => {
    const option = document.createElement("option");
    option.value = make.id;
    option.textContent = make.name;
    evMakeSelect.appendChild(option);
  });

  // Make change handler
  evMakeSelect.addEventListener("change", function () {
    const makeId = this.value;
    evModelSelect.innerHTML = '<option value="">-- Select Model --</option>';
    evConfigSelect.innerHTML =
      '<option value="">-- Select Configuration --</option>';
    document.getElementById("ev-consumption").value = "--";

    if (makeId) {
      const models = getEVModels(makeId);
      models.forEach((model) => {
        const option = document.createElement("option");
        option.value = model;
        option.textContent = model;
        evModelSelect.appendChild(option);
      });
    }
  });

  // Model change handler
  evModelSelect.addEventListener("change", function () {
    const makeId = evMakeSelect.value;
    const model = this.value;
    evConfigSelect.innerHTML =
      '<option value="">-- Select Configuration --</option>';
    document.getElementById("ev-consumption").value = "--";

    if (makeId && model) {
      const configs = getEVConfigurations(makeId, model);
      configs.forEach((config) => {
        const option = document.createElement("option");
        option.value = config;
        option.textContent = config;
        evConfigSelect.appendChild(option);
      });
    }
  });

  // Configuration change handler
  evConfigSelect.addEventListener("change", function () {
    const makeId = evMakeSelect.value;
    const model = evModelSelect.value;
    const config = this.value;

    if (makeId && model && config) {
      const evData = getEVData(makeId, model, config);
      if (evData) {
        document.getElementById("ev-consumption").value = evData.consumption;
        updateEVChargingDuration();
      }
    } else {
      document.getElementById("ev-consumption").value = "--";
    }
  });
}

// Update EV charging duration display
function updateEVChargingDuration() {
  const weeklyKm =
    parseFloat(document.getElementById("ev-weekly-km").value) || 0;
  const consumption =
    parseFloat(document.getElementById("ev-consumption").value) || 0;
  const chargerPower =
    parseFloat(document.getElementById("ev-charger-power").value) || 1;
  const startHour =
    parseInt(document.getElementById("ev-charging-start").value) || 22;

  if (weeklyKm > 0 && consumption > 0 && chargerPower > 0) {
    const dailyKm = weeklyKm / 7;
    const dailyKwh = (dailyKm * consumption) / 100;
    const durationHours = dailyKwh / chargerPower;

    const endHour = (startHour + Math.ceil(durationHours)) % 24;

    const infoText =
      `⚡ Estimated: ${dailyKwh.toFixed(1)} kWh/day, ` +
      `~${durationHours.toFixed(1)} hours charging ` +
      `(${startHour}:00 - ${endHour}:00)`;

    document.getElementById("ev-duration-info").textContent = infoText;
  } else {
    document.getElementById("ev-duration-info").textContent = "";
  }
}

// Configuration Management
function getConfiguration() {
  return {
    tariff: {
      power_amperes: document.getElementById("power-amperes").value,
      power_cost: document.getElementById("power-cost").value,
      electricity_cost: document.getElementById("electricity-cost").value,
      transfer_cost: document.getElementById("transfer-cost").value,
      service_cost: document.getElementById("service-cost").value,
      monthly_service_fee: document.getElementById("monthly-service-fee").value,
      vat_rate: document.getElementById("vat-rate").value,
    },
    consumption: {
      monthly_consumption: document.getElementById("monthly-consumption").value,
      pattern_type: document.getElementById("consumption-pattern").value,
      seasonal_strength: (
        document.getElementById("consumption-seasonal").value / 100
      ).toFixed(2),
    },
    pv: {
      enabled: document.getElementById("pv-enabled").checked,
      size: document.getElementById("pv-size").value,
      cost: document.getElementById("pv-cost").value,
      location: document.getElementById("pv-location").value,
      tilt: document.getElementById("pv-tilt").value,
      azimuth: document.getElementById("pv-azimuth").value,
    },
    battery: {
      enabled: document.getElementById("battery-enabled").checked,
      capacity: document.getElementById("battery-capacity").value,
      cost: document.getElementById("battery-cost").value,
    },
    nordpool: {
      price: document.getElementById("nordpool-price").value,
    },
    ev: {
      enabled: document.getElementById("ev-enabled").checked,
      make: document.getElementById("ev-make").value,
      model: document.getElementById("ev-model").value,
      configuration: document.getElementById("ev-configuration").value,
      consumption: document.getElementById("ev-consumption").value,
      weekly_km: document.getElementById("ev-weekly-km").value,
      charger_power: document.getElementById("ev-charger-power").value,
      charging_start: document.getElementById("ev-charging-start").value,
    },
  };
}

function setConfiguration(config) {
  // Tariff
  if (config.tariff) {
    document.getElementById("power-amperes").value =
      config.tariff.power_amperes || 16;
    document.getElementById("power-cost").value =
      config.tariff.power_cost || 0.82;
    document.getElementById("electricity-cost").value =
      config.tariff.electricity_cost || 0.10379;
    document.getElementById("transfer-cost").value =
      config.tariff.transfer_cost || 0.03962;
    document.getElementById("service-cost").value =
      config.tariff.service_cost || 0.0165;
    document.getElementById("monthly-service-fee").value =
      config.tariff.monthly_service_fee || 0.83;
    document.getElementById("vat-rate").value = config.tariff.vat_rate || 21;
  }

  // Consumption
  if (config.consumption) {
    document.getElementById("monthly-consumption").value =
      config.consumption.monthly_consumption || 250;
    document.getElementById("consumption-pattern").value =
      config.consumption.pattern_type || "working_family";
    const seasonalValue = parseFloat(
      config.consumption.seasonal_strength || 0.2
    );
    document.getElementById("consumption-seasonal").value = seasonalValue * 100;
    document.getElementById("consumption-seasonal-value").textContent =
      seasonalValue.toFixed(2);
  }

  // PV
  if (config.pv) {
    document.getElementById("pv-enabled").checked = config.pv.enabled !== false;
    document.getElementById("pv-size").value = config.pv.size || 9;
    document.getElementById("pv-cost").value = config.pv.cost || 2500;
    document.getElementById("pv-location").value =
      config.pv.location || "riga_latvia";
    document.getElementById("pv-tilt").value = config.pv.tilt || 15;
    document.getElementById("pv-azimuth").value = config.pv.azimuth || 20;
  }

  // Battery
  if (config.battery) {
    document.getElementById("battery-enabled").checked =
      config.battery.enabled !== false;
    document.getElementById("battery-capacity").value =
      config.battery.capacity || 14;
    document.getElementById("battery-cost").value = config.battery.cost || 2000;
  }

  // Nord Pool
  if (config.nordpool) {
    document.getElementById("nordpool-price").value =
      config.nordpool.price || 0.01;
  }

  // EV
  if (config.ev) {
    document.getElementById("ev-enabled").checked = config.ev.enabled === true;

    // Set make first
    if (config.ev.make) {
      document.getElementById("ev-make").value = config.ev.make;
      // Trigger change to populate models
      const event = new Event("change");
      document.getElementById("ev-make").dispatchEvent(event);

      // Wait a bit then set model
      setTimeout(() => {
        if (config.ev.model) {
          document.getElementById("ev-model").value = config.ev.model;
          document
            .getElementById("ev-model")
            .dispatchEvent(new Event("change"));

          // Wait a bit then set configuration
          setTimeout(() => {
            if (config.ev.configuration) {
              document.getElementById("ev-configuration").value =
                config.ev.configuration;
              document
                .getElementById("ev-configuration")
                .dispatchEvent(new Event("change"));
            }
          }, 100);
        }
      }, 100);
    }

    document.getElementById("ev-weekly-km").value = config.ev.weekly_km || 315;
    document.getElementById("ev-charger-power").value =
      config.ev.charger_power || 11;
    document.getElementById("ev-charging-start").value =
      config.ev.charging_start || 18;
  }
}

function saveConfiguration() {
  const config = getConfiguration();
  localStorage.setItem("pv_calculator_config", JSON.stringify(config));
  showToast("Configuration saved successfully!", "success");
}

function loadConfiguration() {
  const savedConfig = localStorage.getItem("pv_calculator_config");
  if (savedConfig) {
    try {
      const config = JSON.parse(savedConfig);
      setConfiguration(config);
      showToast("Configuration loaded successfully!", "success");
    } catch (e) {
      showToast("Error loading configuration: " + e.message, "error");
    }
  }
}

function resetToDefaults() {
  if (confirm("Are you sure you want to reset all values to defaults?")) {
    localStorage.removeItem("pv_calculator_config");
    setConfiguration({});
    showToast("Reset to defaults", "info");
  }
}

// Battery Recommendation
function showBatteryRecommendation() {
  const monthlyConsumption =
    parseFloat(document.getElementById("monthly-consumption").value) || 500;
  const evEnabled = document.getElementById("ev-enabled").checked;
  const weeklyKm =
    parseFloat(document.getElementById("ev-weekly-km").value) || 0;
  const evConsumption =
    parseFloat(document.getElementById("ev-consumption").value) || 0;

  // Calculate daily consumption
  const dailyHousehold = (monthlyConsumption * 12) / 365;
  const dailyEV = evEnabled ? ((weeklyKm / 7) * evConsumption) / 100 : 0;
  const dailyTotal = dailyHousehold + dailyEV;

  // Recommendations
  const recommended50 = (dailyTotal * 0.5).toFixed(1);
  const recommended70 = (dailyTotal * 0.7).toFixed(1);
  const recommended100 = (dailyTotal * 1.0).toFixed(1);

  const message = `
        <h3>Battery Size Recommendation</h3>
        <p><strong>Daily Consumption Analysis:</strong></p>
        <ul>
            <li>Household: ${dailyHousehold.toFixed(1)} kWh/day</li>
            ${
              evEnabled
                ? `<li>EV Charging: ${dailyEV.toFixed(1)} kWh/day</li>`
                : ""
            }
            <li><strong>Total: ${dailyTotal.toFixed(1)} kWh/day</strong></li>
        </ul>
        <p><strong>Recommended Battery Sizes:</strong></p>
        <ul>
            <li><strong>Conservative (50%):</strong> ${recommended50} kWh - Covers evening/morning usage</li>
            <li><strong>Optimal (70%):</strong> ${recommended70} kWh - Good balance of cost and coverage</li>
            <li><strong>Full Coverage (100%):</strong> ${recommended100} kWh - Maximum self-sufficiency</li>
        </ul>
        <p><em>Note: Actual needs depend on your solar generation and consumption patterns.</em></p>
    `;

  showModal(message);
}

// PVGIS Data Fetching
async function fetchPVGISData() {
  const btn = document.getElementById("fetch-pvgis-btn");
  const originalText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Fetching data...';

  try {
    const location = document.getElementById("pv-location").value;
    const pvSize = parseFloat(document.getElementById("pv-size").value) || 5.0;
    const tilt = parseFloat(document.getElementById("pv-tilt").value) || 35;
    const azimuth =
      parseFloat(document.getElementById("pv-azimuth").value) || 0;

    // Location coordinates mapping
    const locationCoords = {
      riga_latvia: { lat: 56.95, lon: 24.11, name: "Riga, Latvia" },
      vilnius_lithuania: { lat: 54.69, lon: 25.28, name: "Vilnius, Lithuania" },
      tallinn_estonia: { lat: 59.44, lon: 24.75, name: "Tallinn, Estonia" },
      helsinki_finland: { lat: 60.17, lon: 24.94, name: "Helsinki, Finland" },
      stockholm_sweden: { lat: 59.33, lon: 18.06, name: "Stockholm, Sweden" },
      oslo_norway: { lat: 59.91, lon: 10.75, name: "Oslo, Norway" },
      copenhagen_denmark: {
        lat: 55.68,
        lon: 12.57,
        name: "Copenhagen, Denmark",
      },
    };

    const coords = locationCoords[location];
    if (!coords) {
      throw new Error("Location not found");
    }

    // Construct PVGIS API URL with CORS proxy
    const pvgisUrl = `https://re.jrc.ec.europa.eu/api/v5_2/PVcalc?lat=${coords.lat}&lon=${coords.lon}&peakpower=${pvSize}&loss=14&angle=${tilt}&aspect=${azimuth}&outputformat=json`;

    // Try with CORS proxy first
    const corsProxy = "https://corsproxy.io/?";
    const apiUrl = corsProxy + encodeURIComponent(pvgisUrl);

    const response = await fetch(apiUrl);
    if (!response.ok) {
      throw new Error("PVGIS API request failed");
    }

    const data = await response.json();

    if (data.outputs && data.outputs.totals) {
      const annualProduction = data.outputs.totals.fixed.E_y;
      const avgDaily = annualProduction / 365;

      document.getElementById(
        "solar-data-source"
      ).innerHTML = `✅ Using: PVGIS Real Data - Annual: ${annualProduction.toFixed(
        0
      )} kWh/year, Daily Avg: ${avgDaily.toFixed(1)} kWh/day`;

      showToast(
        `PVGIS data fetched successfully! Annual production: ${annualProduction.toFixed(
          0
        )} kWh`,
        "success"
      );
    } else {
      throw new Error("Invalid PVGIS response");
    }
  } catch (error) {
    // Show more helpful error message
    const errorMsg =
      error.message.includes("NetworkError") || error.message.includes("CORS")
        ? "PVGIS API unavailable (CORS restriction). Using built-in solar model instead."
        : "Error: " + error.message;

    showToast(errorMsg, "warning");

    // Provide alternative: manual calculation link
    const coords = locationCoords[document.getElementById("pv-location").value];
    const pvSize = parseFloat(document.getElementById("pv-size").value) || 5.0;
    const tilt = parseFloat(document.getElementById("pv-tilt").value) || 35;
    const azimuth =
      parseFloat(document.getElementById("pv-azimuth").value) || 0;

    const pvgisManualUrl = `https://re.jrc.ec.europa.eu/pvg_tools/en/#PVP?lat=${coords.lat}&lon=${coords.lon}&peakpower=${pvSize}&loss=14&angle=${tilt}&aspect=${azimuth}`;

    document.getElementById("solar-data-source").innerHTML =
      `📊 Using: Built-in solar model<br>` +
      `<small>For accurate data, visit: <a href="${pvgisManualUrl}" target="_blank">PVGIS Calculator</a></small>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalText;
  }
}

// Modal functions
function showModal(content) {
  const modal = document.getElementById("modal");
  const modalBody = document.getElementById("modal-body");
  modalBody.innerHTML = content;
  modal.style.display = "block";
}

function closeModal() {
  document.getElementById("modal").style.display = "none";
}

// Toast notification
function showToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 3000);
}

// Analysis Functions (will call calculator.js)
function generateDailyFlow() {
  const config = getConfiguration();
  const date = document.getElementById("analysis-date").value;

  if (!config.pv.enabled) {
    showToast("Please enable PV System to use this feature", "warning");
    return;
  }

  document.getElementById(
    "analysis-status"
  ).textContent = `Calculating daily energy flow for ${date}...`;

  // Call calculator
  const result = calculateDailyEnergyFlow(config, new Date(date));
  displayDailyFlowChart(result);

  document.getElementById(
    "analysis-status"
  ).textContent = `✓ Daily energy flow calculated for ${date}`;
}

function generateAnnualAnalysis() {
  const config = getConfiguration();

  if (!config.pv.enabled) {
    showToast("Please enable PV System to use this feature", "warning");
    return;
  }

  document.getElementById("analysis-status").textContent =
    "Calculating annual analysis...";

  const result = calculateAnnualAnalysis(config);
  displayAnnualAnalysisChart(result);

  document.getElementById("analysis-status").textContent =
    "✓ Annual analysis complete";
}

function generateEnergyDistribution() {
  const config = getConfiguration();

  if (!config.pv.enabled) {
    showToast("Please enable PV System to use this feature", "warning");
    return;
  }

  document.getElementById("analysis-status").textContent =
    "Calculating energy distribution...";

  const result = calculateEnergyDistribution(config);
  displayEnergyDistributionChart(result);

  document.getElementById("analysis-status").textContent =
    "✓ Energy distribution calculated";
}

function generateCumulativePayback() {
  const config = getConfiguration();

  if (!config.pv.enabled) {
    showToast("Please enable PV System to use this feature", "warning");
    return;
  }

  document.getElementById("analysis-status").textContent =
    "Calculating cumulative payback...";

  const result = calculateCumulativePayback(config);
  displayCumulativePaybackChart(result);

  document.getElementById("analysis-status").textContent =
    "✓ Cumulative payback calculated";
}

function generateSummaryReport() {
  const config = getConfiguration();

  if (!config.pv.enabled) {
    showToast("Please enable PV System to use this feature", "warning");
    return;
  }

  document.getElementById("analysis-status").textContent =
    "Generating summary report...";

  const result = generateComparisonSummary(config);
  displaySummaryReport(result);

  document.getElementById("analysis-status").textContent =
    "✓ Summary report generated";
}
