/**
 * Navigation / screen registry.
 * Each entry is used by both the drawer (desktop/tablet) and
 * the bottom tab bar (mobile), so icons and colors stay consistent.
 */
import {
  Home, Fish, Leaf, Sprout, Egg,
  Droplets, Sun, Zap, Truck, DollarSign, Brain,
} from "lucide-react-native";
import { colors } from "./theme";

export const SCREENS = [
  { name: "Dashboard",    label: "Dashboard",      Icon: Home,       color: colors.primary },
  { name: "Aquaculture",  label: "Aquaculture",    Icon: Fish,       color: colors.fish },
  { name: "Greenhouse",   label: "Greenhouse",     Icon: Leaf,       color: colors.crop },
  { name: "VerticalFarm", label: "Vertical Farm",  Icon: Sprout,     color: colors.verticalFarm },
  { name: "Poultry",      label: "Poultry & Duck", Icon: Egg,        color: colors.poultry },
  { name: "Water",        label: "Water System",   Icon: Droplets,   color: colors.water },
  { name: "Energy",       label: "Solar Energy",   Icon: Sun,        color: colors.solar },
  { name: "Automation",   label: "Automation",     Icon: Zap,        color: colors.danger },
  { name: "Market",       label: "Markets",        Icon: Truck,      color: colors.market },
  { name: "Financial",    label: "Financials",     Icon: DollarSign, color: colors.accent },
  { name: "Nursery",      label: "Nursery & Bees", Icon: Sprout,     color: colors.primary },
  { name: "AI",           label: "AI Analysis",    Icon: Brain,      color: colors.ai },
];
