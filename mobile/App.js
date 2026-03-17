/**
 * SmartFarm OS — App entry point.
 *
 * Auth flow:
 *   → not logged in  → LoginScreen
 *   → logged in      → main app (drawer + screens filtered by role)
 *
 * Navigation strategy:
 *   mobile  (<768px)  → drawer hidden, opened via header hamburger
 *   tablet / desktop  → drawer permanently visible on the left
 */
import { useEffect, useRef, Component } from "react";
import { View, Text, StyleSheet, TouchableWithoutFeedback, ActivityIndicator } from "react-native";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { StatusBar }        from "expo-status-bar";

import { NavigationProvider, useNavigation } from "./src/context/NavigationContext";
import { useResponsive }   from "./src/hooks/useResponsive";
import useFarmStore        from "./src/store/useFarmStore";
import useAuthStore        from "./src/store/useAuthStore";
import DrawerContent       from "./src/components/layout/DrawerContent";
import LoginScreen         from "./src/screens/LoginScreen";
import { colors }          from "./src/config/theme";
import { canAccessScreen } from "./src/config/permissions";

// ─── Farm Screens ────────────────────────────────────────────────
import DashboardScreen    from "./src/screens/DashboardScreen";
import AquacultureScreen  from "./src/screens/AquacultureScreen";
import GreenhouseScreen   from "./src/screens/GreenhouseScreen";
import VerticalFarmScreen from "./src/screens/VerticalFarmScreen";
import PoultryScreen      from "./src/screens/PoultryScreen";
import WaterScreen        from "./src/screens/WaterScreen";
import EnergyScreen       from "./src/screens/EnergyScreen";
import AutomationScreen   from "./src/screens/AutomationScreen";
import NurseryScreen      from "./src/screens/NurseryScreen";
// ─── Stock & Supply Chain ────────────────────────────────────────
import StockProducedScreen from "./src/screens/StockProducedScreen";
import StockSalesScreen    from "./src/screens/StockSalesScreen";
import PackingScreen       from "./src/screens/PackingScreen";
import ScannerScreen       from "./src/screens/ScannerScreen";
// ─── Store & Retail ──────────────────────────────────────────────
import StoreScreen         from "./src/screens/StoreScreen";
import POSScreen           from "./src/screens/POSScreen";
import LogisticsScreen     from "./src/screens/LogisticsScreen";
// ─── Finance & Markets ───────────────────────────────────────────
import MarketScreen        from "./src/screens/MarketScreen";
import FinancialScreen     from "./src/screens/FinancialScreen";
import ReportsScreen       from "./src/screens/ReportsScreen";
// ─── Admin & AI ──────────────────────────────────────────────────
import AIScreen                from "./src/screens/AIScreen";
import ServiceRequestsScreen   from "./src/screens/ServiceRequestsScreen";
import ActivityLogScreen       from "./src/screens/ActivityLogScreen";
import UsersScreen             from "./src/screens/UsersScreen";
import SettingsScreen          from "./src/screens/SettingsScreen";
// ─── New Modules ─────────────────────────────────────────────────
import FeedProductionScreen   from "./src/screens/FeedProductionScreen";
import DroneScreen            from "./src/screens/DroneScreen";
import QAScreen               from "./src/screens/QAScreen";
import ComplianceScreen       from "./src/screens/ComplianceScreen";
import NurseryBackendScreen   from "./src/screens/NurseryBackendScreen";

const SCREEN_MAP = {
  // Farm ops
  Dashboard:       DashboardScreen,
  Aquaculture:     AquacultureScreen,
  Greenhouse:      GreenhouseScreen,
  VerticalFarm:    VerticalFarmScreen,
  Poultry:         PoultryScreen,
  Water:           WaterScreen,
  Energy:          EnergyScreen,
  Automation:      AutomationScreen,
  Nursery:         NurseryScreen,
  // Stock & supply chain
  StockProduced:   StockProducedScreen,
  StockSales:      StockSalesScreen,
  Packing:         PackingScreen,
  Scanner:         ScannerScreen,
  // Store & retail
  Store:           StoreScreen,
  POS:             POSScreen,
  Logistics:       LogisticsScreen,
  // Finance & markets
  Market:          MarketScreen,
  Financial:       FinancialScreen,
  Reports:         ReportsScreen,
  // Admin & AI
  AI:              AIScreen,
  ServiceRequests: ServiceRequestsScreen,
  ActivityLog:     ActivityLogScreen,
  Users:           UsersScreen,
  Settings:        SettingsScreen,
  // New modules
  FeedProduction:  FeedProductionScreen,
  Drones:          DroneScreen,
  QA:              QAScreen,
  Compliance:      ComplianceScreen,
  NurseryBE:       NurseryBackendScreen,
};

