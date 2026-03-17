/**
 * Global state store — Zustand.
 *
 * Responsibilities:
 *  - Load / persist farm data via AsyncStorage
 *  - Sensor simulation tick (every 3s when active)
 *  - Mutations for AI conversations and automation toggles
 */
import { create } from "zustand";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { defaultFarmState } from "../data/defaultState";
import { api } from "../services/api";
import useAuthStore from "./useAuthStore";

const STORAGE_KEY = "smartfarm-data-v3";

// Map simulated sensor state to backend bulk-ingest readings.
// Device IDs match seeds/seed_prod.py SENSOR_DEVICES list.
function buildSensorReadings(s) {
  const now = new Date().toISOString();
  return [
    { device_id: 1,  parameter: "water_temp",       value: s.waterTemp,       unit: "°C",      recorded_at: now },
    { device_id: 1,  parameter: "dissolved_oxygen",  value: s.dissolvedO2,     unit: "mg/L",    recorded_at: now },
    { device_id: 1,  parameter: "ph",                value: s.ph,              unit: "pH",      recorded_at: now },
    { device_id: 1,  parameter: "ammonia",           value: s.ammonia,         unit: "mg/L",    recorded_at: now },
    { device_id: 7,  parameter: "air_temp",          value: s.ambientTemp,     unit: "°C",      recorded_at: now },
    { device_id: 7,  parameter: "humidity",          value: s.humidity,        unit: "%",       recorded_at: now },
    { device_id: 7,  parameter: "wind_speed",        value: s.windSpeed,       unit: "km/h",    recorded_at: now },
    { device_id: 7,  parameter: "solar_radiation",   value: s.solarRad,        unit: "W/m²",    recorded_at: now },
    { device_id: 8,  parameter: "air_temp",          value: s.ghTemp,          unit: "°C",      recorded_at: now },
    { device_id: 8,  parameter: "humidity",          value: s.ghHumidity,      unit: "%",       recorded_at: now },
    { device_id: 8,  parameter: "co2",               value: s.ghCO2,           unit: "ppm",     recorded_at: now },
    { device_id: 8,  parameter: "light_par",         value: s.ghLight,         unit: "μmol/m²s",recorded_at: now },
    { device_id: 10, parameter: "air_temp",          value: s.vfTemp,          unit: "°C",      recorded_at: now },
    { device_id: 10, parameter: "humidity",          value: s.vfHumidity,      unit: "%",       recorded_at: now },
    { device_id: 10, parameter: "nutrient_ec",       value: s.vfNutrientEC,    unit: "mS/cm",   recorded_at: now },
    { device_id: 10, parameter: "ph",                value: s.vfPH,            unit: "pH",      recorded_at: now },
    { device_id: 11, parameter: "solar_generation",  value: s.solarGeneration, unit: "kW",      recorded_at: now },
    { device_id: 11, parameter: "consumption",       value: s.farmConsumption, unit: "kW",      recorded_at: now },
    { device_id: 11, parameter: "grid_export",       value: s.gridExport,      unit: "kW",      recorded_at: now },
    { device_id: 12, parameter: "water_level",       value: s.reservoirLevel,  unit: "%",       recorded_at: now },
    { device_id: 12, parameter: "header_tank_level", value: s.headerTankLevel, unit: "%",       recorded_at: now },
    { device_id: 13, parameter: "egg_count",         value: s.eggCount,        unit: "count",   recorded_at: now },
    { device_id: 13, parameter: "feed_level",        value: s.feedLevel,       unit: "%",       recorded_at: now },
    { device_id: 13, parameter: "air_temp",          value: s.poultryTemp,     unit: "°C",      recorded_at: now },
    { device_id: 13, parameter: "ammonia_air",       value: s.poultryAmmonia,  unit: "ppm",     recorded_at: now },
    { device_id: 14, parameter: "soil_moisture",     value: s.soilMoisture,    unit: "%",       recorded_at: now },
    { device_id: 14, parameter: "soil_temp",         value: s.soilTemp,        unit: "°C",      recorded_at: now },
    { device_id: 14, parameter: "soil_ec",           value: s.soilEC,          unit: "mS/cm",   recorded_at: now },
  ].filter((r) => r.value !== null && r.value !== undefined && r.value !== 0 || r.parameter === "ph");
}

