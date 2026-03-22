/**
 * Dynamic role-permission store.
 *
 * Admins can override screen access for predefined roles and create
 * custom roles. Changes are persisted to AsyncStorage.
 *
 * Usage:
 *   const { canAccess } = useRolesStore();
 *   canAccess("Aquaculture", "AQUA_TECH");  // true
 */
import { create } from "zustand";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { SCREEN_ACCESS, ROLE_META, canAccessScreen as defaultCanAccess } from "../config/permissions";

const STORAGE_KEY = "smartfarm-roles-v1";

const useRolesStore = create((set, get) => ({
  /**
   * Admin overrides for predefined roles.
   * { [ROLE_NAME]: string[] } — list of allowed screen names.
   * Empty means "use default from permissions.js".
   */
  roleOverrides: {},

  /**
   * Admin-created custom roles.
   * [{ name, label, description, color, screens: string[] }]
   */
  customRoles: [],

  /** True once storage has been loaded. */
  ready: false,

  // ── Hydrate ────────────────────────────────────────────────────────────────
  load: async () => {
    try {
      const raw = await AsyncStorage.getItem(STORAGE_KEY);
      if (raw) {
        const { roleOverrides, customRoles } = JSON.parse(raw);
        set({ roleOverrides: roleOverrides ?? {}, customRoles: customRoles ?? [], ready: true });
      } else {
        set({ ready: true });
      }
    } catch {
      set({ ready: true });
    }
  },

  // ── Persist helper ─────────────────────────────────────────────────────────
  _save: async () => {
    const { roleOverrides, customRoles } = get();
    await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify({ roleOverrides, customRoles }));
  },

  // ── Override predefined role screens ──────────────────────────────────────
  setRoleOverride: async (roleName, screens) => {
    const roleOverrides = { ...get().roleOverrides, [roleName]: screens };
    set({ roleOverrides });
    await get()._save();
  },

  resetRoleOverride: async (roleName) => {
    const overrides = { ...get().roleOverrides };
    delete overrides[roleName];
    set({ roleOverrides: overrides });
    await get()._save();
  },

  // ── Custom roles ───────────────────────────────────────────────────────────
  addCustomRole: async (role) => {
    const customRoles = [...get().customRoles, { ...role, name: role.name.toUpperCase() }];
    set({ customRoles });
    await get()._save();
  },

  updateCustomRole: async (name, updates) => {
    const customRoles = get().customRoles.map((r) =>
      r.name === name ? { ...r, ...updates } : r
    );
    set({ customRoles });
    await get()._save();
  },

  deleteCustomRole: async (name) => {
    const customRoles = get().customRoles.filter((r) => r.name !== name);
    set({ customRoles });
    await get()._save();
  },

  // ── Access check ──────────────────────────────────────────────────────────
  /**
   * Returns true if the given role can access the given screen.
   * Priority: custom roles → overrides → defaults from permissions.js.
   */
  canAccess: (screenName, role) => {
    const upper = (role || "").toUpperCase();
    const { roleOverrides, customRoles } = get();

    // Check custom roles first
    const custom = customRoles.find((r) => r.name === upper);
    if (custom) return custom.screens.includes(screenName);

    // Check admin override for predefined role
    if (roleOverrides[upper]) return roleOverrides[upper].includes(screenName);

    // Fall back to static permissions.js
    return defaultCanAccess(screenName, upper);
  },

  /**
   * Returns the effective screen list for a role (merged with overrides).
   */
  screensForRole: (roleName) => {
    const upper = (roleName || "").toUpperCase();
    const { roleOverrides, customRoles } = get();

    const custom = customRoles.find((r) => r.name === upper);
    if (custom) return custom.screens;

    if (roleOverrides[upper]) return roleOverrides[upper];

    // Derive from static SCREEN_ACCESS
    const { SCREENS_LIST } = get();
    return SCREENS_LIST.filter((s) => defaultCanAccess(s, upper));
  },

  /**
   * All screen names available in the app — set once on init from navigation config.
   */
  SCREENS_LIST: [],
  initScreens: (names) => set({ SCREENS_LIST: names }),
}));

export default useRolesStore;
