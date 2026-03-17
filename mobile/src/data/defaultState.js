/** Default farm state for first launch / empty storage. */

export const defaultSensors = () => ({
  waterTemp: 26.0,   dissolvedO2: 6.0,  ph: 7.2,       ammonia: 0.0,
  turbidity: 0,      soilMoisture: 0,   soilTemp: 0,    soilEC: 0,
  ghTemp: 28.0,      ghHumidity: 70,    ghCO2: 400,     ghLight: 600,
  ambientTemp: 30.0, humidity: 60,      windSpeed: 5.0, rainfall: 0,
  solarRad: 600,     reservoirLevel: 0, headerTankLevel: 0,
  solarGeneration: 0, gridExport: 0,    farmConsumption: 0,
  eggCount: 0,       feedLevel: 0,      poultryTemp: 28.0, poultryAmmonia: 0,
  vfTemp: 24.0,      vfHumidity: 65,    vfNutrientEC: 0, vfPH: 6.0,
});

export const defaultFarmState = () => ({
  sensors: defaultSensors(),

  alerts: [],

  ponds: [],

  greenhouse: [],

  verticalFarm: [],

  poultry: { hens: 0, layRate: 0, eggsToday: 0, eggsBroken: 0, feedConsumed: 0, mortality: 0, waterUsage: 0 },
  ducks:   { count: 0, eggsToday: 0, pestsConsumed: "—", area: "—" },
  bees:    { hives: 0, activeForagers: "—", honeyStored: 0, lastInspection: "—" },
  nursery: { seedlingsReady: 0, ordersThisMonth: 0, capacityUsed: 0, species: 0 },

  financial: {
    monthlyRevenue: [],
    expenses:   { feed: 0, labour: 0, power: 0, maintenance: 0, logistics: 0, overhead: 0 },
    ytdRevenue: 0,
    ytdExpense: 0,
    ytdProfit:  0,
  },

  markets: {
    hyderabad:  { lastPrice: { murrel: 0, rohu: 0, tomato: 0, chilli: 0 }, trend: "—" },
    chennai:    { lastPrice: { murrel: 0, rohu: 0, tomato: 0, chilli: 0 }, trend: "—" },
    vijayawada: { lastPrice: { murrel: 0, rohu: 0, tomato: 0, chilli: 0 }, trend: "—" },
    kadapa:     { lastPrice: { murrel: 0, rohu: 0, tomato: 0, chilli: 0 }, trend: "—" },
    nellore:    { lastPrice: { murrel: 0, rohu: 0, tomato: 0, chilli: 0 }, trend: "—" },
  },

  automation: {
    irrigation:    { status: "Idle", zonesActive: 0, totalZones: 5, lastRun: "—" },
    fishFeeder:    { status: "Idle", nextFeed: "—", todayFeeds: 0, totalFeeds: 0 },
    eggBelt:       { status: "Idle", collected: 0, target: 0, startTime: "—" },
    manureScraper: { status: "Idle", nextRun: "—", todayRuns: 0, totalRuns: 0 },
    ghClimate:     { status: "Idle", curtains: "Closed", fans: "OFF", pad: "OFF" },
    drone:         { status: "Docked", battery: 0, lastFlight: "—", nextScheduled: "—" },
  },

  aiConversations: [],
  enabledModules: {
    Dashboard: true, Aquaculture: true, Greenhouse: true, VerticalFarm: true,
    Poultry: true, Water: true, Energy: true, Automation: true, Nursery: true,
    StockProduced: true, StockSales: true, Packing: true, Scanner: true,
    Store: true, POS: true, Logistics: true, Market: true, Financial: true,
    Reports: true, AI: true, ServiceRequests: true, ActivityLog: true,
    Users: true, Settings: true,
    FeedProduction: true, Drones: true, QA: true, Compliance: true, NurseryBE: true,
  },
  lastUpdated: Date.now(),
});
