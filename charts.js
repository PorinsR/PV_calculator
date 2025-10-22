// PV Calculator - Chart Visualization

// Store chart instances to destroy them before creating new ones
let chartInstances = {};

function destroyChart(chartId) {
  if (chartInstances[chartId]) {
    chartInstances[chartId].destroy();
    delete chartInstances[chartId];
  }
}

function destroyAllCharts() {
  Object.keys(chartInstances).forEach((id) => destroyChart(id));
}

// Display daily energy flow chart
function displayDailyFlowChart(data) {
  const container = document.getElementById("results-container");

  // Clear previous results
  container.innerHTML = "";

  // Create chart container
  const chartDiv = document.createElement("div");
  chartDiv.className = "chart-container";
  chartDiv.innerHTML = `
        <h3>Daily Energy Flow - ${new Date().toLocaleDateString()}</h3>
        <div class="chart-wrapper">
            <canvas id="dailyFlowChart"></canvas>
        </div>
    `;
  container.appendChild(chartDiv);

  // Create summary cards
  const summaryDiv = document.createElement("div");
  summaryDiv.className = "summary-grid";
  summaryDiv.innerHTML = `
        <div class="summary-card">
            <h4>Total Consumption</h4>
            <div class="value">${data.totals.consumption.toFixed(
              1
            )}<span class="unit">kWh</span></div>
        </div>
        <div class="summary-card">
            <h4>Solar Generation</h4>
            <div class="value">${data.totals.generation.toFixed(
              1
            )}<span class="unit">kWh</span></div>
        </div>
        <div class="summary-card">
            <h4>Grid Import</h4>
            <div class="value">${data.totals.gridImport.toFixed(
              1
            )}<span class="unit">kWh</span></div>
        </div>
        <div class="summary-card">
            <h4>Grid Export</h4>
            <div class="value">${data.totals.gridExport.toFixed(
              1
            )}<span class="unit">kWh</span></div>
        </div>
        <div class="summary-card">
            <h4>Self-Sufficiency</h4>
            <div class="value">${data.totals.selfSufficiency.toFixed(
              1
            )}<span class="unit">%</span></div>
        </div>
        <div class="summary-card">
            <h4>Battery SOC (End)</h4>
            <div class="value">${data.batterySoc[23].toFixed(
              0
            )}<span class="unit">%</span></div>
        </div>
    `;
  container.appendChild(summaryDiv);

  // Create chart
  destroyChart("dailyFlowChart");
  const ctx = document.getElementById("dailyFlowChart").getContext("2d");
  chartInstances["dailyFlowChart"] = new Chart(ctx, {
    type: "line",
    data: {
      labels: data.hours.map((h) => `${h}:00`),
      datasets: [
        {
          label: "Consumption",
          data: data.consumption,
          borderColor: "#f44336",
          backgroundColor: "rgba(244, 67, 54, 0.1)",
          borderWidth: 2,
          tension: 0.4,
        },
        {
          label: "Solar Generation",
          data: data.generation,
          borderColor: "#FF9800",
          backgroundColor: "rgba(255, 152, 0, 0.1)",
          borderWidth: 2,
          tension: 0.4,
        },
        {
          label: "Grid Import",
          data: data.gridImport,
          borderColor: "#9C27B0",
          backgroundColor: "rgba(156, 39, 176, 0.1)",
          borderWidth: 2,
          tension: 0.4,
        },
        {
          label: "Grid Export",
          data: data.gridExport,
          borderColor: "#4CAF50",
          backgroundColor: "rgba(76, 175, 80, 0.1)",
          borderWidth: 2,
          tension: 0.4,
        },
        {
          label: "Battery SOC (%)",
          data: data.batterySoc,
          borderColor: "#2196F3",
          backgroundColor: "rgba(33, 150, 243, 0.1)",
          borderWidth: 2,
          yAxisID: "y1",
          tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false,
      },
      scales: {
        y: {
          type: "linear",
          display: true,
          position: "left",
          title: {
            display: true,
            text: "Power (kW)",
          },
        },
        y1: {
          type: "linear",
          display: true,
          position: "right",
          title: {
            display: true,
            text: "Battery SOC (%)",
          },
          min: 0,
          max: 100,
          grid: {
            drawOnChartArea: false,
          },
        },
      },
      plugins: {
        legend: {
          display: true,
          position: "top",
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              let label = context.dataset.label || "";
              if (label) {
                label += ": ";
              }
              if (context.parsed.y !== null) {
                if (context.dataset.yAxisID === "y1") {
                  label += context.parsed.y.toFixed(1) + "%";
                } else {
                  label += context.parsed.y.toFixed(2) + " kW";
                }
              }
              return label;
            },
          },
        },
      },
    },
  });
}

