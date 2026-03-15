/** Default farm state for first launch / empty storage. */

export const defaultSensors = () => ({
  waterTemp: 26.4,   dissolvedO2: 6.2,  ph: 7.4,       ammonia: 0.01,
  turbidity: 12,     soilMoisture: 42,  soilTemp: 28.3, soilEC: 1.8,
  ghTemp: 32.1,      ghHumidity: 72,    ghCO2: 420,     ghLight: 680,
  ambientTemp: 34.2, humidity: 65,      windSpeed: 8.4, rainfall: 0,
  solarRad: 820,     reservoirLevel: 78,headerTankLevel: 85,
  solarGeneration: 92.4, gridExport: 18.6, farmConsumption: 73.8,
  eggCount: 695,     feedLevel: 62,     poultryTemp: 28.5, poultryAmmonia: 8,
  vfTemp: 24.2,      vfHumidity: 68,    vfNutrientEC: 2.1, vfPH: 6.0,
});

export const defaultFarmState = () => ({
  sensors: defaultSensors(),

  alerts: [
    { id: 1, type: "warning", msg: "Pond P2 DO dropping — 4.8 mg/L",           time: "10 min ago",  system: "Aquaculture" },
    { id: 2, type: "info",    msg: "Greenhouse 1 auto-ventilation activated",   time: "25 min ago",  system: "Greenhouse" },
    { id: 3, type: "success", msg: "Solar generation optimal — 92.4 kW",        time: "1 hr ago",    system: "Energy" },
    { id: 4, type: "info",    msg: "Drone NDVI flight completed",               time: "2 hr ago",    system: "Technology" },
  ],

  ponds: [
    { id: "P1", species: "Murrel",           stock: 3800,  avgWeight: 0.62, fcr: 1.78, do: 5.8, mortality: 1.2, feedToday: 42 },
    { id: "P2", species: "Murrel",           stock: 3750,  avgWeight: 0.58, fcr: 1.82, do: 4.8, mortality: 1.5, feedToday: 40 },
    { id: "P3", species: "Rohu/Catla/Grass", stock: 5800,  avgWeight: 0.45, fcr: 2.10, do: 6.5, mortality: 0.8, feedToday: 55 },
    { id: "P4", species: "Common/Rohu",      stock: 5600,  avgWeight: 0.42, fcr: 2.15, do: 6.2, mortality: 0.9, feedToday: 52 },
    { id: "P5", species: "Nursery",          stock: 12000, avgWeight: 0.02, fcr: 0,    do: 7.1, mortality: 2.0, feedToday: 8 },
    { id: "P6", species: "Mud Crab",         stock: 480,   avgWeight: 0.38, fcr: 3.20, do: 5.5, mortality: 3.5, feedToday: 15 },
  ],

  greenhouse: [
    { id: "GH1-Chilli",   crop: "Green Chilli", stage: "Fruiting",   daysPlanted: 85, health: 92, yieldKg: 2400,  targetKg: 9000 },
    { id: "GH1-Tomato",   crop: "Tomato",       stage: "Flowering",  daysPlanted: 62, health: 88, yieldKg: 1800,  targetKg: 16000 },
    { id: "GH1-Cucumber", crop: "Cucumber",     stage: "Harvesting", daysPlanted: 48, health: 95, yieldKg: 4200,  targetKg: 13000 },
    { id: "GH2-Ridge",    crop: "Ridge Gourd",  stage: "Vegetative", daysPlanted: 28, health: 90, yieldKg: 800,   targetKg: 7000 },
    { id: "GH2-Bitter",   crop: "Bitter Gourd", stage: "Flowering",  daysPlanted: 42, health: 86, yieldKg: 1200,  targetKg: 6000 },
  ],

  verticalFarm: [
    { crop: "Spinach",    tier: "1-2", cycleDay: 18, health: 96, batchKg: 120, cyclesLeft: 2 },
    { crop: "Coriander",  tier: "3-4", cycleDay: 22, health: 94, batchKg: 95,  cyclesLeft: 1 },
    { crop: "Fenugreek",  tier: "5",   cycleDay: 14, health: 98, batchKg: 85,  cyclesLeft: 3 },
    { crop: "Amaranthus", tier: "6",   cycleDay: 20, health: 92, batchKg: 110, cyclesLeft: 2 },
  ],

  poultry: { hens: 792, layRate: 87.5, eggsToday: 695, eggsBroken: 4, feedConsumed: 89, mortality: 0, waterUsage: 1200 },
  ducks:   { count: 395, eggsToday: 310, pestsConsumed: "High", area: "Pond P3-P4 perimeter" },
  bees:    { hives: 20, activeForagers: "High", honeyStored: 42, lastInspection: "3 days ago" },
  nursery: { seedlingsReady: 185000, ordersThisMonth: 12, capacityUsed: 72, species: 24 },

  financial: {
    monthlyRevenue: [
      { month: "Jul", aqua: 8.2,  gh: 1.5, vf: 2.0, field: 0,   poultry: 2.8, nursery: 4.2, other: 2.5 },
      { month: "Aug", aqua: 9.1,  gh: 1.8, vf: 2.2, field: 0,   poultry: 2.9, nursery: 4.5, other: 2.8 },
      { month: "Sep", aqua: 10.5, gh: 1.6, vf: 2.1, field: 3.2, poultry: 3.0, nursery: 4.8, other: 3.0 },
      { month: "Oct", aqua: 11.2, gh: 1.9, vf: 2.4, field: 5.8, poultry: 3.1, nursery: 5.2, other: 3.5 },
      { month: "Nov", aqua: 10.8, gh: 2.1, vf: 2.3, field: 8.2, poultry: 3.2, nursery: 5.0, other: 4.0 },
      { month: "Dec", aqua: 12.0, gh: 2.0, vf: 2.5, field: 6.5, poultry: 3.0, nursery: 4.8, other: 4.5 },
    ],
    expenses:   { feed: 5.8, labour: 1.5, power: 0, maintenance: 0.8, logistics: 1.2, overhead: 1.3 },
    ytdRevenue: 182.4,
    ytdExpense: 63.6,
    ytdProfit:  118.8,
  },

  markets: {
    hyderabad:  { lastPrice: { murrel: 520, rohu: 145, tomato: 38, chilli: 65 }, trend: "up" },
    chennai:    { lastPrice: { murrel: 620, rohu: 155, tomato: 42, chilli: 58 }, trend: "stable" },
    vijayawada: { lastPrice: { murrel: 480, rohu: 135, tomato: 32, chilli: 55 }, trend: "up" },
    kadapa:     { lastPrice: { murrel: 440, rohu: 125, tomato: 28, chilli: 50 }, trend: "down" },
    nellore:    { lastPrice: { murrel: 400, rohu: 120, tomato: 25, chilli: 48 }, trend: "stable" },
  },

  automation: {
    irrigation:    { status: "Active",    zonesActive: 3, totalZones: 5, lastRun: "06:30 AM" },
    fishFeeder:    { status: "Scheduled", nextFeed: "12:00 PM", todayFeeds: 1, totalFeeds: 3 },
    eggBelt:       { status: "Running",   collected: 695, target: 720, startTime: "08:00 AM" },
    manureScraper: { status: "Idle",      nextRun: "06:00 PM", todayRuns: 1, totalRuns: 2 },
    ghClimate:     { status: "Active",    curtains: "Open", fans: "OFF", pad: "OFF" },
    drone:         { status: "Docked",    battery: 94, lastFlight: "07:30 AM", nextScheduled: "3:00 PM" },
  },

  aiConversations: [],
  lastUpdated: Date.now(),
});
