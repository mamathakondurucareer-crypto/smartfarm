/**
 * Role-based access configuration.
 *
 * Roles (all uppercase on frontend):
 *   Farm:      ADMIN, MANAGER, SUPERVISOR, WORKER, VIEWER
 *   Store:     STORE_MANAGER, CASHIER, PACKER, DRIVER, SCANNER
 *   Specialist: AQUA_TECH, GREENHOUSE_TECH, POULTRY_TECH, FIELD_WORKER,
 *               QA_OFFICER, FINANCE_ADMIN, DRONE_OPS
 */
import { colors } from "./theme";

export const ROLES = {
  // ── Farm management ──────────────────────────────────────────────
  ADMIN:            "ADMIN",
  MANAGER:          "MANAGER",
  SUPERVISOR:       "SUPERVISOR",
  WORKER:           "WORKER",
  VIEWER:           "VIEWER",

  // ── Store / retail ───────────────────────────────────────────────
  STORE_MANAGER:    "STORE_MANAGER",
  CASHIER:          "CASHIER",
  PACKER:           "PACKER",
  DRIVER:           "DRIVER",
  SCANNER:          "SCANNER",

  // ── Specialist / department roles ────────────────────────────────
  AQUA_TECH:        "AQUA_TECH",
  GREENHOUSE_TECH:  "GREENHOUSE_TECH",
  POULTRY_TECH:     "POULTRY_TECH",
  FIELD_WORKER:     "FIELD_WORKER",
  QA_OFFICER:       "QA_OFFICER",
  FINANCE_ADMIN:    "FINANCE_ADMIN",
  DRONE_OPS:        "DRONE_OPS",
};

export const ALL_ROLES = Object.values(ROLES);

// ── Shorthand groups ──────────────────────────────────────────────────────────
const FARM_OPS   = ["ADMIN", "MANAGER", "SUPERVISOR", "WORKER"];
const FARM_MGMT  = ["ADMIN", "MANAGER", "SUPERVISOR"];
const ADMIN_MGR  = ["ADMIN", "MANAGER"];
const STORE_STAFF = ["ADMIN", "MANAGER", "STORE_MANAGER", "CASHIER"];
const STORE_MGMT  = ["ADMIN", "MANAGER", "STORE_MANAGER"];

/**
 * Which roles can access each screen.
 * Screens not listed here are accessible to all authenticated users.
 */
export const SCREEN_ACCESS = {
  // ── Farm operations ───────────────────────────────────────────────────────
  Dashboard:       ALL_ROLES,
  Aquaculture:     [...FARM_OPS, "STORE_MANAGER", "AQUA_TECH"],
  Greenhouse:      [...FARM_OPS, "STORE_MANAGER", "GREENHOUSE_TECH"],
  VerticalFarm:    [...FARM_OPS, "STORE_MANAGER", "GREENHOUSE_TECH"],
  Poultry:         [...FARM_OPS, "STORE_MANAGER", "POULTRY_TECH"],
  Water:           [...FARM_OPS, "AQUA_TECH", "GREENHOUSE_TECH", "FIELD_WORKER"],
  Energy:          FARM_MGMT,
  Automation:      [...FARM_MGMT, "DRONE_OPS"],
  Nursery:         [...FARM_MGMT, "GREENHOUSE_TECH"],
  NurseryBE:       [...FARM_MGMT, "GREENHOUSE_TECH"],
  FeedProduction:  [...FARM_OPS, "AQUA_TECH", "POULTRY_TECH"],
  Drones:          [...FARM_MGMT, "DRONE_OPS", "FIELD_WORKER"],

  // ── Quality & compliance ──────────────────────────────────────────────────
  QA:              [...FARM_MGMT, "QA_OFFICER", "AQUA_TECH", "GREENHOUSE_TECH", "POULTRY_TECH"],
  Compliance:      [...ADMIN_MGR, "QA_OFFICER"],

  // ── Stock & supply chain ──────────────────────────────────────────────────
  StockProduced:   [...ADMIN_MGR, "SUPERVISOR", "STORE_MANAGER", "AQUA_TECH", "GREENHOUSE_TECH", "POULTRY_TECH"],
  StockSales:      [...ADMIN_MGR, "STORE_MANAGER"],
  Packing:         [...ADMIN_MGR, "SUPERVISOR", "STORE_MANAGER", "PACKER"],
  Scanner:         ALL_ROLES,
  Logistics:       [...ADMIN_MGR, "STORE_MANAGER", "DRIVER"],

  // ── Store & retail ────────────────────────────────────────────────────────
  Store:           STORE_STAFF,
  POS:             ["ADMIN", "STORE_MANAGER", "CASHIER"],
  Market:          [...ADMIN_MGR, "FINANCE_ADMIN"],

  // ── Finance ───────────────────────────────────────────────────────────────
  Financial:       [...ADMIN_MGR, "FINANCE_ADMIN"],
  Reports:         [...ADMIN_MGR, "STORE_MANAGER", "QA_OFFICER", "FINANCE_ADMIN"],

  // ── Admin & AI ────────────────────────────────────────────────────────────
  AI:              FARM_MGMT,
  ServiceRequests: ALL_ROLES,
  ActivityLog:     [...ADMIN_MGR, "QA_OFFICER"],
  Users:           ADMIN_MGR,
  Roles:           ["ADMIN"],
  Settings:        ADMIN_MGR,
};