// Display annual analysis chart
function displayAnnualAnalysisChart(data) {
  const container = document.getElementById("results-container");
  container.innerHTML = "";

  // Create multiple charts

  // 1. Monthly Generation vs Consumption
  const chartDiv1 = document.createElement("div");
  chartDiv1.className = "chart-container";
  chartDiv1.innerHTML = `
        <h3>Monthly Energy Balance</h3>
        <div class="chart-wrapper">
            <canvas id="monthlyEnergyChart"></canvas>
        </div>
    `;
  container.appendChild(chartDiv1);

  destroyChart("monthlyEnergyChart");
  const ctx1 = document.getElementById("monthlyEnergyChart").getContext("2d");
  chartInstances["monthlyEnergyChart"] = new Chart(ctx1, {
    type: "bar",
    data: {
      labels: data.months,
      datasets: [
        {
          label: "Generation",
          data: data.monthlyGeneration,
          backgroundColor: "rgba(255, 152, 0, 0.7)",
          borderColor: "#FF9800",
          borderWidth: 1,
        },
        {
          label: "Consumption",
          data: data.monthlyConsumption,
          backgroundColor: "rgba(244, 67, 54, 0.7)",
          borderColor: "#f44336",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Energy (kWh)",
          },
        },
      },
      plugins: {
        legend: {
          display: true,
          position: "top",
        },
      },
    },
  });

  // 2. Monthly Self-Sufficiency
  const chartDiv2 = document.createElement("div");
  chartDiv2.className = "chart-container";
  chartDiv2.innerHTML = `
        <h3>Monthly Self-Sufficiency</h3>
        <div class="chart-wrapper">
            <canvas id="monthlySelfSuffChart"></canvas>
        </div>
    `;
  container.appendChild(chartDiv2);

  destroyChart("monthlySelfSuffChart");
  const ctx2 = document.getElementById("monthlySelfSuffChart").getContext("2d");
  chartInstances["monthlySelfSuffChart"] = new Chart(ctx2, {
    type: "line",
    data: {
      labels: data.months,
      datasets: [
        {
          label: "Self-Sufficiency (%)",
          data: data.monthlySelfSufficiency,
          borderColor: "#4CAF50",
          backgroundColor: "rgba(76, 175, 80, 0.2)",
          borderWidth: 3,
          fill: true,
          tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          title: {
            display: true,
            text: "Self-Sufficiency (%)",
          },
        },
      },
      plugins: {
        legend: {
          display: true,
          position: "top",
        },
      },
    },
  });

  // 3. Annual Summary
  const summaryDiv = document.createElement("div");
  summaryDiv.className = "chart-container";
  summaryDiv.innerHTML = `
        <h3>Annual Summary</h3>
        <div class="summary-grid">
            <div class="summary-card">
                <h4>Total Generation</h4>
                <div class="value">${data.annualTotals.generation.toFixed(
                  0
                )}<span class="unit">kWh/year</span></div>
            </div>
            <div class="summary-card">
                <h4>Total Consumption</h4>
                <div class="value">${data.annualTotals.consumption.toFixed(
                  0
                )}<span class="unit">kWh/year</span></div>
            </div>
            <div class="summary-card">
                <h4>Grid Import</h4>
                <div class="value">${data.annualTotals.gridImport.toFixed(
                  0
                )}<span class="unit">kWh/year</span></div>
            </div>
            <div class="summary-card">
                <h4>Grid Export</h4>
                <div class="value">${data.annualTotals.gridExport.toFixed(
                  0
                )}<span class="unit">kWh/year</span></div>
            </div>
            <div class="summary-card">
                <h4>Annual Cost</h4>
                <div class="value">€${data.annualTotals.cost.toFixed(
                  2
                )}<span class="unit">/year</span></div>
            </div>
            <div class="summary-card">
                <h4>Annual Savings</h4>
                <div class="value">€${data.annualTotals.savings.toFixed(
                  2
                )}<span class="unit">/year</span></div>
            </div>
            <div class="summary-card">
                <h4>Avg Self-Sufficiency</h4>
                <div class="value">${data.annualTotals.selfSufficiency.toFixed(
                  1
                )}<span class="unit">%</span></div>
            </div>
        </div>
    `;
  container.appendChild(summaryDiv);
}