const useFarmStore = create((set, get) => ({
  farm:       defaultFarmState(),
  simRunning: false,
  isLoaded:   false,
  tickCount:  0,

  // ─── Storage ───────────────────────────────────────────────────
  loadFromStorage: async () => {
    try {
      const raw = await AsyncStorage.getItem(STORAGE_KEY);
      set({ farm: raw ? JSON.parse(raw) : defaultFarmState(), isLoaded: true });
    } catch {
      set({ isLoaded: true });
    }
  },

  persistToStorage: async () => {
    try {
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(get().farm));
    } catch {}
  },

  // ─── Simulation ────────────────────────────────────────────────
  toggleSimulation: () => set((s) => ({ simRunning: !s.simRunning })),

  tickSensors: () => {
    let updatedSensors = null;
    set((state) => {
      const s = { ...state.farm.sensors };

      // Gradually drift sensor values within realistic bounds
      s.waterTemp       = clamp(s.waterTemp       + drift(0.3),  15, 35, 1);
      s.dissolvedO2     = clamp(s.dissolvedO2     + drift(0.2, -0.02), 3.5, 8, 1);
      s.ph              = clamp(s.ph              + drift(0.05), 6, 9, 2);
      s.soilMoisture    = clamp(s.soilMoisture    + drift(2),    20, 60, 0);
      s.ghTemp          = clamp(s.ghTemp          + drift(0.5),  20, 45, 1);
      s.ghHumidity      = clamp(s.ghHumidity      + drift(2),    50, 95, 0);
      s.solarGeneration = clamp(s.solarGeneration + drift(5),    0,  120, 1);
      s.farmConsumption = round(s.solarGeneration * (0.6 + Math.random() * 0.2), 1);
      s.gridExport      = round(Math.max(0, s.solarGeneration - s.farmConsumption), 1);
      s.reservoirLevel  = clamp(s.reservoirLevel  + drift(0.5, -0.02), 30, 100, 0);
      s.eggCount        = Math.min(720, s.eggCount + Math.floor(Math.random() * 3));
      s.ambientTemp     = clamp(s.ambientTemp     + drift(0.4),  20, 45, 1);

      const alerts = [...state.farm.alerts];

      if (s.dissolvedO2 < 4.5 && !alerts.some((a) => a.msg.includes("CRITICAL DO"))) {
        alerts.unshift({ id: Date.now(), type: "danger", system: "Aquaculture", time: "Just now",
          msg: `CRITICAL DO level ${s.dissolvedO2} mg/L — emergency aeration activated` });
      }
      if (s.ghTemp > 37 && !alerts.some((a) => a.msg.includes("High temperature"))) {
        alerts.unshift({ id: Date.now() + 1, type: "warning", system: "Greenhouse", time: "Just now",
          msg: `High temperature in Greenhouse: ${s.ghTemp}°C — fan+pad activated` });
      }

      updatedSensors = s;
      const newTickCount = (state.tickCount || 0) + 1;
      return {
        farm: { ...state.farm, sensors: s, alerts: alerts.slice(0, 20), lastUpdated: Date.now() },
        tickCount: newTickCount,
      };
    });

    // Persist readings to backend every 20 ticks (~60 seconds at 3s interval)
    const tickCount = get().tickCount;
    if (tickCount % 20 === 0 && updatedSensors) {
      const token = useAuthStore.getState().token;
      if (token) {
        const readings = buildSensorReadings(updatedSensors);
        api.sensors.bulkIngest(token, readings).catch(() => {});
      }
    }

    get().persistToStorage();
  },

  // ─── AI ────────────────────────────────────────────────────────
  saveAIConversations: (messages) => {
    set((s) => ({ farm: { ...s.farm, aiConversations: messages.slice(-20) } }));
    get().persistToStorage();
  },

  // ─── Module toggles ────────────────────────────────────────────
  toggleModule: (name) => {
    set((s) => ({
      farm: { ...s.farm, enabledModules: { ...s.farm.enabledModules, [name]: !s.farm.enabledModules[name] } },
    }));
    get().persistToStorage();
  },

  // ─── Aquaculture ───────────────────────────────────────────────
  updatePond: (id, updates) => {
    set((s) => ({ farm: { ...s.farm, ponds: s.farm.ponds.map((p) => p.id === id ? { ...p, ...updates } : p) } }));
    get().persistToStorage();
  },
  addPond: (pond) => {
    set((s) => ({ farm: { ...s.farm, ponds: [...s.farm.ponds, pond] } }));
    get().persistToStorage();
  },
  removePond: (id) => {
    set((s) => ({ farm: { ...s.farm, ponds: s.farm.ponds.filter((p) => p.id !== id) } }));
    get().persistToStorage();
  },

  // ─── Greenhouse ────────────────────────────────────────────────
  updateGreenhouse: (id, updates) => {
    set((s) => ({ farm: { ...s.farm, greenhouse: s.farm.greenhouse.map((c) => c.id === id ? { ...c, ...updates } : c) } }));
    get().persistToStorage();
  },
  addGreenhouse: (crop) => {
    set((s) => ({ farm: { ...s.farm, greenhouse: [...s.farm.greenhouse, crop] } }));
    get().persistToStorage();
  },
  removeGreenhouse: (id) => {
    set((s) => ({ farm: { ...s.farm, greenhouse: s.farm.greenhouse.filter((c) => c.id !== id) } }));
    get().persistToStorage();
  },

  // ─── Vertical Farm ─────────────────────────────────────────────
  updateVerticalFarm: (crop, updates) => {
    set((s) => ({ farm: { ...s.farm, verticalFarm: s.farm.verticalFarm.map((v) => v.crop === crop ? { ...v, ...updates } : v) } }));
    get().persistToStorage();
  },
  addVerticalFarm: (batch) => {
    set((s) => ({ farm: { ...s.farm, verticalFarm: [...s.farm.verticalFarm, batch] } }));
    get().persistToStorage();
  },
  removeVerticalFarm: (crop) => {
    set((s) => ({ farm: { ...s.farm, verticalFarm: s.farm.verticalFarm.filter((v) => v.crop !== crop) } }));
    get().persistToStorage();
  },

  // ─── Poultry / Ducks / Bees / Nursery ─────────────────────────
  updatePoultry: (updates) => {
    set((s) => ({ farm: { ...s.farm, poultry: { ...s.farm.poultry, ...updates } } }));
    get().persistToStorage();
  },
  updateDucks: (updates) => {
    set((s) => ({ farm: { ...s.farm, ducks: { ...s.farm.ducks, ...updates } } }));
    get().persistToStorage();
  },
  updateBees: (updates) => {
    set((s) => ({ farm: { ...s.farm, bees: { ...s.farm.bees, ...updates } } }));
    get().persistToStorage();
  },
  updateNursery: (updates) => {
    set((s) => ({ farm: { ...s.farm, nursery: { ...s.farm.nursery, ...updates } } }));
    get().persistToStorage();
  },
}));

// ─── Helpers ───────────────────────────────────────────────────────
const drift  = (range, bias = 0) => (Math.random() - 0.5) * range + bias;
const round  = (n, dp)           => +n.toFixed(dp);
const clamp  = (n, min, max, dp) => round(Math.max(min, Math.min(max, n)), dp);

export default useFarmStore;
