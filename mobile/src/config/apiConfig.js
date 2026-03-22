/**
 * API base URL — injected at Docker build time via EXPO_PUBLIC_API_URL.
 * Falls back to localhost:8002 for local dev outside Docker.
 * For physical device testing, set EXPO_PUBLIC_API_URL to your LAN IP.
 */
export const API_BASE =
  process.env.EXPO_PUBLIC_API_URL || "http://localhost:8002";