// Display energy distribution chart
function displayEnergyDistributionChart(data) {
  const container = document.getElementById("results-container");
  container.innerHTML = "";

  const chartDiv = document.createElement("div");
  chartDiv.className = "chart-container";
  chartDiv.innerHTML = `
        <h3>Annual Energy Flow Distribution</h3>
        <div class="chart-wrapper">
            <canvas id="energyDistChart"></canvas>
        </div>
    `;
  container.appendChild(chartDiv);

  destroyChart("energyDistChart");
  const ctx = document.getElementById("energyDistChart").getContext("2d");
  chartInstances["energyDistChart"] = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: data.labels,
      datasets: [
        {
          data: data.values,
          backgroundColor: [
            "rgba(76, 175, 80, 0.8)",
            "rgba(33, 150, 243, 0.8)",
            "rgba(255, 152, 0, 0.8)",
            "rgba(156, 39, 176, 0.8)",
          ],
          borderColor: ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0"],
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: "right",
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              let label = context.label || "";
              if (label) {
                label += ": ";
              }
              label += context.parsed.toFixed(1) + " kWh";
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = ((context.parsed / total) * 100).toFixed(1);
              label += ` (${percentage}%)`;
              return label;
            },
          },
        },
      },
    },
  });

  // Add summary
  const summaryDiv = document.createElement("div");
  summaryDiv.className = "summary-grid";
  summaryDiv.innerHTML = `
        <div class="summary-card">
            <h4>Direct Self-Consumption</h4>
            <div class="value">${data.values[0].toFixed(
              0
            )}<span class="unit">kWh</span></div>
        </div>
        <div class="summary-card">
            <h4>Battery Storage</h4>
            <div class="value">${data.values[1].toFixed(
              0
            )}<span class="unit">kWh</span></div>
        </div>
        <div class="summary-card">
            <h4>Grid Export</h4>
            <div class="value">${data.values[2].toFixed(
              0
            )}<span class="unit">kWh</span></div>
        </div>
        <div class="summary-card">
            <h4>Grid Import</h4>
            <div class="value">${data.values[3].toFixed(
              0
            )}<span class="unit">kWh</span></div>
        </div>
    `;
  container.appendChild(summaryDiv);
}

