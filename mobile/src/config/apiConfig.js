/**
 * API base URL — change API_BASE to your machine's LAN IP when
 * testing on a physical device (e.g. "http://192.168.1.10:8000").
 * For web/simulator localhost:8000 works fine.
 */
import { Platform } from "react-native";

export const API_BASE =
  Platform.OS === "web"
    ? "http://localhost:8002"   // Docker host port (docker-compose maps 8002→8000)
    : "http://localhost:8002";  // replace with LAN IP for physical device

// Anthropic Claude API key — required for the AI Analysis screen.
// Get yours at https://console.anthropic.com
export const CLAUDE_API_KEY = "";
