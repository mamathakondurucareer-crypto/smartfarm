import { useState, useEffect, useCallback, useRef } from "react";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid, Legend, AreaChart, Area, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from "recharts";
import { Fish, Leaf, Egg, Sun, Droplets, Bot, TrendingUp, AlertTriangle, Thermometer, Wind, CloudRain, Activity, ChevronRight, Settings, Bell, Search, Menu, X, Plus, Minus, RefreshCw, Send, Zap, BarChart3, MapPin, Calendar, Users, Truck, Bug, Sprout, Home, Database, Brain, ShieldCheck, Expand, Clock, DollarSign, ChevronDown, ChevronUp, Check, Loader2, Wifi, WifiOff } from "lucide-react";

// ─── Color tokens ───
const T = {
  bg: "#0B1A14", card: "#122A1E", cardHover: "#1A3D2B", border: "#1E4D35",
  primary: "#2ECC71", primaryDim: "#27AE60", accent: "#F1C40F", accentDim: "#D4A843",
  danger: "#E74C3C", dangerDim: "#C0392B", warn: "#F39C12", info: "#3498DB",
  text: "#E8F5E9", textDim: "#8FAF9A", textMuted: "#5A7A66",
  water: "#2980B9", solar: "#F39C12", fish: "#1ABC9C", crop: "#27AE60",
  poultry: "#E67E22", market: "#9B59B6",
};

// ─── Storage helpers ───
const STORE_KEY = "smartfarm-data-v2";
const loadData = () => {
  try { const d = localStorage.getItem(STORE_KEY); return d ? JSON.parse(d) : null; } catch { return null; }
};
const saveData = (d) => {
  try { localStorage.setItem(STORE_KEY, JSON.stringify(d)); } catch {}
};

const defaultSensorData = () => ({
  waterTemp: 26.4, dissolvedO2: 6.2, ph: 7.4, ammonia: 0.01, turbidity: 12,
  soilMoisture: 42, soilTemp: 28.3, soilEC: 1.8,
  ghTemp: 32.1, ghHumidity: 72, ghCO2: 420, ghLight: 680,
  ambientTemp: 34.2, humidity: 65, windSpeed: 8.4, rainfall: 0, solarRad: 820,
  reservoirLevel: 78, headerTankLevel: 85,
  solarGeneration: 92.4, gridExport: 18.6, farmConsumption: 73.8,
  eggCount: 695, feedLevel: 62, poultryTemp: 28.5, poultryAmmonia: 8,
  vfTemp: 24.2, vfHumidity: 68, vfNutrientEC: 2.1, vfPH: 6.0,
});

const defaultFarmState = () => ({
  sensors: defaultSensorData(),
  alerts: [
    { id: 1, type: "warning", msg: "Pond P2 DO dropping — 4.8 mg/L", time: "10 min ago", system: "Aquaculture" },
    { id: 2, type: "info", msg: "Greenhouse 1 auto-ventilation activated", time: "25 min ago", system: "Greenhouse" },
    { id: 3, type: "success", msg: "Solar generation optimal — 92.4 kW", time: "1 hr ago", system: "Energy" },
    { id: 4, type: "info", msg: "Drone NDVI flight completed", time: "2 hr ago", system: "Technology" },
  ],
  ponds: [
    { id: "P1", species: "Murrel", stock: 3800, avgWeight: 0.62, fcr: 1.78, do: 5.8, mortality: 1.2, feedToday: 42 },
    { id: "P2", species: "Murrel", stock: 3750, avgWeight: 0.58, fcr: 1.82, do: 4.8, mortality: 1.5, feedToday: 40 },
    { id: "P3", species: "Rohu/Catla/Grass", stock: 5800, avgWeight: 0.45, fcr: 2.1, do: 6.5, mortality: 0.8, feedToday: 55 },
    { id: "P4", species: "Common/Rohu", stock: 5600, avgWeight: 0.42, fcr: 2.15, do: 6.2, mortality: 0.9, feedToday: 52 },
    { id: "P5", species: "Nursery", stock: 12000, avgWeight: 0.02, fcr: 0, do: 7.1, mortality: 2.0, feedToday: 8 },
    { id: "P6", species: "Mud Crab", stock: 480, avgWeight: 0.38, fcr: 3.2, do: 5.5, mortality: 3.5, feedToday: 15 },
  ],
  greenhouse: [
    { id: "GH1-Chilli", crop: "Green Chilli", stage: "Fruiting", daysPlanted: 85, health: 92, yieldKg: 2400, targetKg: 9000 },
    { id: "GH1-Tomato", crop: "Tomato", stage: "Flowering", daysPlanted: 62, health: 88, yieldKg: 1800, targetKg: 16000 },
    { id: "GH1-Cucumber", crop: "Cucumber", stage: "Harvesting", daysPlanted: 48, health: 95, yieldKg: 4200, targetKg: 13000 },
    { id: "GH2-Ridge", crop: "Ridge Gourd", stage: "Vegetative", daysPlanted: 28, health: 90, yieldKg: 800, targetKg: 7000 },
    { id: "GH2-Bitter", crop: "Bitter Gourd", stage: "Flowering", daysPlanted: 42, health: 86, yieldKg: 1200, targetKg: 6000 },
  ],
  verticalFarm: [
    { crop: "Spinach", tier: "1-2", cycleDay: 18, health: 96, batchKg: 120, cyclesLeft: 2 },
    { crop: "Coriander", tier: "3-4", cycleDay: 22, health: 94, batchKg: 95, cyclesLeft: 1 },
    { crop: "Fenugreek", tier: "5", cycleDay: 14, health: 98, batchKg: 85, cyclesLeft: 3 },
    { crop: "Amaranthus", tier: "6", cycleDay: 20, health: 92, batchKg: 110, cyclesLeft: 2 },
  ],
  poultry: { hens: 792, layRate: 87.5, eggsToday: 695, eggsBroken: 4, feedConsumed: 89, mortality: 0, waterUsage: 1200 },
  ducks: { count: 395, eggsToday: 310, pestsConsumed: "High", area: "Pond P3-P4 perimeter" },
  bees: { hives: 20, activeForagers: "High", honeyStored: 42, lastInspection: "3 days ago" },
  nursery: { seedlingsReady: 185000, ordersThisMonth: 12, capacityUsed: 72, species: 24 },
  financial: {
    monthlyRevenue: [
      { month: "Jul", aqua: 8.2, gh: 1.5, vf: 2.0, field: 0, poultry: 2.8, nursery: 4.2, other: 2.5 },
      { month: "Aug", aqua: 9.1, gh: 1.8, vf: 2.2, field: 0, poultry: 2.9, nursery: 4.5, other: 2.8 },
      { month: "Sep", aqua: 10.5, gh: 1.6, vf: 2.1, field: 3.2, poultry: 3.0, nursery: 4.8, other: 3.0 },
      { month: "Oct", aqua: 11.2, gh: 1.9, vf: 2.4, field: 5.8, poultry: 3.1, nursery: 5.2, other: 3.5 },
      { month: "Nov", aqua: 10.8, gh: 2.1, vf: 2.3, field: 8.2, poultry: 3.2, nursery: 5.0, other: 4.0 },
      { month: "Dec", aqua: 12.0, gh: 2.0, vf: 2.5, field: 6.5, poultry: 3.0, nursery: 4.8, other: 4.5 },
    ],
    expenses: { feed: 5.8, labour: 1.5, power: 0, maintenance: 0.8, logistics: 1.2, overhead: 1.3 },
    ytdRevenue: 182.4, ytdExpense: 63.6, ytdProfit: 118.8,
  },
  markets: {
    hyderabad: { lastPrice: { murrel: 520, rohu: 145, tomato: 38, chilli: 65 }, trend: "up" },
    chennai: { lastPrice: { murrel: 620, rohu: 155, tomato: 42, chilli: 58 }, trend: "stable" },
    vijayawada: { lastPrice: { murrel: 480, rohu: 135, tomato: 32, chilli: 55 }, trend: "up" },
    kadapa: { lastPrice: { murrel: 440, rohu: 125, tomato: 28, chilli: 50 }, trend: "down" },
    nellore: { lastPrice: { murrel: 400, rohu: 120, tomato: 25, chilli: 48 }, trend: "stable" },
  },
  automation: {
    irrigation: { status: "Active", zonesActive: 3, totalZones: 5, lastRun: "06:30 AM" },
    fishFeeder: { status: "Scheduled", nextFeed: "12:00 PM", todayFeeds: 1, totalFeeds: 3 },
    eggBelt: { status: "Running", collected: 695, target: 720, startTime: "08:00 AM" },
    manureScraper: { status: "Idle", nextRun: "06:00 PM", todayRuns: 1, totalRuns: 2 },
    ghClimate: { status: "Active", curtains: "Open", fans: "OFF", pad: "OFF" },
    drone: { status: "Docked", battery: 94, lastFlight: "07:30 AM", nextScheduled: "3:00 PM" },
  },
  aiConversations: [],
  lastUpdated: Date.now(),
});