// Display cumulative payback chart
function displayCumulativePaybackChart(data) {
  const container = document.getElementById("results-container");
  container.innerHTML = "";

  const chartDiv = document.createElement("div");
  chartDiv.className = "chart-container";
  chartDiv.innerHTML = `
        <h3>20-Year Cumulative Cost Comparison</h3>
        <div class="chart-wrapper">
            <canvas id="paybackChart"></canvas>
        </div>
    `;
  container.appendChild(chartDiv);

  destroyChart("paybackChart");
  const ctx = document.getElementById("paybackChart").getContext("2d");

  // Build datasets only for enabled scenarios
  const datasets = [];

  // Always include baseline
  if (data.scenarios.noPV) {
    datasets.push({
      label: data.scenarios.noPV.label,
      data: data.scenarios.noPV.costs,
      borderColor: "#f44336",
      backgroundColor: "rgba(244, 67, 54, 0.1)",
      borderWidth: 3,
      tension: 0.1,
    });
  }

  // Only include PV Only if it exists
  if (data.scenarios.pvOnly && data.scenarios.pvOnly.enabled) {
    datasets.push({
      label: data.scenarios.pvOnly.label,
      data: data.scenarios.pvOnly.costs,
      borderColor: "#FF9800",
      backgroundColor: "rgba(255, 152, 0, 0.1)",
      borderWidth: 3,
      tension: 0.1,
    });
  }

  // Only include PV+Battery if it exists
  if (data.scenarios.pvBattery && data.scenarios.pvBattery.enabled) {
    datasets.push({
      label: data.scenarios.pvBattery.label,
      data: data.scenarios.pvBattery.costs,
      borderColor: "#4CAF50",
      backgroundColor: "rgba(76, 175, 80, 0.1)",
      borderWidth: 3,
      tension: 0.1,
    });
  }

  chartInstances["paybackChart"] = new Chart(ctx, {
    type: "line",
    data: {
      labels: data.years,
      datasets: datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Cumulative Cost (EUR)",
          },
        },
        x: {
          title: {
            display: true,
            text: "Years",
          },
        },
      },
      plugins: {
        legend: {
          display: true,
          position: "top",
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              let label = context.dataset.label || "";
              if (label) {
                label += ": ";
              }
              label += "€" + context.parsed.y.toFixed(0);
              return label;
            },
          },
        },
      },
    },
  });

  // Add breakeven info
  const infoDiv = document.createElement("div");
  infoDiv.className = "chart-container";
  infoDiv.innerHTML = `
        <h3>Breakeven Analysis</h3>
        <div class="summary-grid">
            <div class="summary-card">
                <h4>PV Only Breakeven</h4>
                <div class="value">${
                  data.breakeven.pvOnly
                }<span class="unit">years</span></div>
            </div>
            <div class="summary-card">
                <h4>PV + Battery Breakeven</h4>
                <div class="value">${
                  data.breakeven.pvBattery
                }<span class="unit">years</span></div>
            </div>
            <div class="summary-card">
                <h4>20-Year Savings (PV Only)</h4>
                <div class="value">€${(
                  data.scenarios.noPV.costs[20] -
                  data.scenarios.pvOnly.costs[20]
                ).toFixed(0)}</div>
            </div>
            <div class="summary-card">
                <h4>20-Year Savings (PV+Battery)</h4>
                <div class="value">€${(
                  data.scenarios.noPV.costs[20] -
                  data.scenarios.pvBattery.costs[20]
                ).toFixed(0)}</div>
            </div>
        </div>
    `;
  container.appendChild(infoDiv);
}

