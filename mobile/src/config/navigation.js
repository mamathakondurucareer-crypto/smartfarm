/**
 * Navigation / screen registry.
 * Each entry is used by both the drawer (desktop/tablet) and
 * the bottom tab bar (mobile), so icons and colors stay consistent.
 */
import {
  Home, Fish, Leaf, Sprout, Egg,
  Droplets, Sun, Zap, Truck, DollarSign, Brain, Users,
  Store, ShoppingCart, ScanLine, Package,
  BarChart3, ClipboardList, Wrench, Activity, Box, MapPin, Settings,
  Bug, Plane, Shield, FileText, Layers,
} from "lucide-react-native";
import { colors } from "./theme";

export const SCREENS = [
  // ── Farm Operations ───────────────────────────────────────────
  { name: "Dashboard",        label: "Dashboard",        Icon: Home,          color: colors.primary },
  { name: "Aquaculture",      label: "Aquaculture",      Icon: Fish,          color: colors.fish },
  { name: "Greenhouse",       label: "Greenhouse",       Icon: Leaf,          color: colors.crop },
  { name: "VerticalFarm",     label: "Vertical Farm",    Icon: Sprout,        color: colors.verticalFarm },
  { name: "Poultry",          label: "Poultry & Duck",   Icon: Egg,           color: colors.poultry },
  { name: "Water",            label: "Water System",     Icon: Droplets,      color: colors.water },
  { name: "Energy",           label: "Solar Energy",     Icon: Sun,           color: colors.solar },
  { name: "Automation",       label: "Automation",       Icon: Zap,           color: colors.danger },
  { name: "Nursery",          label: "Nursery & Bees",   Icon: Sprout,        color: colors.primary },

  // ── Stock & Supply Chain ──────────────────────────────────────
  { name: "StockProduced",    label: "Stock Produced",   Icon: Box,           color: colors.crop },
  { name: "StockSales",       label: "Stock Sales",      Icon: BarChart3,     color: colors.market },
  { name: "Packing",          label: "Packing",          Icon: Package,       color: colors.packing },
  { name: "Scanner",          label: "Scan Barcode",     Icon: ScanLine,      color: colors.scanner },

  // ── Store & Retail ────────────────────────────────────────────
  { name: "Store",            label: "Store",            Icon: Store,         color: colors.store },
  { name: "POS",              label: "Point of Sale",    Icon: ShoppingCart,  color: colors.pos },
  { name: "Logistics",        label: "Logistics",        Icon: MapPin,        color: colors.logistics },

  // ── Finance & Markets ─────────────────────────────────────────
  { name: "Market",           label: "Markets",          Icon: Truck,         color: colors.market },
  { name: "Financial",        label: "Financials",       Icon: DollarSign,    color: colors.accent },
  { name: "Reports",          label: "Reports",          Icon: ClipboardList, color: colors.reports },

  // ── Admin & AI ────────────────────────────────────────────────
  { name: "AI",               label: "AI Analysis",      Icon: Brain,         color: colors.ai },
  { name: "ServiceRequests",  label: "Service Requests", Icon: Wrench,        color: colors.service },
  { name: "ActivityLog",      label: "Activity Log",     Icon: Activity,      color: colors.textDim },
  { name: "Users",            label: "User Management",  Icon: Users,         color: colors.info },
  { name: "Settings",         label: "Settings",         Icon: Settings,      color: colors.textDim },

  // ── New Modules ───────────────────────────────────────────────
  { name: "FeedProduction",   label: "Feed Production",  Icon: Bug,           color: "#8D6E63" },
  { name: "Drones",           label: "Drones",           Icon: Plane,         color: "#29B6F6" },
  { name: "QA",               label: "QA & Traceability",Icon: Shield,        color: "#66BB6A" },
  { name: "Compliance",       label: "Compliance",       Icon: FileText,      color: "#5C6BC0" },
  { name: "NurseryBE",        label: "Nursery Orders",   Icon: Layers,        color: "#26A69A" },
];
