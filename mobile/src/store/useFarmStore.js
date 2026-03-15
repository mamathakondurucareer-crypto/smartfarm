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

const STORAGE_KEY = "smartfarm-data-v2";

const useFarmStore = create((set, get) => ({
  farm:       defaultFarmState(),
  simRunning: false,
  isLoaded:   false,

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

      return {
        farm: { ...state.farm, sensors: s, alerts: alerts.slice(0, 20), lastUpdated: Date.now() },
      };
    });
    get().persistToStorage();
  },

  // ─── AI ────────────────────────────────────────────────────────
  saveAIConversations: (messages) => {
    set((s) => ({ farm: { ...s.farm, aiConversations: messages.slice(-20) } }));
    get().persistToStorage();
  },
}));

// ─── Helpers ───────────────────────────────────────────────────────
const drift  = (range, bias = 0) => (Math.random() - 0.5) * range + bias;
const round  = (n, dp)           => +n.toFixed(dp);
const clamp  = (n, min, max, dp) => round(Math.max(min, Math.min(max, n)), dp);

export default useFarmStore;