// Display summary report
function displaySummaryReport(data) {
  const container = document.getElementById("results-container");
  container.innerHTML = "";

  const reportDiv = document.createElement("div");
  reportDiv.className = "chart-container";

  let htmlContent = `<h3>Detailed Scenario Comparison Report</h3>`;

  // Always show baseline
  htmlContent += `
        <h4 style="margin-top: 20px; color: #f44336;">Scenario 1: No PV System</h4>
        <table>
            <tr>
                <td><strong>Annual Cost:</strong></td>
                <td>€${data.scenarios.noPV.annualCost.toFixed(2)}/year</td>
            </tr>
            <tr>
                <td><strong>20-Year Total Cost:</strong></td>
                <td>€${data.scenarios.noPV.twentyYearCost.toFixed(0)}</td>
            </tr>
            <tr>
                <td><strong>Self-Sufficiency:</strong></td>
                <td>${data.scenarios.noPV.selfSufficiency.toFixed(1)}%</td>
            </tr>
            <tr>
                <td><strong>Grid Dependency:</strong></td>
                <td>${data.scenarios.noPV.gridDependency.toFixed(1)}%</td>
            </tr>
        </table>
  `;

  // Only show PV Only if enabled
  if (data.scenarios.pvOnly && data.scenarios.pvOnly.enabled) {
    htmlContent += `
        <h4 style="margin-top: 20px; color: #FF9800;">Scenario 2: PV Only</h4>
        <table>
            <tr>
                <td><strong>Initial Investment:</strong></td>
                <td>€${data.scenarios.pvOnly.initialInvestment.toFixed(0)}</td>
            </tr>
            <tr>
                <td><strong>Annual Cost:</strong></td>
                <td>€${data.scenarios.pvOnly.annualCost.toFixed(2)}/year</td>
            </tr>
            <tr>
                <td><strong>Annual Savings:</strong></td>
                <td>€${data.scenarios.pvOnly.annualSavings.toFixed(2)}/year</td>
            </tr>
            <tr>
                <td><strong>20-Year Total Cost:</strong></td>
                <td>€${data.scenarios.pvOnly.twentyYearCost.toFixed(0)}</td>
            </tr>
            <tr>
                <td><strong>Breakeven Period:</strong></td>
                <td>${data.scenarios.pvOnly.breakeven} years</td>
            </tr>
            <tr>
                <td><strong>Self-Sufficiency:</strong></td>
                <td>${data.scenarios.pvOnly.selfSufficiency.toFixed(1)}%</td>
            </tr>
            <tr>
                <td><strong>Grid Dependency:</strong></td>
                <td>${data.scenarios.pvOnly.gridDependency.toFixed(1)}%</td>
            </tr>
            <tr style="background-color: #e8f5e9;">
                <td><strong>20-Year Savings vs No PV:</strong></td>
                <td><strong>€${(
                  data.scenarios.noPV.twentyYearCost -
                  data.scenarios.pvOnly.twentyYearCost
                ).toFixed(0)}</strong></td>
            </tr>
        </table>
    `;
  }

  // Only show PV+Battery if enabled
  if (data.scenarios.pvBattery && data.scenarios.pvBattery.enabled) {
    htmlContent += `
        <h4 style="margin-top: 20px; color: #4CAF50;">Scenario 3: PV + Battery</h4>
        <table>
            <tr>
                <td><strong>Initial Investment:</strong></td>
                <td>€${data.scenarios.pvBattery.initialInvestment.toFixed(
                  0
                )}</td>
            </tr>
            <tr>
                <td><strong>Annual Cost:</strong></td>
                <td>€${data.scenarios.pvBattery.annualCost.toFixed(2)}/year</td>
            </tr>
            <tr>
                <td><strong>Annual Savings:</strong></td>
                <td>€${data.scenarios.pvBattery.annualSavings.toFixed(
                  2
                )}/year</td>
            </tr>
            <tr>
                <td><strong>20-Year Total Cost:</strong></td>
                <td>€${data.scenarios.pvBattery.twentyYearCost.toFixed(0)}</td>
            </tr>
            <tr>
                <td><strong>Breakeven Period:</strong></td>
                <td>${data.scenarios.pvBattery.breakeven} years</td>
            </tr>
            <tr>
                <td><strong>Self-Sufficiency:</strong></td>
                <td>${data.scenarios.pvBattery.selfSufficiency.toFixed(1)}%</td>
            </tr>
            <tr>
                <td><strong>Grid Dependency:</strong></td>
                <td>${data.scenarios.pvBattery.gridDependency.toFixed(1)}%</td>
            </tr>
            <tr style="background-color: #e8f5e9;">
                <td><strong>20-Year Savings vs No PV:</strong></td>
                <td><strong>€${(
                  data.scenarios.noPV.twentyYearCost -
                  data.scenarios.pvBattery.twentyYearCost
                ).toFixed(0)}</strong></td>
            </tr>`;

    // Only show comparison with PV Only if it also exists
    if (data.scenarios.pvOnly && data.scenarios.pvOnly.enabled) {
      htmlContent += `
            <tr style="background-color: #fff3e0;">
                <td><strong>Additional Savings vs PV Only:</strong></td>
                <td><strong>€${(
                  data.scenarios.pvOnly.twentyYearCost -
                  data.scenarios.pvBattery.twentyYearCost
                ).toFixed(0)}</strong></td>
            </tr>`;
    }

    htmlContent += `
        </table>
        
        <h4 style="margin-top: 20px;">Recommendation</h4>
        <div class="info-box ${
          data.scenarios.pvBattery.breakeven < 15 ? "success" : "info"
        }">
            <p><strong>${
              data.scenarios.pvBattery.breakeven < 15
                ? "✅ Highly Recommended"
                : "💡 Consider Carefully"
            }</strong></p>
            <p>
                ${
                  data.scenarios.pvBattery.breakeven < 15
                    ? `With a breakeven period of ${
                        data.scenarios.pvBattery.breakeven
                      } years, the PV+Battery system is financially attractive. 
                       You'll achieve ${data.scenarios.pvBattery.selfSufficiency.toFixed(
                         0
                       )}% self-sufficiency and save 
                       €${data.scenarios.pvBattery.annualSavings.toFixed(
                         0
                       )}/year.`
                    : `The breakeven period of ${
                        data.scenarios.pvBattery.breakeven
                      } years is relatively long. Consider starting with PV only 
                       (${
                         data.scenarios.pvOnly
                           ? data.scenarios.pvOnly.breakeven
                           : "N/A"
                       } year breakeven) and adding battery storage later when prices decrease.`
                }
            </p>
        </div>
    `;
  }

  reportDiv.innerHTML = htmlContent;
  container.appendChild(reportDiv);
}