// ─── Error boundary ───────────────────────────────────────────────
class ErrorBoundary extends Component {
  state = { error: null };
  static getDerivedStateFromError(error) { return { error }; }
  render() {
    if (this.state.error) {
      return (
        <View style={errStyles.container}>
          <Text style={errStyles.title}>Render Error</Text>
          <Text style={errStyles.msg}>{this.state.error.message}</Text>
          <Text style={errStyles.stack}>{this.state.error.stack?.slice(0, 600)}</Text>
        </View>
      );
    }
    return this.props.children;
  }
}

const errStyles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#1a0000", padding: 20, paddingTop: 60 },
  title:     { color: "#ff6b6b", fontSize: 18, fontWeight: "700", marginBottom: 12 },
  msg:       { color: "#ffcccc", fontSize: 14, marginBottom: 16 },
  stack:     { color: "#886666", fontSize: 10, fontFamily: "monospace" },
});

// ─── Unauthorised placeholder ─────────────────────────────────────
function UnauthorisedScreen() {
  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.bg }}>
      <Text style={{ color: colors.textMuted, fontSize: 16 }}>🔒 Access denied</Text>
      <Text style={{ color: colors.textMuted, fontSize: 13, marginTop: 8 }}>
        Your role does not have permission to view this screen.
      </Text>
    </View>
  );
}

// ─── Main app layout ─────────────────────────────────────────────
function AppLayout() {
  const { activeScreen, drawerOpen, closeDrawer } = useNavigation();
  const { showPermanentDrawer, drawerWidth }       = useResponsive();
  const userRole = useAuthStore((s) => (s.user?.role ?? "VIEWER").toUpperCase());

  const allowed      = canAccessScreen(activeScreen, userRole);
  const ActiveScreen = allowed ? (SCREEN_MAP[activeScreen] ?? DashboardScreen) : UnauthorisedScreen;

  return (
    <View style={styles.root}>
      {showPermanentDrawer && (
        <View style={[styles.drawer, { width: drawerWidth }]}>
          <DrawerContent />
        </View>
      )}

      {!showPermanentDrawer && drawerOpen && (
        <>
          <TouchableWithoutFeedback onPress={closeDrawer}>
            <View style={styles.backdrop} />
          </TouchableWithoutFeedback>
          <View style={[styles.drawer, styles.overlayDrawer, { width: drawerWidth }]}>
            <DrawerContent />
          </View>
        </>
      )}

      <View style={styles.content}>
        <ErrorBoundary>
          <ActiveScreen />
        </ErrorBoundary>
      </View>
    </View>
  );
}

// ─── Root ─────────────────────────────────────────────────────────
export default function App() {
  const loadFromStorage = useFarmStore((s) => s.loadFromStorage);
  const simRunning      = useFarmStore((s) => s.simRunning);
  const tickSensors     = useFarmStore((s) => s.tickSensors);
  const intervalRef     = useRef(null);

  const loadAuth = useAuthStore((s) => s.loadAuth);
  const token    = useAuthStore((s) => s.token);
  const authReady= useAuthStore((s) => s.authReady);

  // Hydrate auth + farm data from storage
  useEffect(() => { loadAuth(); loadFromStorage(); }, []);

  // Sensor simulation
  useEffect(() => {
    if (simRunning) {
      intervalRef.current = setInterval(tickSensors, 3000);
    } else {
      clearInterval(intervalRef.current);
    }
    return () => clearInterval(intervalRef.current);
  }, [simRunning, tickSensors]);

  // Show a splash while checking stored credentials
  if (!authReady) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <ErrorBoundary>
      <SafeAreaProvider>
        <StatusBar style="light" />
        {token ? (
          <NavigationProvider>
            <AppLayout />
          </NavigationProvider>
        ) : (
          <LoginScreen />
        )}
      </SafeAreaProvider>
    </ErrorBoundary>
  );
}

const styles = StyleSheet.create({
  root:          { flex: 1, flexDirection: "row", backgroundColor: colors.bg },
  drawer:        { backgroundColor: colors.card, borderRightWidth: 1, borderRightColor: colors.border },
  overlayDrawer: { position: "absolute", top: 0, left: 0, bottom: 0, zIndex: 100, elevation: 10 },
  backdrop:      { position: "absolute", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: "rgba(0,0,0,0.5)", zIndex: 99 },
  content:       { flex: 1 },
});
