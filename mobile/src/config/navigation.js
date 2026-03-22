/**
 * Navigation / screen registry.
 * Each entry is used by both the drawer (desktop/tablet) and
 * the bottom tab bar (mobile), so icons and colors stay consistent.
 *
 * `section` groups screens into department buckets rendered as
 * collapsible headers in the sidebar.
 */
import {
  Home, Fish, Leaf, Sprout, Egg,
  Droplets, Sun, Zap, Truck, DollarSign, Brain, Users,
  Store, ShoppingCart, ScanLine, Package,
  BarChart3, ClipboardList, Wrench, Activity, Box, MapPin, Settings,
  Bug, Plane, Shield, FileText, Layers,
} from "lucide-react-native";
import { colors } from "./theme";

/** Department sections rendered as sidebar group headers. */
export const SECTIONS = [
  { key: "operations", label: "Farm Operations"       },
  { key: "quality",    label: "Quality & Compliance"  },
  { key: "supply",     label: "Stock & Supply Chain"  },
  { key: "retail",     label: "Store & Sales"         },
  { key: "finance",    label: "Finance"               },
  { key: "admin",      label: "Admin"                 },
];

export const SCREENS = [
  // ── Farm Operations ───────────────────────────────────────────
  { name: "Dashboard",       label: "Dashboard",         Icon: Home,          color: colors.primary,     section: "operations" },
  { name: "Aquaculture",     label: "Aquaculture",        Icon: Fish,          color: colors.fish,        section: "operations" },
  { name: "Greenhouse",      label: "Greenhouse",         Icon: Leaf,          color: colors.crop,        section: "operations" },
  { name: "VerticalFarm",    label: "Vertical Farm",      Icon: Sprout,        color: colors.verticalFarm,section: "operations" },
  { name: "Poultry",         label: "Poultry & Duck",     Icon: Egg,           color: colors.poultry,     section: "operations" },
  { name: "Water",           label: "Water System",       Icon: Droplets,      color: colors.water,       section: "operations" },
  { name: "Energy",          label: "Solar Energy",       Icon: Sun,           color: colors.solar,       section: "operations" },
  { name: "Automation",      label: "Automation",         Icon: Zap,           color: colors.danger,      section: "operations" },
  { name: "Nursery",         label: "Nursery & Bees",     Icon: Sprout,        color: colors.primary,     section: "operations" },
  { name: "NurseryBE",       label: "Nursery Orders",     Icon: Layers,        color: "#26A69A",          section: "operations" },
  { name: "FeedProduction",  label: "Feed Production",    Icon: Bug,           color: "#8D6E63",          section: "operations" },
  { name: "Drones",          label: "Drones",             Icon: Plane,         color: "#29B6F6",          section: "operations" },

  // ── Quality & Compliance ──────────────────────────────────────
  { name: "QA",              label: "QA & Traceability",  Icon: Shield,        color: "#66BB6A",          section: "quality"    },
  { name: "Compliance",      label: "Compliance",         Icon: FileText,      color: "#5C6BC0",          section: "quality"    },

  // ── Stock & Supply Chain ──────────────────────────────────────
  { name: "StockProduced",   label: "Stock Produced",     Icon: Box,           color: colors.crop,        section: "supply"     },
  { name: "StockSales",      label: "Stock Sales",        Icon: BarChart3,     color: colors.market,      section: "supply"     },
  { name: "Packing",         label: "Packing",            Icon: Package,       color: colors.packing,     section: "supply"     },
  { name: "Scanner",         label: "Scan Barcode",       Icon: ScanLine,      color: colors.scanner,     section: "supply"     },
  { name: "Logistics",       label: "Logistics",          Icon: MapPin,        color: colors.logistics,   section: "supply"     },

  // ── Store & Sales ─────────────────────────────────────────────
  { name: "Store",           label: "Store",              Icon: Store,         color: colors.store,       section: "retail"     },
  { name: "POS",             label: "Point of Sale",      Icon: ShoppingCart,  color: colors.pos,         section: "retail"     },
  { name: "Market",          label: "Markets",            Icon: Truck,         color: colors.market,      section: "retail"     },

  // ── Finance ───────────────────────────────────────────────────
  { name: "Financial",       label: "Financials",         Icon: DollarSign,    color: colors.accent,      section: "finance"    },
  { name: "Reports",         label: "Reports",            Icon: ClipboardList, color: colors.reports,     section: "finance"    },

  // ── Admin ─────────────────────────────────────────────────────
  { name: "AI",              label: "AI Analysis",        Icon: Brain,         color: colors.ai,          section: "admin"      },
  { name: "ServiceRequests", label: "Service Requests",   Icon: Wrench,        color: colors.service,     section: "admin"      },
  { name: "ActivityLog",     label: "Activity Log",       Icon: Activity,      color: colors.textDim,     section: "admin"      },
  { name: "Users",           label: "User Management",    Icon: Users,         color: colors.info,        section: "admin"      },
  { name: "Roles",           label: "Role Management",    Icon: Shield,        color: "#6A1B9A",          section: "admin"      },
  { name: "Settings",        label: "Settings",           Icon: Settings,      color: colors.textDim,     section: "admin"      },
];
