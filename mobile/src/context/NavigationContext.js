/**
 * Custom navigation context — replaces @react-navigation/drawer.
 * Tracks the active screen name and exposes navigate() / toggleDrawer().
 */
import React, { createContext, useContext, useState } from "react";

const NavigationContext = createContext(null);

export function NavigationProvider({ children }) {
  const [activeScreen, setActiveScreen] = useState("Dashboard");
  const [drawerOpen, setDrawerOpen]     = useState(false);

  const navigate     = (name) => { setActiveScreen(name); setDrawerOpen(false); };
  const toggleDrawer = ()     => setDrawerOpen((v) => !v);
  const closeDrawer  = ()     => setDrawerOpen(false);

  return (
    <NavigationContext.Provider value={{ activeScreen, drawerOpen, navigate, toggleDrawer, closeDrawer }}>
      {children}
    </NavigationContext.Provider>
  );
}

export function useNavigation() {
  return useContext(NavigationContext);
}
