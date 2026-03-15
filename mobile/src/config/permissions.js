/**
 * Role-based access configuration.
 *
 * Roles (from backend RoleEnum — all uppercase on frontend):
 *   Farm:  ADMIN, MANAGER, SUPERVISOR, WORKER, VIEWER
 *   Store: STORE_MANAGER, CASHIER, PACKER, DRIVER, SCANNER
 */

export const ROLES = {
  ADMIN:         "ADMIN",
  MANAGER:       "MANAGER",
  SUPERVISOR:    "SUPERVISOR",
  WORKER:        "WORKER",
  VIEWER:        "VIEWER",
  STORE_MANAGER: "STORE_MANAGER",
  CASHIER:       "CASHIER",
  PACKER:        "PACKER",
  DRIVER:        "DRIVER",
  SCANNER:       "SCANNER",
};

export const ALL_ROLES = Object.values(ROLES);

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
  // Farm ops
  Dashboard:       ALL_ROLES,
  Aquaculture:     [...FARM_OPS, "STORE_MANAGER"],
  Greenhouse:      [...FARM_OPS, "STORE_MANAGER"],
  VerticalFarm:    [...FARM_OPS, "STORE_MANAGER"],
  Poultry:         [...FARM_OPS, "STORE_MANAGER"],
  Water:           FARM_OPS,
  Energy:          FARM_MGMT,
  Automation:      FARM_MGMT,
  Nursery:         FARM_MGMT,

  // Stock & supply chain
  StockProduced:   [...ADMIN_MGR, "SUPERVISOR", "STORE_MANAGER"],
  StockSales:      [...ADMIN_MGR, "STORE_MANAGER"],
  Packing:         [...ADMIN_MGR, "SUPERVISOR", "STORE_MANAGER", "PACKER"],
  Scanner:         [...ALL_ROLES],   // all roles can scan

  // Store & retail
  Store:           STORE_STAFF,
  POS:             ["ADMIN", "STORE_MANAGER", "CASHIER"],
  Logistics:       [...ADMIN_MGR, "STORE_MANAGER", "DRIVER"],

  // Finance & markets
  Market:          ADMIN_MGR,
  Financial:       ADMIN_MGR,
  Reports:         [...ADMIN_MGR, "STORE_MANAGER"],

  // Admin & AI
  AI:              FARM_MGMT,
  ServiceRequests: ALL_ROLES,   // everyone can submit
  ActivityLog:     ADMIN_MGR,
  Users:           ADMIN_MGR,
};

export const canAccessScreen = (screenName, role) => {
  const allowed = SCREEN_ACCESS[screenName];
  if (!allowed) return true;               // unlisted screens: open to all
  return allowed.includes((role || "").toUpperCase());
};