// ─── Micro components ───
const Badge = ({ children, color = T.primary }) => (
  <span style={{ background: color + "22", color, padding: "2px 8px", borderRadius: 4, fontSize: 11, fontWeight: 600 }}>{children}</span>
);

const StatCard = ({ icon: Icon, label, value, unit, color, sub, small }) => (
  <div style={{ background: T.card, borderRadius: 10, padding: small ? "10px 12px" : "14px 16px", border: `1px solid ${T.border}`, display: "flex", alignItems: "center", gap: 12, minWidth: 0 }}>
    <div style={{ width: small ? 32 : 38, height: small ? 32 : 38, borderRadius: 8, background: (color || T.primary) + "22", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
      <Icon size={small ? 16 : 18} color={color || T.primary} />
    </div>
    <div style={{ minWidth: 0 }}>
      <div style={{ fontSize: 11, color: T.textDim, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{label}</div>
      <div style={{ fontSize: small ? 16 : 20, fontWeight: 700, color: T.text, display: "flex", alignItems: "baseline", gap: 3 }}>
        {value}<span style={{ fontSize: 11, color: T.textDim, fontWeight: 400 }}>{unit}</span>
      </div>
      {sub && <div style={{ fontSize: 10, color: T.textMuted }}>{sub}</div>}
    </div>
  </div>
);

const SectionHeader = ({ icon: Icon, title, color, children }) => (
  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <div style={{ width: 32, height: 32, borderRadius: 8, background: (color || T.primary) + "22", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <Icon size={16} color={color || T.primary} />
      </div>
      <h2 style={{ fontSize: 18, fontWeight: 700, color: T.text, margin: 0 }}>{title}</h2>
    </div>
    {children}
  </div>
);

const ProgressBar = ({ value, max, color = T.primary, height = 6 }) => (
  <div style={{ background: T.bg, borderRadius: height, height, width: "100%", overflow: "hidden" }}>
    <div style={{ width: `${Math.min((value / max) * 100, 100)}%`, height: "100%", background: color, borderRadius: height, transition: "width 0.5s ease" }} />
  </div>
);

const AlertDot = ({ type }) => {
  const colors = { warning: T.warn, danger: T.danger, info: T.info, success: T.primary };
  return <div style={{ width: 8, height: 8, borderRadius: 4, background: colors[type] || T.info, flexShrink: 0 }} />;
};

const TabBtn = ({ active, onClick, icon: Icon, label, color }) => (
  <button onClick={onClick} style={{
    display: "flex", alignItems: "center", gap: 6, padding: "8px 14px", borderRadius: 8,
    border: active ? `1px solid ${color || T.primary}` : "1px solid transparent",
    background: active ? (color || T.primary) + "18" : "transparent",
    color: active ? (color || T.primary) : T.textDim,
    cursor: "pointer", fontSize: 12, fontWeight: active ? 600 : 400, transition: "all 0.2s",
    whiteSpace: "nowrap",
  }}>
    {Icon && <Icon size={14} />}{label}
  </button>
);

const MiniTable = ({ headers, rows, colWidths }) => (
  <div style={{ overflowX: "auto" }}>
    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
      <thead>
        <tr>{headers.map((h, i) => (
          <th key={i} style={{ padding: "8px 10px", textAlign: i === 0 ? "left" : "right", color: T.textDim, borderBottom: `1px solid ${T.border}`, fontWeight: 600, whiteSpace: "nowrap", width: colWidths?.[i] }}>{h}</th>
        ))}</tr>
      </thead>
      <tbody>
        {rows.map((row, ri) => (
          <tr key={ri} style={{ background: ri % 2 === 0 ? "transparent" : T.bg + "60" }}>
            {row.map((cell, ci) => (
              <td key={ci} style={{ padding: "7px 10px", textAlign: ci === 0 ? "left" : "right", color: T.text, borderBottom: `1px solid ${T.border}40`, whiteSpace: "nowrap" }}>
                {typeof cell === "object" ? cell : cell}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

const CHART_COLORS = [T.fish, T.crop, T.primary, T.accent, T.poultry, T.info, T.market, T.danger];

// ─── Tabs config ───
const TABS = [
  { id: "dashboard", label: "Dashboard", icon: Home, color: T.primary },
  { id: "aquaculture", label: "Aquaculture", icon: Fish, color: T.fish },
  { id: "greenhouse", label: "Greenhouse", icon: Leaf, color: T.crop },
  { id: "verticalfarm", label: "Vertical Farm", icon: Sprout, color: "#8E44AD" },
  { id: "poultry", label: "Poultry & Duck", icon: Egg, color: T.poultry },
  { id: "water", label: "Water System", icon: Droplets, color: T.water },
  { id: "energy", label: "Solar Energy", icon: Sun, color: T.solar },
  { id: "automation", label: "Automation", icon: Zap, color: "#E74C3C" },
  { id: "market", label: "Markets", icon: Truck, color: T.market },
  { id: "financial", label: "Financials", icon: DollarSign, color: T.accent },
  { id: "nursery", label: "Nursery & Bees", icon: Sprout, color: "#2ECC71" },
  { id: "ai", label: "AI Analysis", icon: Brain, color: "#00BCD4" },
];

// ═══════════════════════════════════════════════════════════════════
// MAIN APP
// ═══════════════════════════════════════════════════════════════════
export default function SmartFarmApp() {
  const [farm, setFarm] = useState(() => loadData() || defaultFarmState());
  const [tab, setTab] = useState("dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [alertsOpen, setAlertsOpen] = useState(false);
  const [simRunning, setSimRunning] = useState(false);

  useEffect(() => { saveData(farm); }, [farm]);

  // Sensor simulation
  useEffect(() => {
    if (!simRunning) return;
    const iv = setInterval(() => {
      setFarm(prev => {
        const s = { ...prev.sensors };
        s.waterTemp = +(s.waterTemp + (Math.random() - 0.5) * 0.3).toFixed(1);
        s.dissolvedO2 = +Math.max(3.5, Math.min(8, s.dissolvedO2 + (Math.random() - 0.48) * 0.2)).toFixed(1);
        s.ph = +(s.ph + (Math.random() - 0.5) * 0.05).toFixed(2);
        s.soilMoisture = +Math.max(20, Math.min(60, s.soilMoisture + (Math.random() - 0.5) * 2)).toFixed(0);
        s.ghTemp = +(s.ghTemp + (Math.random() - 0.5) * 0.5).toFixed(1);
        s.ghHumidity = +Math.max(50, Math.min(95, s.ghHumidity + (Math.random() - 0.5) * 2)).toFixed(0);
        s.solarGeneration = +Math.max(0, Math.min(120, s.solarGeneration + (Math.random() - 0.5) * 5)).toFixed(1);
        s.farmConsumption = +(s.solarGeneration * (0.6 + Math.random() * 0.2)).toFixed(1);
        s.gridExport = +Math.max(0, s.solarGeneration - s.farmConsumption).toFixed(1);
        s.reservoirLevel = +Math.max(30, Math.min(100, s.reservoirLevel + (Math.random() - 0.52) * 0.5)).toFixed(0);
        s.eggCount = Math.min(720, s.eggCount + Math.floor(Math.random() * 3));
        s.ambientTemp = +(s.ambientTemp + (Math.random() - 0.5) * 0.4).toFixed(1);
        const newAlerts = [...prev.alerts];
        if (s.dissolvedO2 < 4.5 && !newAlerts.find(a => a.msg.includes("CRITICAL DO"))) {
          newAlerts.unshift({ id: Date.now(), type: "danger", msg: `CRITICAL DO level ${s.dissolvedO2} mg/L — emergency aeration activated`, time: "Just now", system: "Aquaculture" });
        }
        if (s.ghTemp > 37 && !newAlerts.find(a => a.msg.includes("High temperature"))) {
          newAlerts.unshift({ id: Date.now() + 1, type: "warning", msg: `High temperature in Greenhouse: ${s.ghTemp}°C — fan+pad activated`, time: "Just now", system: "Greenhouse" });
        }
        return { ...prev, sensors: s, alerts: newAlerts.slice(0, 20), lastUpdated: Date.now() };
      });
    }, 3000);
    return () => clearInterval(iv);
  }, [simRunning]);

  const navWidth = sidebarOpen ? 200 : 56;

  return (
    <div style={{ display: "flex", height: "100vh", background: T.bg, color: T.text, fontFamily: "'DM Sans', 'Segoe UI', sans-serif", overflow: "hidden" }}>
      {/* ─── Sidebar ─── */}
      <nav style={{ width: navWidth, background: T.card, borderRight: `1px solid ${T.border}`, display: "flex", flexDirection: "column", transition: "width 0.25s ease", flexShrink: 0, overflow: "hidden" }}>
        <div style={{ padding: "16px 12px", display: "flex", alignItems: "center", gap: 10, borderBottom: `1px solid ${T.border}` }}>
          <button onClick={() => setSidebarOpen(!sidebarOpen)} style={{ background: "none", border: "none", color: T.textDim, cursor: "pointer", padding: 4 }}>
            {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
          {sidebarOpen && <span style={{ fontSize: 14, fontWeight: 700, color: T.primary, whiteSpace: "nowrap" }}>🌿 SmartFarm OS</span>}
        </div>
        <div style={{ flex: 1, overflowY: "auto", padding: "8px 6px" }}>
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)} style={{
              display: "flex", alignItems: "center", gap: 10, width: "100%", padding: sidebarOpen ? "9px 12px" : "9px 0",
              justifyContent: sidebarOpen ? "flex-start" : "center",
              borderRadius: 8, border: "none", cursor: "pointer", marginBottom: 2,
              background: tab === t.id ? t.color + "20" : "transparent",
              color: tab === t.id ? t.color : T.textDim, fontSize: 12, fontWeight: tab === t.id ? 600 : 400,
              transition: "all 0.15s",
            }}>
              <t.icon size={16} />
              {sidebarOpen && <span style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{t.label}</span>}
            </button>
          ))}
        </div>
        <div style={{ padding: "10px 12px", borderTop: `1px solid ${T.border}` }}>
          <button onClick={() => setSimRunning(!simRunning)} style={{
            display: "flex", alignItems: "center", justifyContent: sidebarOpen ? "flex-start" : "center", gap: 8,
            width: "100%", padding: "8px 10px", borderRadius: 8, border: `1px solid ${simRunning ? T.primary : T.border}`,
            background: simRunning ? T.primary + "15" : "transparent", color: simRunning ? T.primary : T.textDim,
            cursor: "pointer", fontSize: 11, fontWeight: 600,
          }}>
            {simRunning ? <Wifi size={14} /> : <WifiOff size={14} />}
            {sidebarOpen && (simRunning ? "LIVE" : "Simulate")}
          </button>
        </div>
      </nav>

      {/* ─── Main ─── */}
      <main style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        {/* Top bar */}
        <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 20px", borderBottom: `1px solid ${T.border}`, background: T.card, flexShrink: 0 }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 16, fontWeight: 700 }}>{TABS.find(t => t.id === tab)?.label || "Dashboard"}</h1>
            <div style={{ fontSize: 11, color: T.textMuted }}>Nellore District, AP • {new Date(farm.lastUpdated).toLocaleTimeString()}</div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{ position: "relative" }}>
              <button onClick={() => setAlertsOpen(!alertsOpen)} style={{ background: "none", border: "none", color: T.textDim, cursor: "pointer", position: "relative", padding: 4 }}>
                <Bell size={18} />
                {farm.alerts.some(a => a.type === "danger") && <div style={{ position: "absolute", top: 2, right: 2, width: 7, height: 7, borderRadius: 4, background: T.danger }} />}
              </button>
              {alertsOpen && (
                <div style={{ position: "absolute", top: 34, right: 0, width: 340, background: T.card, border: `1px solid ${T.border}`, borderRadius: 10, boxShadow: "0 8px 32px rgba(0,0,0,0.5)", zIndex: 100, maxHeight: 400, overflowY: "auto" }}>
                  <div style={{ padding: "12px 14px", borderBottom: `1px solid ${T.border}`, fontWeight: 600, fontSize: 13 }}>Alerts ({farm.alerts.length})</div>
                  {farm.alerts.map(a => (
                    <div key={a.id} style={{ padding: "10px 14px", borderBottom: `1px solid ${T.border}40`, display: "flex", gap: 10, alignItems: "flex-start" }}>
                      <AlertDot type={a.type} />
                      <div>
                        <div style={{ fontSize: 12, color: T.text }}>{a.msg}</div>
                        <div style={{ fontSize: 10, color: T.textMuted, marginTop: 2 }}>{a.system} • {a.time}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <Badge color={simRunning ? T.primary : T.textMuted}>{simRunning ? "● LIVE" : "○ OFFLINE"}</Badge>
          </div>
        </header>

        {/* Content */}
        <div style={{ flex: 1, overflowY: "auto", padding: 20 }} onClick={() => alertsOpen && setAlertsOpen(false)}>
          {tab === "dashboard" && <DashboardView farm={farm} setTab={setTab} />}
          {tab === "aquaculture" && <AquacultureView farm={farm} setFarm={setFarm} />}
          {tab === "greenhouse" && <GreenhouseView farm={farm} />}
          {tab === "verticalfarm" && <VerticalFarmView farm={farm} />}
          {tab === "poultry" && <PoultryView farm={farm} />}
          {tab === "water" && <WaterView farm={farm} />}
          {tab === "energy" && <EnergyView farm={farm} />}
          {tab === "automation" && <AutomationView farm={farm} setFarm={setFarm} />}
          {tab === "market" && <MarketView farm={farm} />}
          {tab === "financial" && <FinancialView farm={farm} />}
          {tab === "nursery" && <NurseryView farm={farm} />}
          {tab === "ai" && <AIView farm={farm} setFarm={setFarm} />}
        </div>
      </main>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// DASHBOARD
// ═══════════════════════════════════════════════════════════════════
function DashboardView({ farm, setTab }) {
  const s = farm.sensors;
  const revData = [
    { name: "Aquaculture", value: 101.4, color: T.fish },
    { name: "Greenhouse", value: 19.05, color: T.crop },
    { name: "Vertical Farm", value: 25, color: "#8E44AD" },
    { name: "Field Crops", value: 60, color: T.accent },
    { name: "Poultry/Duck", value: 33.8, color: T.poultry },
    { name: "Nursery", value: 56.7, color: "#2ECC71" },
    { name: "Other", value: 233, color: T.info },
  ];
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* KPI Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 10 }}>
        <StatCard icon={DollarSign} label="YTD Revenue" value={`₹${farm.financial.ytdRevenue}L`} color={T.primary} sub="+12.4% vs target" />
        <StatCard icon={TrendingUp} label="YTD Profit" value={`₹${farm.financial.ytdProfit}L`} color={T.accent} sub="65.1% margin" />
        <StatCard icon={Fish} label="Fish Stock" value={`${(farm.ponds.reduce((a, p) => a + p.stock, 0) / 1000).toFixed(1)}K`} color={T.fish} sub="6 ponds active" />
        <StatCard icon={Egg} label="Eggs Today" value={s.eggCount} color={T.poultry} sub={`${farm.poultry.layRate}% lay rate`} />
        <StatCard icon={Sun} label="Solar Gen." value={`${s.solarGeneration}kW`} color={T.solar} sub={`${s.gridExport}kW exported`} />
        <StatCard icon={Droplets} label="Reservoir" value={`${s.reservoirLevel}%`} color={T.water} sub="~7.8M litres" />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* Environment */}
        <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
          <SectionHeader icon={Thermometer} title="Environment" color={T.info} />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
            <StatCard small icon={Thermometer} label="Ambient" value={s.ambientTemp} unit="°C" color={T.danger} />
            <StatCard small icon={Droplets} label="Humidity" value={s.humidity} unit="%" color={T.water} />
            <StatCard small icon={Wind} label="Wind" value={s.windSpeed} unit="km/h" color={T.textDim} />
            <StatCard small icon={Sun} label="Solar Rad." value={s.solarRad} unit="W/m²" color={T.solar} />
            <StatCard small icon={Thermometer} label="GH Temp" value={s.ghTemp} unit="°C" color={s.ghTemp > 36 ? T.danger : T.crop} />
            <StatCard small icon={Activity} label="GH CO₂" value={s.ghCO2} unit="ppm" color={T.crop} />
          </div>
        </div>

        {/* Revenue Pie */}
        <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
          <SectionHeader icon={BarChart3} title="Revenue Mix (Annual Target)" color={T.accent} />
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <ResponsiveContainer width="50%" height={180}>
              <PieChart>
                <Pie data={revData} dataKey="value" cx="50%" cy="50%" outerRadius={75} innerRadius={40} strokeWidth={0}>
                  {revData.map((d, i) => <Cell key={i} fill={d.color} />)}
                </Pie>
                <Tooltip contentStyle={{ background: T.card, border: `1px solid ${T.border}`, borderRadius: 8, fontSize: 12, color: T.text }} formatter={(v) => `₹${v}L`} />
              </PieChart>
            </ResponsiveContainer>
            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 4 }}>
              {revData.map(d => (
                <div key={d.name} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11 }}>
                  <div style={{ width: 8, height: 8, borderRadius: 2, background: d.color, flexShrink: 0 }} />
                  <span style={{ color: T.textDim, flex: 1 }}>{d.name}</span>
                  <span style={{ color: T.text, fontWeight: 600 }}>₹{d.value}L</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Alerts + Quick Links */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
          <SectionHeader icon={AlertTriangle} title="Recent Alerts" color={T.warn} />
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {farm.alerts.slice(0, 5).map(a => (
              <div key={a.id} style={{ display: "flex", gap: 10, alignItems: "flex-start", padding: "8px 10px", background: T.bg, borderRadius: 8 }}>
                <AlertDot type={a.type} />
                <div>
                  <div style={{ fontSize: 12, color: T.text }}>{a.msg}</div>
                  <div style={{ fontSize: 10, color: T.textMuted }}>{a.system} • {a.time}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
          <SectionHeader icon={Zap} title="Automation Status" color="#E74C3C" />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
            {Object.entries(farm.automation).map(([key, val]) => (
              <div key={key} style={{ padding: "8px 10px", background: T.bg, borderRadius: 8, display: "flex", alignItems: "center", gap: 8 }}>
                <div style={{ width: 8, height: 8, borderRadius: 4, background: val.status === "Active" || val.status === "Running" ? T.primary : val.status === "Scheduled" ? T.accent : T.textMuted }} />
                <div>
                  <div style={{ fontSize: 11, fontWeight: 600, color: T.text, textTransform: "capitalize" }}>{key.replace(/([A-Z])/g, " $1")}</div>
                  <div style={{ fontSize: 10, color: T.textDim }}>{val.status}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// AQUACULTURE
// ═══════════════════════════════════════════════════════════════════
function AquacultureView({ farm, setFarm }) {
  const totalStock = farm.ponds.reduce((a, p) => a + p.stock, 0);
  const totalBiomass = farm.ponds.reduce((a, p) => a + p.stock * p.avgWeight, 0);
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 10 }}>
        <StatCard icon={Fish} label="Total Stock" value={totalStock.toLocaleString()} color={T.fish} sub="6 ponds" />
        <StatCard icon={Activity} label="Biomass" value={`${(totalBiomass / 1000).toFixed(1)}T`} color={T.primary} />
        <StatCard icon={Thermometer} label="Water Temp" value={farm.sensors.waterTemp} unit="°C" color={T.info} />
        <StatCard icon={Droplets} label="Avg DO" value={farm.sensors.dissolvedO2} unit="mg/L" color={farm.sensors.dissolvedO2 < 5 ? T.danger : T.water} />
        <StatCard icon={Activity} label="pH" value={farm.sensors.ph} color={T.primary} />
        <StatCard icon={AlertTriangle} label="Ammonia" value={farm.sensors.ammonia} unit="mg/L" color={farm.sensors.ammonia > 0.05 ? T.danger : T.primary} />
      </div>

      <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
        <SectionHeader icon={Fish} title="Pond Status" color={T.fish} />
        <MiniTable
          headers={["Pond", "Species", "Stock", "Avg Wt (kg)", "FCR", "DO (mg/L)", "Feed Today (kg)", "Mortality %"]}
          rows={farm.ponds.map(p => [
            <span style={{ fontWeight: 700, color: T.fish }}>{p.id}</span>,
            p.species,
            p.stock.toLocaleString(),
            p.avgWeight.toFixed(2),
            p.fcr.toFixed(2),
            <span style={{ color: p.do < 5 ? T.danger : T.primary, fontWeight: 600 }}>{p.do}</span>,
            p.feedToday,
            <span style={{ color: p.mortality > 2 ? T.danger : T.textDim }}>{p.mortality}%</span>,
          ])}
        />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
          <SectionHeader icon={BarChart3} title="Biomass Growth Tracking" color={T.fish} />
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={[
              { week: "W1", p1: 180, p2: 170, p3: 280, p4: 260 },
              { week: "W4", p1: 320, p2: 310, p3: 450, p4: 420 },
              { week: "W8", p1: 580, p2: 550, p3: 720, p4: 680 },
              { week: "W12", p1: 850, p2: 800, p3: 1050, p4: 980 },
              { week: "W16", p1: 1200, p2: 1100, p3: 1400, p4: 1300 },
              { week: "W20", p1: 1650, p2: 1520, p3: 1800, p4: 1680 },
              { week: "W24", p1: 2356, p2: 2175, p3: 2610, p4: 2352 },
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke={T.border} />
              <XAxis dataKey="week" tick={{ fill: T.textDim, fontSize: 10 }} />
              <YAxis tick={{ fill: T.textDim, fontSize: 10 }} />
              <Tooltip contentStyle={{ background: T.card, border: `1px solid ${T.border}`, borderRadius: 8, fontSize: 11, color: T.text }} />
              <Area type="monotone" dataKey="p1" stroke={T.fish} fill={T.fish + "30"} name="P1 Murrel" />
              <Area type="monotone" dataKey="p3" stroke={T.primary} fill={T.primary + "30"} name="P3 IMC" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
          <SectionHeader icon={Activity} title="Water Quality 24hr" color={T.water} />
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={Array.from({ length: 24 }, (_, i) => ({
              hr: `${i}:00`, do: +(5.5 + Math.sin(i / 4) * 1.2 + Math.random() * 0.3).toFixed(1),
              ph: +(7.2 + Math.sin(i / 6) * 0.3).toFixed(2), temp: +(25 + Math.sin(i / 5) * 2).toFixed(1),
            }))}>
              <CartesianGrid strokeDasharray="3 3" stroke={T.border} />
              <XAxis dataKey="hr" tick={{ fill: T.textDim, fontSize: 9 }} interval={3} />
              <YAxis tick={{ fill: T.textDim, fontSize: 10 }} />
              <Tooltip contentStyle={{ background: T.card, border: `1px solid ${T.border}`, borderRadius: 8, fontSize: 11, color: T.text }} />
              <Line type="monotone" dataKey="do" stroke={T.water} strokeWidth={2} dot={false} name="DO mg/L" />
              <Line type="monotone" dataKey="ph" stroke={T.accent} strokeWidth={2} dot={false} name="pH" />
              <Legend wrapperStyle={{ fontSize: 10 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// GREENHOUSE
// ═══════════════════════════════════════════════════════════════════
function GreenhouseView({ farm }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 10 }}>
        <StatCard icon={Thermometer} label="GH Temperature" value={farm.sensors.ghTemp} unit="°C" color={farm.sensors.ghTemp > 36 ? T.danger : T.crop} />
        <StatCard icon={Droplets} label="GH Humidity" value={farm.sensors.ghHumidity} unit="%" color={T.water} />
        <StatCard icon={Activity} label="CO₂ Level" value={farm.sensors.ghCO2} unit="ppm" color={T.crop} />
        <StatCard icon={Sun} label="Light (PAR)" value={farm.sensors.ghLight} unit="µmol" color={T.solar} />
        <StatCard icon={Droplets} label="Soil Moisture" value={farm.sensors.soilMoisture} unit="%" color={T.water} />
        <StatCard icon={Thermometer} label="Soil Temp" value={farm.sensors.soilTemp} unit="°C" color={T.poultry} />
      </div>

      <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
        <SectionHeader icon={Leaf} title="Crop Status" color={T.crop} />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 12 }}>
          {farm.greenhouse.map(c => (
            <div key={c.id} style={{ background: T.bg, borderRadius: 10, padding: 14, border: `1px solid ${T.border}` }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                <span style={{ fontWeight: 700, color: T.text, fontSize: 14 }}>{c.crop}</span>
                <Badge color={c.stage === "Harvesting" ? T.primary : c.stage === "Fruiting" ? T.accent : T.info}>{c.stage}</Badge>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6, fontSize: 12, color: T.textDim, marginBottom: 10 }}>
                <div>Day {c.daysPlanted}</div>
                <div style={{ textAlign: "right" }}>Health: <span style={{ color: c.health > 90 ? T.primary : c.health > 80 ? T.accent : T.danger, fontWeight: 600 }}>{c.health}%</span></div>
              </div>
              <div style={{ fontSize: 11, color: T.textDim, marginBottom: 4 }}>Yield: {c.yieldKg.toLocaleString()} / {c.targetKg.toLocaleString()} kg</div>
              <ProgressBar value={c.yieldKg} max={c.targetKg} color={T.crop} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// VERTICAL FARM
// ═══════════════════════════════════════════════════════════════════
function VerticalFarmView({ farm }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 10 }}>
        <StatCard icon={Thermometer} label="VF Temp" value={farm.sensors.vfTemp} unit="°C" color="#8E44AD" />
        <StatCard icon={Droplets} label="VF Humidity" value={farm.sensors.vfHumidity} unit="%" color={T.water} />
        <StatCard icon={Activity} label="Nutrient EC" value={farm.sensors.vfNutrientEC} unit="mS" color={T.primary} />
        <StatCard icon={Activity} label="Solution pH" value={farm.sensors.vfPH} color={T.accent} />
      </div>
      <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
        <SectionHeader icon={Sprout} title="Vertical Farm Tiers" color="#8E44AD" />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 12 }}>
          {farm.verticalFarm.map(v => (
            <div key={v.crop} style={{ background: T.bg, borderRadius: 10, padding: 14, border: `1px solid ${T.border}` }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                <span style={{ fontWeight: 700, fontSize: 14 }}>{v.crop}</span>
                <Badge color="#8E44AD">Tier {v.tier}</Badge>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 4, fontSize: 11, color: T.textDim }}>
                <div>Cycle Day: {v.cycleDay}</div>
                <div>Health: <span style={{ color: T.primary, fontWeight: 600 }}>{v.health}%</span></div>
                <div>Batch: {v.batchKg} kg</div>
                <div>Cycles Left: {v.cyclesLeft}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// POULTRY
// ═══════════════════════════════════════════════════════════════════
function PoultryView({ farm }) {
  const p = farm.poultry;
  const d = farm.ducks;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
          <SectionHeader icon={Egg} title="Poultry — 800 Layer Hens" color={T.poultry} />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
            <StatCard small icon={Users} label="Active Hens" value={p.hens} color={T.poultry} />
            <StatCard small icon={Egg} label="Eggs Today" value={p.eggsToday} color={T.accent} sub={`${p.eggsBroken} broken`} />
            <StatCard small icon={TrendingUp} label="Lay Rate" value={`${p.layRate}%`} color={T.primary} />
            <StatCard small icon={Activity} label="Feed Used" value={`${p.feedConsumed}kg`} color={T.poultry} />
            <StatCard small icon={Thermometer} label="Shed Temp" value={farm.sensors.poultryTemp} unit="°C" color={T.info} />
            <StatCard small icon={AlertTriangle} label="NH₃ Level" value={farm.sensors.poultryAmmonia} unit="ppm" color={farm.sensors.poultryAmmonia > 20 ? T.danger : T.primary} />
          </div>
        </div>
        <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
          <SectionHeader icon={Bug} title="Ducks & Bees" color={T.info} />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 16 }}>
            <StatCard small icon={Users} label="Ducks Active" value={d.count} color={T.info} />
            <StatCard small icon={Egg} label="Duck Eggs" value={d.eggsToday} color={T.accent} />
          </div>
          <div style={{ fontSize: 12, color: T.textDim, padding: "8px 10px", background: T.bg, borderRadius: 8, marginBottom: 10 }}>
            <div><strong>Pest Control:</strong> {d.pestsConsumed} activity at {d.area}</div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
            <StatCard small icon={Sprout} label="Bee Hives" value={farm.bees.hives} color={T.accent} />
            <StatCard small icon={Activity} label="Honey Stored" value={`${farm.bees.honeyStored}kg`} color={T.accent} />
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// WATER
// ═══════════════════════════════════════════════════════════════════
function WaterView({ farm }) {
  const s = farm.sensors;
  const flowStages = [
    { label: "Reservoir", value: `${s.reservoirLevel}%`, icon: Database, color: T.water },
    { label: "Solar Pump", value: "5 HP DC", icon: Sun, color: T.solar },
    { label: "Header Tank", value: `${s.headerTankLevel}%`, icon: Droplets, color: T.info },
    { label: "Gravity Drip", value: "5 Zones", icon: Sprout, color: T.crop },
    { label: "Fish Ponds", value: "Reuse", icon: Fish, color: T.fish },
    { label: "Collection Pond", value: "Recycle", icon: RefreshCw, color: T.primary },
  ];
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 10 }}>
        <StatCard icon={Database} label="Reservoir" value={`${s.reservoirLevel}%`} color={T.water} sub="~7.8M litres" />
        <StatCard icon={Droplets} label="Header Tank" value={`${s.headerTankLevel}%`} color={T.info} sub="30,000L capacity" />
        <StatCard icon={CloudRain} label="Rainfall Today" value={s.rainfall} unit="mm" color={T.water} />
        <StatCard icon={Activity} label="Daily Usage" value="43,500" unit="L" color={T.textDim} />
      </div>
      <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
        <SectionHeader icon={Droplets} title="Water Flow — Closed Loop System" color={T.water} />
        <div style={{ display: "flex", alignItems: "center", gap: 4, overflowX: "auto", padding: "10px 0" }}>
          {flowStages.map((st, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 4, flexShrink: 0 }}>
              <div style={{ textAlign: "center", padding: "12px 14px", background: st.color + "18", borderRadius: 10, border: `1px solid ${st.color}40`, minWidth: 100 }}>
                <st.icon size={20} color={st.color} style={{ marginBottom: 4 }} />
                <div style={{ fontSize: 12, fontWeight: 700, color: T.text }}>{st.label}</div>
                <div style={{ fontSize: 11, color: T.textDim }}>{st.value}</div>
              </div>
              {i < flowStages.length - 1 && <ChevronRight size={18} color={T.textMuted} />}
            </div>
          ))}
          <ChevronRight size={18} color={T.textMuted} />
          <div style={{ fontSize: 11, color: T.water, fontWeight: 600, padding: "4px 8px", border: `1px dashed ${T.water}`, borderRadius: 6 }}>↺ Reservoir</div>
        </div>
      </div>
      <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
        <SectionHeader icon={BarChart3} title="Daily Water Budget" color={T.water} />
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={[
            { use: "Fish Ponds", litres: 25000 }, { use: "Greenhouse", litres: 5000 },
            { use: "Field Crops", litres: 8000 }, { use: "Nursery", litres: 2000 },
            { use: "Poultry/Duck", litres: 1500 }, { use: "Vertical Farm", litres: 500 },
            { use: "Packhouse", litres: 1000 }, { use: "Misc", litres: 500 },
          ]}>
            <CartesianGrid strokeDasharray="3 3" stroke={T.border} />
            <XAxis dataKey="use" tick={{ fill: T.textDim, fontSize: 10 }} angle={-25} textAnchor="end" height={60} />
            <YAxis tick={{ fill: T.textDim, fontSize: 10 }} />
            <Tooltip contentStyle={{ background: T.card, border: `1px solid ${T.border}`, borderRadius: 8, fontSize: 11, color: T.text }} formatter={v => `${v.toLocaleString()} L`} />
            <Bar dataKey="litres" fill={T.water} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// ENERGY
// ═══════════════════════════════════════════════════════════════════
function EnergyView({ farm }) {
  const s = farm.sensors;
  const hourly = Array.from({ length: 24 }, (_, i) => {
    const gen = i < 6 || i > 18 ? 0 : Math.max(0, 120 * Math.sin((i - 6) / 12 * Math.PI) * (0.85 + Math.random() * 0.15));
    const cons = 50 + Math.random() * 30;
    return { hr: `${i}:00`, generation: +gen.toFixed(1), consumption: +cons.toFixed(1), export: +Math.max(0, gen - cons).toFixed(1) };
  });
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(170px, 1fr))", gap: 10 }}>
        <StatCard icon={Sun} label="Current Generation" value={s.solarGeneration} unit="kW" color={T.solar} sub="of 120 kWp capacity" />
        <StatCard icon={Zap} label="Farm Consumption" value={s.farmConsumption} unit="kW" color={T.info} />
        <StatCard icon={TrendingUp} label="Grid Export" value={s.gridExport} unit="kW" color={T.primary} />
        <StatCard icon={DollarSign} label="Today Revenue" value="₹1,234" color={T.accent} sub="Grid export earnings" />
      </div>
      <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
        <SectionHeader icon={Sun} title="24-Hour Energy Profile" color={T.solar} />
        <ResponsiveContainer width="100%" height={250}>
          <AreaChart data={hourly}>
            <CartesianGrid strokeDasharray="3 3" stroke={T.border} />
            <XAxis dataKey="hr" tick={{ fill: T.textDim, fontSize: 9 }} interval={2} />
            <YAxis tick={{ fill: T.textDim, fontSize: 10 }} />
            <Tooltip contentStyle={{ background: T.card, border: `1px solid ${T.border}`, borderRadius: 8, fontSize: 11, color: T.text }} />
            <Area type="monotone" dataKey="generation" stroke={T.solar} fill={T.solar + "30"} strokeWidth={2} name="Generation (kW)" />
            <Area type="monotone" dataKey="consumption" stroke={T.info} fill={T.info + "20"} strokeWidth={2} name="Consumption (kW)" />
            <Area type="monotone" dataKey="export" stroke={T.primary} fill={T.primary + "20"} strokeWidth={1} name="Export (kW)" />
            <Legend wrapperStyle={{ fontSize: 10 }} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// AUTOMATION
// ═══════════════════════════════════════════════════════════════════
function AutomationView({ farm, setFarm }) {
  const auto = farm.automation;
  const systems = [
    { key: "irrigation", icon: Droplets, name: "Irrigation System", color: T.water, fields: [`Zones: ${auto.irrigation.zonesActive}/${auto.irrigation.totalZones}`, `Last Run: ${auto.irrigation.lastRun}`] },
    { key: "fishFeeder", icon: Fish, name: "Fish Auto-Feeder", color: T.fish, fields: [`Next: ${auto.fishFeeder.nextFeed}`, `Today: ${auto.fishFeeder.todayFeeds}/${auto.fishFeeder.totalFeeds}`] },
    { key: "eggBelt", icon: Egg, name: "Egg Collection Belt", color: T.poultry, fields: [`Collected: ${auto.eggBelt.collected}/${auto.eggBelt.target}`, `Since: ${auto.eggBelt.startTime}`] },
    { key: "manureScraper", icon: RefreshCw, name: "Manure Scraper", color: "#8B4513", fields: [`Next: ${auto.manureScraper.nextRun}`, `Today: ${auto.manureScraper.todayRuns}/${auto.manureScraper.totalRuns}`] },
    { key: "ghClimate", icon: Thermometer, name: "Greenhouse Climate", color: T.crop, fields: [`Curtains: ${auto.ghClimate.curtains}`, `Fans: ${auto.ghClimate.fans} | Pad: ${auto.ghClimate.pad}`] },
    { key: "drone", icon: Wind, name: "Agriculture Drone", color: T.info, fields: [`Battery: ${auto.drone.battery}%`, `Next: ${auto.drone.nextScheduled}`] },
  ];
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 12 }}>
        {systems.map(sys => (
          <div key={sys.key} style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <div style={{ width: 36, height: 36, borderRadius: 8, background: sys.color + "22", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <sys.icon size={18} color={sys.color} />
                </div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: T.text }}>{sys.name}</div>
                  <div style={{ fontSize: 11, color: T.textDim }}>{auto[sys.key].status}</div>
                </div>
              </div>
              <div style={{ width: 10, height: 10, borderRadius: 5, background: auto[sys.key].status === "Active" || auto[sys.key].status === "Running" ? T.primary : auto[sys.key].status === "Scheduled" ? T.accent : T.textMuted }} />
            </div>
            {sys.fields.map((f, i) => (
              <div key={i} style={{ fontSize: 11, color: T.textDim, padding: "4px 0" }}>{f}</div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// MARKET
// ═══════════════════════════════════════════════════════════════════
function MarketView({ farm }) {
  const mkts = farm.markets;
  const cities = [
    { name: "Hyderabad", data: mkts.hyderabad, share: "35%", dist: "400 km" },
    { name: "Chennai", data: mkts.chennai, share: "25%", dist: "180 km" },
    { name: "Vijayawada", data: mkts.vijayawada, share: "15%", dist: "280 km" },
    { name: "Kadapa", data: mkts.kadapa, share: "10%", dist: "200 km" },
    { name: "Nellore", data: mkts.nellore, share: "15%", dist: "15 km" },
  ];
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
        <SectionHeader icon={MapPin} title="Five-City Market Prices (₹/kg)" color={T.market} />
        <MiniTable
          headers={["City", "Distance", "Share", "Murrel", "Rohu", "Tomato", "Chilli", "Trend"]}
          rows={cities.map(c => [
            <span style={{ fontWeight: 700, color: T.market }}>{c.name}</span>,
            c.dist, c.share,
            `₹${c.data.lastPrice.murrel}`, `₹${c.data.lastPrice.rohu}`,
            `₹${c.data.lastPrice.tomato}`, `₹${c.data.lastPrice.chilli}`,
            <Badge color={c.data.trend === "up" ? T.primary : c.data.trend === "down" ? T.danger : T.accent}>{c.data.trend === "up" ? "↑" : c.data.trend === "down" ? "↓" : "→"} {c.data.trend}</Badge>,
          ])}
        />
      </div>
      <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
        <SectionHeader icon={BarChart3} title="Murrel Price Comparison" color={T.fish} />
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={cities.map(c => ({ city: c.name, price: c.data.lastPrice.murrel }))}>
            <CartesianGrid strokeDasharray="3 3" stroke={T.border} />
            <XAxis dataKey="city" tick={{ fill: T.textDim, fontSize: 11 }} />
            <YAxis tick={{ fill: T.textDim, fontSize: 10 }} domain={[300, 700]} />
            <Tooltip contentStyle={{ background: T.card, border: `1px solid ${T.border}`, borderRadius: 8, fontSize: 11, color: T.text }} formatter={v => `₹${v}/kg`} />
            <Bar dataKey="price" radius={[6, 6, 0, 0]}>
              {cities.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// FINANCIAL
// ═══════════════════════════════════════════════════════════════════
function FinancialView({ farm }) {
  const f = farm.financial;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 10 }}>
        <StatCard icon={TrendingUp} label="YTD Revenue" value={`₹${f.ytdRevenue}L`} color={T.primary} />
        <StatCard icon={DollarSign} label="YTD Expenses" value={`₹${f.ytdExpense}L`} color={T.danger} />
        <StatCard icon={DollarSign} label="YTD Profit" value={`₹${f.ytdProfit}L`} color={T.accent} sub={`${((f.ytdProfit / f.ytdRevenue) * 100).toFixed(1)}% margin`} />
        <StatCard icon={TrendingUp} label="Monthly Avg" value={`₹${(f.ytdRevenue / 6).toFixed(1)}L`} color={T.info} />
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
          <SectionHeader icon={BarChart3} title="Monthly Revenue by Stream" color={T.accent} />
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={f.monthlyRevenue}>
              <CartesianGrid strokeDasharray="3 3" stroke={T.border} />
              <XAxis dataKey="month" tick={{ fill: T.textDim, fontSize: 10 }} />
              <YAxis tick={{ fill: T.textDim, fontSize: 10 }} />
              <Tooltip contentStyle={{ background: T.card, border: `1px solid ${T.border}`, borderRadius: 8, fontSize: 11, color: T.text }} formatter={v => `₹${v}L`} />
              <Bar dataKey="aqua" stackId="a" fill={T.fish} name="Aquaculture" />
              <Bar dataKey="gh" stackId="a" fill={T.crop} name="Greenhouse" />
              <Bar dataKey="vf" stackId="a" fill="#8E44AD" name="Vertical Farm" />
              <Bar dataKey="field" stackId="a" fill={T.accent} name="Field Crops" />
              <Bar dataKey="poultry" stackId="a" fill={T.poultry} name="Poultry" />
              <Bar dataKey="nursery" stackId="a" fill="#2ECC71" name="Nursery" />
              <Bar dataKey="other" stackId="a" fill={T.info} name="Other" radius={[4, 4, 0, 0]} />
              <Legend wrapperStyle={{ fontSize: 9 }} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
          <SectionHeader icon={DollarSign} title="Operating Expenses (Monthly)" color={T.danger} />
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={Object.entries(f.expenses).map(([k, v]) => ({ name: k.charAt(0).toUpperCase() + k.slice(1), value: v }))} dataKey="value" cx="50%" cy="50%" outerRadius={85} innerRadius={45} strokeWidth={0}>
                {Object.keys(f.expenses).map((_, i) => <Cell key={i} fill={CHART_COLORS[i]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: T.card, border: `1px solid ${T.border}`, borderRadius: 8, fontSize: 11, color: T.text }} formatter={v => `₹${v}L`} />
              <Legend wrapperStyle={{ fontSize: 10 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// NURSERY
// ═══════════════════════════════════════════════════════════════════
function NurseryView({ farm }) {
  const n = farm.nursery;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 10 }}>
        <StatCard icon={Sprout} label="Seedlings Ready" value={`${(n.seedlingsReady / 1000).toFixed(0)}K`} color={T.primary} sub="of 300K capacity" />
        <StatCard icon={Truck} label="Orders This Month" value={n.ordersThisMonth} color={T.accent} />
        <StatCard icon={Activity} label="Capacity Used" value={`${n.capacityUsed}%`} color={T.info} />
        <StatCard icon={Leaf} label="Species Available" value={n.species} color={T.crop} />
      </div>
      <div style={{ background: T.card, borderRadius: 12, padding: 16, border: `1px solid ${T.border}` }}>
        <SectionHeader icon={Sprout} title="Nursery & Apiculture Summary" color={T.primary} />
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div>
            <h3 style={{ fontSize: 14, color: T.text, marginBottom: 10 }}>Seedling Nursery</h3>
            <div style={{ fontSize: 12, color: T.textDim, lineHeight: 1.8 }}>
              Monthly capacity: 300,000 seedlings<br />
              Current readiness: {n.seedlingsReady.toLocaleString()}<br />
              Active species: {n.species} varieties<br />
              Revenue this month: ₹5.2 Lakh<br />
              Top sellers: Tomato, Chilli, Brinjal, Marigold
            </div>
          </div>
          <div>
            <h3 style={{ fontSize: 14, color: T.text, marginBottom: 10 }}>Apiculture — 20 Hives</h3>
            <div style={{ fontSize: 12, color: T.textDim, lineHeight: 1.8 }}>
              Active hives: {farm.bees.hives}<br />
              Forager activity: {farm.bees.activeForagers}<br />
              Honey stored: {farm.bees.honeyStored} kg<br />
              Last inspection: {farm.bees.lastInspection}<br />
              Pollination boost: +18% greenhouse yield
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// AI ANALYSIS (with Anthropic API)
// ═══════════════════════════════════════════════════════════════════
function AIView({ farm, setFarm }) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState(farm.aiConversations || []);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversations]);

  const farmContext = useCallback(() => {
    const s = farm.sensors;
    const p = farm.ponds;
    return `LIVE FARM DATA SNAPSHOT:
SENSORS: WaterTemp=${s.waterTemp}°C, DO=${s.dissolvedO2}mg/L, pH=${s.ph}, Ammonia=${s.ammonia}mg/L, SoilMoisture=${s.soilMoisture}%, GH_Temp=${s.ghTemp}°C, GH_Humidity=${s.ghHumidity}%, GH_CO2=${s.ghCO2}ppm, Ambient=${s.ambientTemp}°C, SolarGen=${s.solarGeneration}kW, ReservoirLevel=${s.reservoirLevel}%
PONDS: ${p.map(pd => `${pd.id}(${pd.species}): Stock=${pd.stock}, AvgWt=${pd.avgWeight}kg, DO=${pd.do}, FCR=${pd.fcr}, Mortality=${pd.mortality}%`).join("; ")}
GREENHOUSE: ${farm.greenhouse.map(g => `${g.crop}: ${g.stage}, Health=${g.health}%, Yield=${g.yieldKg}/${g.targetKg}kg, Day${g.daysPlanted}`).join("; ")}
VERTICAL_FARM: ${farm.verticalFarm.map(v => `${v.crop}: Day${v.cycleDay}, Health=${v.health}%, Batch=${v.batchKg}kg`).join("; ")}
POULTRY: Hens=${farm.poultry.hens}, LayRate=${farm.poultry.layRate}%, EggsToday=${farm.poultry.eggsToday}, FeedUsed=${farm.poultry.feedConsumed}kg
DUCKS: ${farm.ducks.count} active, Eggs=${farm.ducks.eggsToday}, Area=${farm.ducks.area}
BEES: ${farm.bees.hives} hives, Honey=${farm.bees.honeyStored}kg
NURSERY: Seedlings=${farm.nursery.seedlingsReady}, Capacity=${farm.nursery.capacityUsed}%
FINANCIAL: YTD_Revenue=₹${farm.financial.ytdRevenue}L, YTD_Expense=₹${farm.financial.ytdExpense}L, YTD_Profit=₹${farm.financial.ytdProfit}L
MARKETS: Hyderabad(Murrel₹${farm.markets.hyderabad.lastPrice.murrel}), Chennai(Murrel₹${farm.markets.chennai.lastPrice.murrel}), Vijayawada, Kadapa, Nellore
ALERTS: ${farm.alerts.slice(0, 5).map(a => a.msg).join("; ")}`;
  }, [farm]);

  const quickAnalyses = [
    { id: "health", label: "🐟 Full Farm Health Check", prompt: "Perform a comprehensive health analysis of the entire farm. Check all pond water quality (DO, pH, ammonia, temperature), greenhouse crop health scores and disease risk, poultry lay rates and ammonia levels, vertical farm nutrient levels. Flag any parameters outside optimal ranges with specific corrective actions. Rate overall farm health 1-10." },
    { id: "financial", label: "💰 Financial Performance Review", prompt: "Analyze the farm's financial performance. Calculate revenue per acre, revenue per worker, EBITDA margin, and compare against targets. Identify the highest and lowest performing revenue streams. Project next quarter revenue based on current trends. Suggest 3 specific actions to improve profitability." },
    { id: "market", label: "📊 Market Strategy Optimizer", prompt: "Analyze current market prices across all 5 cities (Hyderabad, Chennai, Vijayawada, Kadapa, Nellore). Determine the optimal allocation of each product to each market to maximize revenue. Calculate the revenue uplift from optimal routing vs current allocation. Identify arbitrage opportunities where price differentials justify logistics costs." },
    { id: "risk", label: "⚠️ Risk Assessment Report", prompt: "Conduct a comprehensive risk assessment. Evaluate: (1) Disease risk based on water quality trends and weather, (2) Climate risk from current weather patterns, (3) Market risk from price volatility, (4) Equipment failure risk based on automation system status, (5) Water security risk from reservoir levels. Assign risk scores and recommend immediate mitigation actions." },
    { id: "yield", label: "🌱 Yield Optimization Analysis", prompt: "Analyze current crop yields vs targets for all greenhouse crops, vertical farm crops, and aquaculture. Identify underperforming areas. Recommend specific interventions: irrigation adjustments, nutrient changes, stocking density modifications, harvest timing. Calculate the revenue impact of achieving 100% yield targets." },
    { id: "automation", label: "🤖 Automation Efficiency Audit", prompt: "Audit the farm's automation systems. Evaluate irrigation efficiency (soil moisture vs thresholds), fish feeding optimization (FCR improvement opportunities), greenhouse climate control performance, egg collection rates, and drone utilization. Calculate labour hours saved by automation. Recommend upgrades or new automation workflows." },
  ];

  const sendMessage = async (msg) => {
    if (!msg.trim()) return;
    const userMsg = { role: "user", text: msg, time: new Date().toLocaleTimeString() };
    const newConvs = [...conversations, userMsg];
    setConversations(newConvs);
    setQuery("");
    setLoading(true);

    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          system: `You are the AI Farm Analyst for an Integrated Smart Regenerative Farm in Nellore, Andhra Pradesh, India. You have access to live sensor data and operational metrics. Provide expert agricultural analysis with specific, actionable recommendations. Use data-driven insights. Format responses with clear sections, metrics, and priorities. Keep responses focused and practical. Use ₹ for currency. Always reference specific sensor readings and thresholds.

${farmContext()}`,
          messages: [
            ...newConvs.filter(c => c.role === "user" || c.role === "assistant").slice(-6).map(c => ({
              role: c.role === "user" ? "user" : "assistant",
              content: c.text
            })),
          ]
        })
      });
      const data = await response.json();
      const aiText = data.content?.filter(b => b.type === "text").map(b => b.text).join("\n") || "Analysis complete. No specific issues detected at this time.";
      const aiMsg = { role: "assistant", text: aiText, time: new Date().toLocaleTimeString() };
      const updated = [...newConvs, aiMsg];
      setConversations(updated);
      setFarm(prev => ({ ...prev, aiConversations: updated.slice(-20) }));
    } catch (err) {
      const errMsg = { role: "assistant", text: `⚠️ Analysis temporarily unavailable. Error: ${err.message}\n\nTip: The AI analysis connects to Claude API for real-time farm intelligence. Ensure the connection is active.`, time: new Date().toLocaleTimeString() };
      const updated = [...newConvs, errMsg];
      setConversations(updated);
    }
    setLoading(false);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16, height: "calc(100vh - 140px)" }}>
      {/* Quick Analysis Buttons */}
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", flexShrink: 0 }}>
        {quickAnalyses.map(qa => (
          <button key={qa.id} onClick={() => sendMessage(qa.prompt)} disabled={loading}
            style={{
              padding: "8px 14px", borderRadius: 8, border: `1px solid ${T.border}`,
              background: selectedAnalysis === qa.id ? "#00BCD4" + "20" : T.card,
              color: selectedAnalysis === qa.id ? "#00BCD4" : T.textDim,
              cursor: loading ? "not-allowed" : "pointer", fontSize: 12, fontWeight: 500,
              opacity: loading ? 0.5 : 1, transition: "all 0.15s",
            }}>
            {qa.label}
          </button>
        ))}
      </div>

      {/* Chat Area */}
      <div style={{ flex: 1, background: T.card, borderRadius: 12, border: `1px solid ${T.border}`, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        <div style={{ padding: "12px 16px", borderBottom: `1px solid ${T.border}`, display: "flex", alignItems: "center", gap: 8 }}>
          <Brain size={16} color="#00BCD4" />
          <span style={{ fontSize: 14, fontWeight: 600 }}>AI Farm Analyst</span>
          <Badge color="#00BCD4">Powered by Claude</Badge>
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: 16, display: "flex", flexDirection: "column", gap: 12 }}>
          {conversations.length === 0 && (
            <div style={{ textAlign: "center", padding: "40px 20px", color: T.textMuted }}>
              <Brain size={40} color={T.textMuted} style={{ marginBottom: 12 }} />
              <div style={{ fontSize: 14, marginBottom: 8 }}>AI Farm Analysis Ready</div>
              <div style={{ fontSize: 12 }}>Ask any question about your farm or click a quick analysis above. The AI has access to all live sensor data, financial metrics, and operational parameters.</div>
            </div>
          )}
          {conversations.map((msg, i) => (
            <div key={i} style={{ display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start" }}>
              <div style={{
                maxWidth: "85%", padding: "10px 14px", borderRadius: 12,
                background: msg.role === "user" ? T.primary + "25" : T.bg,
                border: `1px solid ${msg.role === "user" ? T.primary + "40" : T.border}`,
              }}>
                <div style={{ fontSize: 10, color: T.textMuted, marginBottom: 4 }}>
                  {msg.role === "user" ? "You" : "🤖 AI Analyst"} • {msg.time}
                </div>
                <div style={{ fontSize: 12, color: T.text, lineHeight: 1.7, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>{msg.text}</div>
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ display: "flex", gap: 8, alignItems: "center", padding: "10px 14px", background: T.bg, borderRadius: 12, border: `1px solid ${T.border}`, maxWidth: "60%" }}>
              <Loader2 size={14} color="#00BCD4" style={{ animation: "spin 1s linear infinite" }} />
              <span style={{ fontSize: 12, color: T.textDim }}>Analyzing farm data...</span>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input */}
        <div style={{ padding: "12px 16px", borderTop: `1px solid ${T.border}`, display: "flex", gap: 10 }}>
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !loading && sendMessage(query)}
            placeholder="Ask about water quality, crop health, financials, market strategy..."
            style={{
              flex: 1, padding: "10px 14px", borderRadius: 8, border: `1px solid ${T.border}`,
              background: T.bg, color: T.text, fontSize: 13, outline: "none",
            }}
          />
          <button onClick={() => sendMessage(query)} disabled={loading || !query.trim()}
            style={{
              padding: "10px 18px", borderRadius: 8, border: "none",
              background: loading || !query.trim() ? T.border : "#00BCD4",
              color: T.white, cursor: loading || !query.trim() ? "not-allowed" : "pointer",
              display: "flex", alignItems: "center", gap: 6, fontSize: 13, fontWeight: 600,
            }}>
            <Send size={14} /> Analyze
          </button>
        </div>
      </div>

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
