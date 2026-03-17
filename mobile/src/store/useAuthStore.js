/**
 * Auth state — JWT token + logged-in user persisted via AsyncStorage.
 */
import { create } from "zustand";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { api, setUnauthorizedHandler } from "../services/api";

const AUTH_KEY = "smartfarm-auth-v1";

const useAuthStore = create((set, get) => ({
  token:     null,
  user:      null,
  authReady: false,   // true once storage has been checked

  // ─── Hydrate from storage on app launch ───────────────────────
  loadAuth: async () => {
    // Register global 401 handler so any API call auto-logs out
    setUnauthorizedHandler(() => {
      AsyncStorage.removeItem(AUTH_KEY);
      set({ token: null, user: null });
    });

    try {
      const raw = await AsyncStorage.getItem(AUTH_KEY);
      if (raw) {
        const { token, user } = JSON.parse(raw);
        // Normalise: ensure role is uppercase; older sessions may use role_name
        if (!user.role && user.role_name) user.role = user.role_name;
        if (user.role) user.role = user.role.toUpperCase();

        // Validate token against the server — clears stale/pre-security-update tokens
        try {
          await api.me(token);
          set({ token, user, authReady: true });
        } catch {
          await AsyncStorage.removeItem(AUTH_KEY);
          set({ authReady: true });
        }
      } else {
        set({ authReady: true });
      }
    } catch {
      set({ authReady: true });
    }
  },

  // ─── Login ────────────────────────────────────────────────────
  login: async (username, password) => {
    const tokenData = await api.login(username, password);
    const user      = await api.me(tokenData.access_token);
    // /me returns UserOut which has role_id but no role name.
    // Attach the role name from the JWT login response.
    user.role = (tokenData.role || "").toUpperCase();
    const payload = { token: tokenData.access_token, user };
    await AsyncStorage.setItem(AUTH_KEY, JSON.stringify(payload));
    set(payload);
  },

  // ─── Logout ───────────────────────────────────────────────────
  logout: async () => {
    await AsyncStorage.removeItem(AUTH_KEY);
    set({ token: null, user: null });
  },

  // ─── Role helpers ─────────────────────────────────────────────
  /** Returns true if the logged-in user has one of the given roles */
  hasRole: (...roles) => {
    const { user } = get();
    return !!user && roles.includes(user.role);
  },
}));

export default useAuthStore;
