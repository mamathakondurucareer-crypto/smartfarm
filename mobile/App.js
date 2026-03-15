/**
 * SmartFarm OS — App entry point.
 *
 * Navigation strategy:
 *   mobile  (<768px)  → drawer hidden, opened via header hamburger menu
 *   tablet / desktop  → drawer permanently visible on the left
 *
 * All screens are lazy-loaded via the drawer navigator.
 */
import "react-native-gesture-handler";
import React, { useEffect, useRef } from "react";
import { NavigationContainer }       from "@react-navigation/native";
import { createDrawerNavigator }     from "@react-navigation/drawer";
import { SafeAreaProvider }          from "react-native-safe-area-context";
import { StatusBar }                 from "expo-status-bar";

import { useResponsive }    from "./src/hooks/useResponsive";
import useFarmStore         from "./src/store/useFarmStore";
import DrawerContent        from "./src/components/layout/DrawerContent";
import { colors }           from "./src/config/theme";

// ─── Screens ─────────────────────────────────────────────────────
import DashboardScreen    from "./src/screens/DashboardScreen";
import AquacultureScreen  from "./src/screens/AquacultureScreen";
import GreenhouseScreen   from "./src/screens/GreenhouseScreen";
import VerticalFarmScreen from "./src/screens/VerticalFarmScreen";
import PoultryScreen      from "./src/screens/PoultryScreen";
import WaterScreen        from "./src/screens/WaterScreen";
import EnergyScreen       from "./src/screens/EnergyScreen";
import AutomationScreen   from "./src/screens/AutomationScreen";
import MarketScreen       from "./src/screens/MarketScreen";
import FinancialScreen    from "./src/screens/FinancialScreen";
import NurseryScreen      from "./src/screens/NurseryScreen";
import AIScreen           from "./src/screens/AIScreen";

const Drawer = createDrawerNavigator();

// ─── Inner navigator (uses responsive hook inside NavigationContainer) ──
function AppNavigator() {
  const { showPermanentDrawer, drawerWidth } = useResponsive();

  return (
    <Drawer.Navigator
      drawerContent={(props) => <DrawerContent {...props} />}
      screenOptions={{
        headerShown:         false,          // Each screen has its own ScreenWrapper header
        drawerType:          showPermanentDrawer ? "permanent" : "front",
        drawerStyle:         { width: drawerWidth, backgroundColor: colors.card },
        overlayColor:        "rgba(0,0,0,0.5)",
        swipeEnabled:        !showPermanentDrawer,
        sceneContainerStyle: { backgroundColor: colors.bg },
      }}
    >
      <Drawer.Screen name="Dashboard"    component={DashboardScreen} />
      <Drawer.Screen name="Aquaculture"  component={AquacultureScreen} />
      <Drawer.Screen name="Greenhouse"   component={GreenhouseScreen} />
      <Drawer.Screen name="VerticalFarm" component={VerticalFarmScreen} />
      <Drawer.Screen name="Poultry"      component={PoultryScreen} />
      <Drawer.Screen name="Water"        component={WaterScreen} />
      <Drawer.Screen name="Energy"       component={EnergyScreen} />
      <Drawer.Screen name="Automation"   component={AutomationScreen} />
      <Drawer.Screen name="Market"       component={MarketScreen} />
      <Drawer.Screen name="Financial"    component={FinancialScreen} />
      <Drawer.Screen name="Nursery"      component={NurseryScreen} />
      <Drawer.Screen name="AI"           component={AIScreen} />
    </Drawer.Navigator>
  );
}

// ─── Root ────────────────────────────────────────────────────────
export default function App() {
  const loadFromStorage = useFarmStore((s) => s.loadFromStorage);
  const simRunning      = useFarmStore((s) => s.simRunning);
  const tickSensors     = useFarmStore((s) => s.tickSensors);
  const intervalRef     = useRef(null);

  // Load persisted state on mount
  useEffect(() => { loadFromStorage(); }, []);

  // Start / stop sensor simulation interval
  useEffect(() => {
    if (simRunning) {
      intervalRef.current = setInterval(tickSensors, 3000);
    } else {
      clearInterval(intervalRef.current);
    }
    return () => clearInterval(intervalRef.current);
  }, [simRunning, tickSensors]);

  return (
    <SafeAreaProvider>
      <StatusBar style="light" backgroundColor={colors.card} />
      <NavigationContainer>
        <AppNavigator />
      </NavigationContainer>
    </SafeAreaProvider>
  );
}
