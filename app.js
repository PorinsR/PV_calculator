// PV Calculator - Main Application Logic

// Global state for location
let currentLocationCoords = { lat: 56.95, lon: 24.11, name: "Riga, Latvia" };
let addressSearchTimeout = null;
let pvgisMonthlyData = null; // Store PVGIS monthly generation data

// Initialize application
document.addEventListener("DOMContentLoaded", function () {
  initializeTabs();
  initializeFormElements();
  initializeEVDatabase();
  initializeAddressAutocomplete();
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
      location_coords: currentLocationCoords,
      tilt: document.getElementById("pv-tilt").value,
      azimuth: document.getElementById("pv-azimuth").value,
      pvgisData: pvgisMonthlyData, // Include PVGIS data if available
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
      config.pv.location || "Riga, Latvia";
    document.getElementById("pv-tilt").value = config.pv.tilt || 15;
    document.getElementById("pv-azimuth").value = config.pv.azimuth || 20;

    // If location coordinates are saved, restore them
    if (config.pv.location_coords) {
      currentLocationCoords = config.pv.location_coords;
    }
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
// Initialize address autocomplete
function initializeAddressAutocomplete() {
  const locationInput = document.getElementById("pv-location");
  const suggestionsDiv = document.getElementById("address-suggestions");
  const statusSpan = document.getElementById("location-status");

  // Search for addresses as user types
  locationInput.addEventListener("input", async function () {
    const query = locationInput.value.trim();

    if (query.length < 3) {
      suggestionsDiv.classList.remove("show");
      return;
    }

    // Debounce search
    clearTimeout(addressSearchTimeout);
    addressSearchTimeout = setTimeout(async () => {
      try {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
            query
          )}&limit=5`,
          {
            headers: {
              "User-Agent": "PV Calculator Web App",
            },
          }
        );
        const results = await response.json();

        if (results.length > 0) {
          suggestionsDiv.innerHTML = results
            .map(
              (result) => `
            <div class="suggestion-item" data-lat="${result.lat}" data-lon="${result.lon}" data-name="${result.display_name}">
              ${result.display_name}
            </div>
          `
            )
            .join("");

          suggestionsDiv.classList.add("show");

          // Add click handlers
          document.querySelectorAll(".suggestion-item").forEach((item) => {
            item.addEventListener("click", function () {
              const lat = parseFloat(this.dataset.lat);
              const lon = parseFloat(this.dataset.lon);
              const name = this.dataset.name;

              currentLocationCoords = { lat, lon, name };
              locationInput.value = name;
              suggestionsDiv.classList.remove("show");

              statusSpan.innerHTML =
                '<i class="fas fa-check-circle" style="color: green;"></i> Location set';

              // Automatically fetch PVGIS data
              fetchPVGISDataAuto();
            });
          });
        } else {
          suggestionsDiv.classList.remove("show");
        }
      } catch (error) {
        console.error("Address search error:", error);
        suggestionsDiv.classList.remove("show");
      }
    }, 500);
  });

  // Close suggestions when clicking outside
  document.addEventListener("click", function (e) {
    if (
      !locationInput.contains(e.target) &&
      !suggestionsDiv.contains(e.target)
    ) {
      suggestionsDiv.classList.remove("show");
    }
  });

  // Fetch initial PVGIS data on load
  setTimeout(() => fetchPVGISDataAuto(), 1000);

  // Auto-refresh PVGIS data when PV parameters change
  ["pv-size", "pv-tilt", "pv-azimuth"].forEach((id) => {
    document.getElementById(id).addEventListener("change", () => {
      fetchPVGISDataAuto();
    });
  });
}

// Automatic PVGIS data fetch (no button, runs in background)
// PVGIS: Photovoltaic Geographical Information System
// © European Union, Joint Research Centre (JRC)
// More info: https://re.jrc.ec.europa.eu/pvg_tools/en/
async function fetchPVGISDataAuto() {
  const statusDiv = document.getElementById("solar-data-source");
  statusDiv.innerHTML =
    '<i class="fas fa-spinner fa-spin"></i> Fetching solar data from PVGIS...';

  try {
    const pvSize = parseFloat(document.getElementById("pv-size").value) || 5.0;
    const tilt = parseFloat(document.getElementById("pv-tilt").value) || 35;
    const azimuth =
      parseFloat(document.getElementById("pv-azimuth").value) || 0;

    const coords = currentLocationCoords;

    // Construct PVGIS API URL with CORS proxy
    // PVGIS API documentation: https://joint-research-centre.ec.europa.eu/pvgis-photovoltaic-geographical-information-system/getting-started-pvgis/api-non-interactive-service_en
    const pvgisUrl = `https://re.jrc.ec.europa.eu/api/v5_2/PVcalc?lat=${coords.lat}&lon=${coords.lon}&peakpower=${pvSize}&loss=14&angle=${tilt}&aspect=${azimuth}&outputformat=json`;

    // Try with CORS proxy first
    const corsProxy = "https://corsproxy.io/?";
    const apiUrl = corsProxy + encodeURIComponent(pvgisUrl);

    const response = await fetch(apiUrl);
    if (!response.ok) {
      throw new Error("PVGIS API request failed");
    }

    const data = await response.json();

    if (data.outputs && data.outputs.totals && data.outputs.monthly) {
      const annualProduction = data.outputs.totals.fixed.E_y;
      const avgDaily = annualProduction / 365;

      // Store monthly data for calculations
      pvgisMonthlyData = {
        monthly: data.outputs.monthly.fixed.map((m) => ({
          month: m.month,
          E_m: m.E_m, // Monthly energy output (kWh)
          H_sun: m.H_sun, // Average daily sun hours
          E_d: m.E_d, // Average daily energy (kWh)
        })),
        annualProduction: annualProduction,
        systemSize: pvSize,
        location: currentLocationCoords,
      };

      statusDiv.innerHTML = `✅ Using: PVGIS Real Data - Annual: ${annualProduction.toFixed(
        0
      )} kWh/year, Daily Avg: ${avgDaily.toFixed(1)} kWh/day`;

      showToast(
        `PVGIS data fetched! Annual production: ${annualProduction.toFixed(
          0
        )} kWh`,
        "success"
      );
    } else {
      throw new Error("Invalid PVGIS response");
    }
  } catch (error) {
    // Fallback to built-in solar model
    console.log("PVGIS fetch failed, using built-in solar model:", error);

    // Clear PVGIS data to force fallback to built-in model
    pvgisMonthlyData = null;

    const coords = currentLocationCoords;
    const pvSize = parseFloat(document.getElementById("pv-size").value) || 5.0;
    const tilt = parseFloat(document.getElementById("pv-tilt").value) || 35;
    const azimuth =
      parseFloat(document.getElementById("pv-azimuth").value) || 0;

    const pvgisManualUrl = `https://re.jrc.ec.europa.eu/pvg_tools/en/#PVP?lat=${coords.lat}&lon=${coords.lon}&peakpower=${pvSize}&loss=14&angle=${tilt}&aspect=${azimuth}`;

    statusDiv.innerHTML =
      `📊 Using: Built-in solar model<br>` +
      `<small>For accurate data, visit: <a href="${pvgisManualUrl}" target="_blank">PVGIS Calculator</a></small>`;
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
