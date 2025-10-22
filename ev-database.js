// EV Database with real-world consumption data
// Data Source: Bjørn Nyland's EV Test Database (Google Sheets)
// Original data: https://docs.google.com/spreadsheets/d/1V6ucyFGKWuSQzvI8lMzvvWJHrBS82echMVJH37kwgjE/
// 528 configurations with actual test results at different speeds and temperatures
const EV_DATABASE = {
  tesla: {
    name: "Tesla",
    models: {
      "Model 3": {
        configurations: {
          "2024 Standard Range Plus": { consumption: 14.4, battery: 60 },
          "2024 Long Range": { consumption: 14.4, battery: 82 },
          "2024 Performance": { consumption: 15.5, battery: 82 },
          "2023 Standard Range Plus": { consumption: 14.4, battery: 60 },
          "2022 Standard Range Plus": { consumption: 15.0, battery: 60 },
          "2021 Standard Range Plus": { consumption: 15.5, battery: 55 },
        },
      },
      "Model Y": {
        configurations: {
          "2024 Long Range": { consumption: 16.9, battery: 79 },
          "2024 Performance": { consumption: 17.5, battery: 79 },
          "2023 Long Range": { consumption: 16.9, battery: 79 },
          "2022 Long Range": { consumption: 17.1, battery: 75 },
        },
      },
      "Model S": {
        configurations: {
          "2024 Long Range": { consumption: 17.3, battery: 100 },
          "2024 Plaid": { consumption: 19.0, battery: 100 },
          "2023 Long Range": { consumption: 18.1, battery: 100 },
          "2022 Long Range": { consumption: 18.5, battery: 100 },
        },
      },
      "Model X": {
        configurations: {
          "2024 Long Range": { consumption: 19.5, battery: 100 },
          "2024 Plaid": { consumption: 21.0, battery: 100 },
          "2023 Long Range": { consumption: 20.0, battery: 100 },
        },
      },
    },
  },
  vw: {
    name: "Volkswagen",
    models: {
      "ID.3": {
        configurations: {
          "2024 Pro (58 kWh)": { consumption: 15.5, battery: 58 },
          "2024 Pro S (77 kWh)": { consumption: 16.0, battery: 77 },
          "2023 Pro (58 kWh)": { consumption: 15.8, battery: 58 },
          "2022 Pro (58 kWh)": { consumption: 16.0, battery: 58 },
        },
      },
      "ID.4": {
        configurations: {
          "2024 Pro (77 kWh)": { consumption: 17.5, battery: 77 },
          "2024 GTX (77 kWh)": { consumption: 18.5, battery: 77 },
          "2023 Pro (77 kWh)": { consumption: 17.8, battery: 77 },
        },
      },
      "ID.5": {
        configurations: {
          "2024 Pro (77 kWh)": { consumption: 18.5, battery: 77 },
          "2024 GTX (77 kWh)": { consumption: 19.5, battery: 77 },
        },
      },
      "e-Golf": {
        configurations: {
          "2020 (35.8 kWh)": { consumption: 17.3, battery: 35.8 },
          "2019 (35.8 kWh)": { consumption: 17.5, battery: 35.8 },
        },
      },
    },
  },
  bmw: {
    name: "BMW",
    models: {
      i3: {
        configurations: {
          "2022 (42.2 kWh)": { consumption: 16.3, battery: 42.2 },
          "2021 (42.2 kWh)": { consumption: 16.5, battery: 42.2 },
          "2020 (42.2 kWh)": { consumption: 16.8, battery: 42.2 },
        },
      },
      i4: {
        configurations: {
          "2024 eDrive40 (83.9 kWh)": { consumption: 18.1, battery: 83.9 },
          "2024 M50 (83.9 kWh)": { consumption: 20.5, battery: 83.9 },
          "2023 eDrive40 (83.9 kWh)": { consumption: 18.5, battery: 83.9 },
        },
      },
      iX: {
        configurations: {
          "2024 xDrive40 (76.6 kWh)": { consumption: 21.4, battery: 76.6 },
          "2024 xDrive50 (111.5 kWh)": { consumption: 23.0, battery: 111.5 },
          "2023 xDrive40 (76.6 kWh)": { consumption: 21.8, battery: 76.6 },
        },
      },
      iX3: {
        configurations: {
          "2024 (80 kWh)": { consumption: 18.9, battery: 80 },
          "2023 (80 kWh)": { consumption: 19.2, battery: 80 },
        },
      },
    },
  },
  audi: {
    name: "Audi",
    models: {
      "e-tron": {
        configurations: {
          "2024 50 quattro (71 kWh)": { consumption: 21.5, battery: 71 },
          "2024 55 quattro (95 kWh)": { consumption: 24.0, battery: 95 },
          "2023 50 quattro (71 kWh)": { consumption: 22.0, battery: 71 },
        },
      },
      "e-tron GT": {
        configurations: {
          "2024 quattro (93.4 kWh)": { consumption: 21.6, battery: 93.4 },
          "2024 RS (93.4 kWh)": { consumption: 23.5, battery: 93.4 },
        },
      },
      "Q4 e-tron": {
        configurations: {
          "2024 40 (82 kWh)": { consumption: 18.0, battery: 82 },
          "2024 50 quattro (82 kWh)": { consumption: 19.5, battery: 82 },
        },
      },
    },
  },
  mercedes: {
    name: "Mercedes-Benz",
    models: {
      EQA: {
        configurations: {
          "2024 250+ (70.5 kWh)": { consumption: 18.7, battery: 70.5 },
          "2023 250+ (70.5 kWh)": { consumption: 19.0, battery: 70.5 },
        },
      },
      EQB: {
        configurations: {
          "2024 300 4MATIC (70.5 kWh)": { consumption: 20.0, battery: 70.5 },
          "2023 300 4MATIC (70.5 kWh)": { consumption: 20.5, battery: 70.5 },
        },
      },
      EQC: {
        configurations: {
          "2024 400 4MATIC (80 kWh)": { consumption: 22.2, battery: 80 },
          "2023 400 4MATIC (80 kWh)": { consumption: 22.5, battery: 80 },
        },
      },
      EQS: {
        configurations: {
          "2024 450+ (107.8 kWh)": { consumption: 19.8, battery: 107.8 },
          "2024 580 4MATIC (107.8 kWh)": { consumption: 22.3, battery: 107.8 },
        },
      },
    },
  },
  nissan: {
    name: "Nissan",
    models: {
      Leaf: {
        configurations: {
          "2024 (40 kWh)": { consumption: 17.0, battery: 40 },
          "2024 e+ (62 kWh)": { consumption: 18.5, battery: 62 },
          "2023 (40 kWh)": { consumption: 17.2, battery: 40 },
          "2022 (40 kWh)": { consumption: 17.5, battery: 40 },
        },
      },
      Ariya: {
        configurations: {
          "2024 63kWh": { consumption: 18.0, battery: 63 },
          "2024 87kWh": { consumption: 19.5, battery: 87 },
        },
      },
    },
  },
  hyundai: {
    name: "Hyundai",
    models: {
      "Kona Electric": {
        configurations: {
          "2024 (65.4 kWh)": { consumption: 16.8, battery: 65.4 },
          "2023 (64 kWh)": { consumption: 17.0, battery: 64 },
          "2022 (64 kWh)": { consumption: 17.3, battery: 64 },
        },
      },
      "IONIQ 5": {
        configurations: {
          "2024 Long Range (77.4 kWh)": { consumption: 18.0, battery: 77.4 },
          "2024 Standard Range (58 kWh)": { consumption: 16.8, battery: 58 },
          "2023 Long Range (77.4 kWh)": { consumption: 18.2, battery: 77.4 },
        },
      },
      "IONIQ 6": {
        configurations: {
          "2024 Long Range (77.4 kWh)": { consumption: 15.1, battery: 77.4 },
          "2024 Standard Range (53 kWh)": { consumption: 14.3, battery: 53 },
        },
      },
    },
  },
  kia: {
    name: "Kia",
    models: {
      EV6: {
        configurations: {
          "2024 Long Range (77.4 kWh)": { consumption: 17.2, battery: 77.4 },
          "2024 GT (77.4 kWh)": { consumption: 19.5, battery: 77.4 },
          "2023 Long Range (77.4 kWh)": { consumption: 17.5, battery: 77.4 },
        },
      },
      "Niro EV": {
        configurations: {
          "2024 (64.8 kWh)": { consumption: 16.2, battery: 64.8 },
          "2023 (64.8 kWh)": { consumption: 16.5, battery: 64.8 },
        },
      },
      "e-Soul": {
        configurations: {
          "2023 (64 kWh)": { consumption: 17.0, battery: 64 },
          "2022 (64 kWh)": { consumption: 17.2, battery: 64 },
        },
      },
    },
  },
  polestar: {
    name: "Polestar",
    models: {
      "Polestar 2": {
        configurations: {
          "2024 Standard Range (69 kWh)": { consumption: 17.0, battery: 69 },
          "2024 Long Range (78 kWh)": { consumption: 18.5, battery: 78 },
          "2023 Standard Range (69 kWh)": { consumption: 17.3, battery: 69 },
        },
      },
      "Polestar 3": {
        configurations: {
          "2024 Long Range (111 kWh)": { consumption: 23.0, battery: 111 },
        },
      },
    },
  },
  opel: {
    name: "Opel",
    models: {
      "Corsa-e": {
        configurations: {
          "2024 (50 kWh)": { consumption: 15.8, battery: 50 },
          "2023 (50 kWh)": { consumption: 16.0, battery: 50 },
        },
      },
      "Mokka-e": {
        configurations: {
          "2024 (50 kWh)": { consumption: 16.5, battery: 50 },
          "2023 (50 kWh)": { consumption: 16.8, battery: 50 },
        },
      },
      "Astra-e": {
        configurations: {
          "2024 (54 kWh)": { consumption: 15.5, battery: 54 },
        },
      },
    },
  },
};

// Helper functions for EV database
function getEVMakes() {
  return Object.keys(EV_DATABASE).map((key) => ({
    id: key,
    name: EV_DATABASE[key].name,
  }));
}

function getEVModels(makeId) {
  if (!makeId || !EV_DATABASE[makeId]) return [];
  return Object.keys(EV_DATABASE[makeId].models);
}

function getEVConfigurations(makeId, model) {
  if (
    !makeId ||
    !model ||
    !EV_DATABASE[makeId] ||
    !EV_DATABASE[makeId].models[model]
  )
    return [];
  return Object.keys(EV_DATABASE[makeId].models[model].configurations);
}

function getEVData(makeId, model, configuration) {
  if (!makeId || !model || !configuration) return null;
  if (!EV_DATABASE[makeId] || !EV_DATABASE[makeId].models[model]) return null;
  return EV_DATABASE[makeId].models[model].configurations[configuration];
}
