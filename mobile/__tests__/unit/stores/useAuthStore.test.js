/**
 * Unit tests for useAuthStore — authentication state management.
 */

import useAuthStore from "../../../src/store/useAuthStore";

// Mock api module
jest.mock("../../../src/services/api", () => ({
  api: {
    login: jest.fn(),
    me: jest.fn(),
  },
}));

import { api } from "../../../src/services/api";

// Reset store state before each test
beforeEach(() => {
  useAuthStore.setState({ token: null, user: null, authReady: false });
  jest.clearAllMocks();
});

// ── Initial state ───────────────────────────────────────────────────────────
describe("initial state", () => {
  it("has null token", () => {
    expect(useAuthStore.getState().token).toBeNull();
  });

  it("has null user", () => {
    expect(useAuthStore.getState().user).toBeNull();
  });

  it("has authReady false", () => {
    expect(useAuthStore.getState().authReady).toBe(false);
  });
});

// ── login ───────────────────────────────────────────────────────────────────
describe("login", () => {
  const mockTokenData = {
    access_token: "test-jwt-token-abc123",
    token_type: "bearer",
    username: "admin",
    role: "admin",
  };

  const mockUserData = {
    id: 1,
    username: "admin",
    email: "admin@smartfarm.in",
    full_name: "Farm Administrator",
    role_id: 1,
  };

  it("sets token after successful login", async () => {
    api.login.mockResolvedValue(mockTokenData);
    api.me.mockResolvedValue(mockUserData);

    await useAuthStore.getState().login("admin", "admin123");

    expect(useAuthStore.getState().token).toBe("test-jwt-token-abc123");
  });

  it("sets user after successful login", async () => {
    api.login.mockResolvedValue(mockTokenData);
    api.me.mockResolvedValue(mockUserData);

    await useAuthStore.getState().login("admin", "admin123");

    const { user } = useAuthStore.getState();
    expect(user).not.toBeNull();
    expect(user.username).toBe("admin");
  });

  it("normalizes role to uppercase", async () => {
    api.login.mockResolvedValue({ ...mockTokenData, role: "cashier" });
    api.me.mockResolvedValue(mockUserData);

    await useAuthStore.getState().login("cashier1", "cashier123");

    expect(useAuthStore.getState().user.role).toBe("CASHIER");
  });

  it("calls api.me with the received token", async () => {
    api.login.mockResolvedValue(mockTokenData);
    api.me.mockResolvedValue(mockUserData);

    await useAuthStore.getState().login("admin", "admin123");

    expect(api.me).toHaveBeenCalledWith("test-jwt-token-abc123");
  });

  it("throws on invalid credentials", async () => {
    api.login.mockRejectedValue(new Error("Invalid credentials"));

    await expect(
      useAuthStore.getState().login("admin", "wrong-password")
    ).rejects.toThrow("Invalid credentials");
  });

  it("does not set token on login failure", async () => {
    api.login.mockRejectedValue(new Error("Unauthorized"));

    try {
      await useAuthStore.getState().login("admin", "wrong");
    } catch {
      // expected
    }

    expect(useAuthStore.getState().token).toBeNull();
  });
});

// ── logout ──────────────────────────────────────────────────────────────────
describe("logout", () => {
  it("clears token on logout", async () => {
    useAuthStore.setState({ token: "some-token", user: { username: "admin" } });

    await useAuthStore.getState().logout();

    expect(useAuthStore.getState().token).toBeNull();
  });

  it("clears user on logout", async () => {
    useAuthStore.setState({ token: "some-token", user: { username: "admin" } });

    await useAuthStore.getState().logout();

    expect(useAuthStore.getState().user).toBeNull();
  });
});

// ── hasRole ─────────────────────────────────────────────────────────────────
describe("hasRole", () => {
  it("returns false when not logged in", () => {
    expect(useAuthStore.getState().hasRole("ADMIN")).toBe(false);
  });

  it("returns true when role matches", () => {
    useAuthStore.setState({ user: { role: "ADMIN" } });
    expect(useAuthStore.getState().hasRole("ADMIN")).toBe(true);
  });

  it("returns false when role does not match", () => {
    useAuthStore.setState({ user: { role: "CASHIER" } });
    expect(useAuthStore.getState().hasRole("ADMIN")).toBe(false);
  });

  it("matches any of multiple provided roles", () => {
    useAuthStore.setState({ user: { role: "CASHIER" } });
    expect(useAuthStore.getState().hasRole("ADMIN", "CASHIER", "MANAGER")).toBe(true);
  });

  it("returns false when none of the roles match", () => {
    useAuthStore.setState({ user: { role: "VIEWER" } });
    expect(useAuthStore.getState().hasRole("ADMIN", "MANAGER")).toBe(false);
  });

  it("is case-sensitive (roles should be uppercase)", () => {
    useAuthStore.setState({ user: { role: "ADMIN" } });
    // lowercase "admin" should not match uppercase "ADMIN"
    expect(useAuthStore.getState().hasRole("admin")).toBe(false);
    expect(useAuthStore.getState().hasRole("ADMIN")).toBe(true);
  });
});

// ── loadAuth ────────────────────────────────────────────────────────────────
describe("loadAuth", () => {
  it("sets authReady to true when storage is empty", async () => {
    const AsyncStorage = require("@react-native-async-storage/async-storage");
    AsyncStorage.getItem.mockResolvedValueOnce(null);

    await useAuthStore.getState().loadAuth();

    expect(useAuthStore.getState().authReady).toBe(true);
  });

  it("restores token and user from storage", async () => {
    const AsyncStorage = require("@react-native-async-storage/async-storage");
    const stored = JSON.stringify({
      token: "restored-token",
      user: { username: "admin", role: "ADMIN" },
    });
    AsyncStorage.getItem.mockResolvedValueOnce(stored);

    await useAuthStore.getState().loadAuth();

    expect(useAuthStore.getState().token).toBe("restored-token");
    expect(useAuthStore.getState().user.username).toBe("admin");
    expect(useAuthStore.getState().authReady).toBe(true);
  });

  it("normalizes old role_name field to role", async () => {
    const AsyncStorage = require("@react-native-async-storage/async-storage");
    const stored = JSON.stringify({
      token: "token",
      user: { username: "manager", role_name: "manager" },
    });
    AsyncStorage.getItem.mockResolvedValueOnce(stored);

    await useAuthStore.getState().loadAuth();

    expect(useAuthStore.getState().user.role).toBe("MANAGER");
  });

  it("sets authReady to true even if storage throws", async () => {
    const AsyncStorage = require("@react-native-async-storage/async-storage");
    AsyncStorage.getItem.mockRejectedValueOnce(new Error("Storage error"));

    await useAuthStore.getState().loadAuth();

    expect(useAuthStore.getState().authReady).toBe(true);
  });
});