/**
 * Human-readable metadata for each role — shown in the Roles screen.
 */
export const ROLE_META = {
  ADMIN:           { label: "Admin",              color: colors.danger,    description: "Full system access — all screens and settings." },
  MANAGER:         { label: "Manager",            color: colors.accent,    description: "Farm and store management, finance, and reporting." },
  SUPERVISOR:      { label: "Supervisor",         color: colors.info,      description: "Farm operations, quality, and stock oversight." },
  WORKER:          { label: "Worker",             color: colors.primary,   description: "Day-to-day farm operations and scanning." },
  VIEWER:          { label: "Viewer",             color: colors.textMuted, description: "Read-only dashboard and service requests." },
  STORE_MANAGER:   { label: "Store Manager",      color: "#FF7043",        description: "Store, POS, stock, logistics, and packing." },
  CASHIER:         { label: "Cashier",            color: "#FFA726",        description: "Point-of-sale and store operations." },
  PACKER:          { label: "Packer",             color: "#8D6E63",        description: "Packing station and barcode scanner." },
  DRIVER:          { label: "Driver",             color: "#29B6F6",        description: "Logistics and route tracking." },
  SCANNER:         { label: "Scanner",            color: colors.textDim,   description: "Barcode scanning only." },
  AQUA_TECH:       { label: "Aqua Technician",    color: "#0288D1",        description: "Aquaculture, feed production, water, stock, and QA for aqua operations." },
  GREENHOUSE_TECH: { label: "Greenhouse Tech",    color: "#2E7D32",        description: "Greenhouse, vertical farm, nursery, water management, and related stock." },
  POULTRY_TECH:    { label: "Poultry Technician", color: "#F57F17",        description: "Poultry & duck operations, feed production, stock, and QA." },
  FIELD_WORKER:    { label: "Field Worker",       color: "#558B2F",        description: "Water systems, drones, and general farm support." },
  QA_OFFICER:      { label: "QA Officer",         color: "#6A1B9A",        description: "Quality assurance, compliance, reporting, and activity logs." },
  FINANCE_ADMIN:   { label: "Finance Admin",      color: "#00695C",        description: "Financial management, market data, and reports." },
  DRONE_OPS:       { label: "Drone Operator",     color: "#1565C0",        description: "Drone fleet management and automation oversight." },
};

export const canAccessScreen = (screenName, role) => {
  const allowed = SCREEN_ACCESS[screenName];
  if (!allowed) return true;               // unlisted screens: open to all
  return allowed.includes((role || "").toUpperCase());
};
