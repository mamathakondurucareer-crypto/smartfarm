/**
 * AI Analysis screen — chat interface powered by the Anthropic Claude API.
 * Sends live farm context with every request so the AI can give
 * data-driven, actionable recommendations.
 */
import React, { useState, useRef, useEffect, useCallback } from "react";
import {
  View, Text, TextInput, TouchableOpacity,
  ScrollView, KeyboardAvoidingView, Platform,
  ActivityIndicator,
} from "react-native";
import { Brain, Send } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Badge         from "../components/ui/Badge";
import { colors } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";
import { styles } from "./AIScreen.styles";
import { commonStyles as cs } from "../styles/common";
import { CLAUDE_API_KEY } from "../config/apiConfig";

// ─── Quick analysis prompts ───────────────────────────────────────
const QUICK_PROMPTS = [
  {
    id: "health",
    label: "🐟 Farm Health Check",
    prompt: "Perform a comprehensive health analysis of the entire farm. Check all pond water quality (DO, pH, ammonia, temperature), greenhouse crop health scores and disease risk, poultry lay rates and ammonia levels, vertical farm nutrient levels. Flag any parameters outside optimal ranges with specific corrective actions. Rate overall farm health 1–10.",
  },
  {
    id: "financial",
    label: "💰 Financial Review",
    prompt: "Analyze the farm's financial performance. Calculate revenue per acre, EBITDA margin, and compare against targets. Identify highest and lowest performing revenue streams. Project next quarter revenue based on current trends. Suggest 3 specific actions to improve profitability.",
  },
  {
    id: "market",
    label: "📊 Market Strategy",
    prompt: "Analyze current market prices across all 5 cities (Hyderabad, Chennai, Vijayawada, Kadapa, Nellore). Determine optimal product allocation to maximize revenue. Identify arbitrage opportunities where price differentials justify logistics costs.",
  },
  {
    id: "risk",
    label: "⚠️ Risk Assessment",
    prompt: "Conduct a comprehensive risk assessment covering: (1) disease risk from water quality trends, (2) climate risk from weather patterns, (3) market price volatility, (4) equipment failure from automation status, (5) water security from reservoir levels. Assign risk scores and recommend mitigation actions.",
  },
  {
    id: "yield",
    label: "🌱 Yield Optimization",
    prompt: "Analyze current crop yields vs targets for all greenhouse, vertical farm, and aquaculture systems. Identify underperforming areas. Recommend specific interventions and calculate revenue impact of achieving 100% yield targets.",
  },
  {
    id: "automation",
    label: "🤖 Automation Audit",
    prompt: "Audit all automation systems: irrigation efficiency, fish feeding optimization, greenhouse climate control, egg collection rates, and drone utilization. Calculate labour hours saved. Recommend upgrades or new automation workflows.",
  },
];

// ─── Build farm context string for the AI ─────────────────────────
function buildFarmContext(farm) {
  const s = farm.sensors;
  return `LIVE FARM DATA SNAPSHOT:
SENSORS: WaterTemp=${s.waterTemp}°C, DO=${s.dissolvedO2}mg/L, pH=${s.ph}, Ammonia=${s.ammonia}mg/L, SoilMoisture=${s.soilMoisture}%, GH_Temp=${s.ghTemp}°C, GH_Humidity=${s.ghHumidity}%, GH_CO2=${s.ghCO2}ppm, Ambient=${s.ambientTemp}°C, SolarGen=${s.solarGeneration}kW, Reservoir=${s.reservoirLevel}%
PONDS: ${farm.ponds.map((p) => `${p.id}(${p.species}): Stock=${p.stock}, AvgWt=${p.avgWeight}kg, DO=${p.do}, FCR=${p.fcr}, Mort=${p.mortality}%`).join("; ")}
GREENHOUSE: ${farm.greenhouse.map((g) => `${g.crop}: ${g.stage}, Health=${g.health}%, Yield=${g.yieldKg}/${g.targetKg}kg, Day${g.daysPlanted}`).join("; ")}
VERTICAL_FARM: ${farm.verticalFarm.map((v) => `${v.crop}: Day${v.cycleDay}, Health=${v.health}%, Batch=${v.batchKg}kg`).join("; ")}
POULTRY: Hens=${farm.poultry.hens}, LayRate=${farm.poultry.layRate}%, EggsToday=${farm.poultry.eggsToday}
DUCKS: ${farm.ducks.count} active, Eggs=${farm.ducks.eggsToday}
BEES: ${farm.bees.hives} hives, Honey=${farm.bees.honeyStored}kg
FINANCIAL: YTD_Revenue=₹${farm.financial.ytdRevenue}L, YTD_Expense=₹${farm.financial.ytdExpense}L, YTD_Profit=₹${farm.financial.ytdProfit}L
MARKETS: Hyderabad(Murrel₹${farm.markets.hyderabad.lastPrice.murrel}), Chennai(Murrel₹${farm.markets.chennai.lastPrice.murrel}), Vijayawada, Kadapa, Nellore
ALERTS: ${farm.alerts.slice(0, 5).map((a) => a.msg).join("; ")}`;
}

// ─── Component ────────────────────────────────────────────────────
export default function AIScreen() {
  const farm            = useFarmStore((s) => s.farm);
  const saveConversations = useFarmStore((s) => s.saveAIConversations);

  const [messages, setMessages]   = useState(farm.aiConversations ?? []);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef                 = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messages.length > 0) {
      scrollRef.current?.scrollToEnd({ animated: true });
    }
  }, [messages]);

  const sendMessage = useCallback(async (text) => {
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;

    const userMsg = { role: "user", text: trimmed, time: new Date().toLocaleTimeString() };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInputText("");
    setIsLoading(true);

    try {
      if (!CLAUDE_API_KEY) throw new Error("Claude API key not configured. Set CLAUDE_API_KEY in src/config/apiConfig.js");

      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method:  "POST",
        headers: {
          "Content-Type":    "application/json",
          "x-api-key":       CLAUDE_API_KEY,
          "anthropic-version": "2023-06-01",
        },
        body: JSON.stringify({
          model:      "claude-sonnet-4-6",
          max_tokens: 1000,
          system: `You are the AI Farm Analyst for an Integrated Smart Regenerative Farm in Nellore, Andhra Pradesh, India. You have access to live sensor data. Provide expert agricultural analysis with specific, actionable recommendations. Use ₹ for currency. Reference specific sensor readings and thresholds.

${buildFarmContext(farm)}`,
          messages: updated
            .filter((m) => m.role === "user" || m.role === "assistant")
            .slice(-6)
            .map((m) => ({ role: m.role === "user" ? "user" : "assistant", content: m.text })),
        }),
      });

      const data   = await response.json();
      if (data.error) throw new Error(data.error.message || `API error (${response.status})`);
      const aiText = data.content?.filter((b) => b.type === "text").map((b) => b.text).join("\n")
        ?? "Analysis complete. No specific issues detected at this time.";

      const aiMsg     = { role: "assistant", text: aiText, time: new Date().toLocaleTimeString() };
      const withReply = [...updated, aiMsg];
      setMessages(withReply);
      saveConversations(withReply);
    } catch (err) {
      const errMsg = {
        role: "assistant",
        text: `⚠️ Analysis temporarily unavailable.\n\nError: ${err.message}\n\nEnsure your device has internet access and the Claude API key is configured.`,
        time: new Date().toLocaleTimeString(),
      };
      setMessages([...updated, errMsg]);
    }

    setIsLoading(false);
  }, [messages, isLoading, farm, saveConversations]);

  return (
    <ScreenWrapper title="AI Analysis">
      {/* Quick prompt chips */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.chipsScroll} contentContainerStyle={styles.chips}>
        {QUICK_PROMPTS.map((qp) => (
          <TouchableOpacity
            key={qp.id}
            onPress={() => sendMessage(qp.prompt)}
            disabled={isLoading}
            style={[styles.chip, isLoading && styles.chipDisabled]}
            activeOpacity={0.7}
          >
            <Text style={styles.chipText}>{qp.label}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Chat area */}
      <KeyboardAvoidingView
        style={styles.chatContainer}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        keyboardVerticalOffset={100}
      >
        {/* Message list */}
        <ScrollView
          ref={scrollRef}
          style={styles.messageList}
          contentContainerStyle={styles.messageListContent}
          showsVerticalScrollIndicator={false}
        >
          {messages.length === 0 && (
            <View style={cs.emptyState}>
              <Brain size={40} color={colors.textMuted} />
              <Text style={cs.emptyTitle}>AI Farm Analysis Ready</Text>
              <Text style={styles.emptyBody}>
                Ask any question about your farm or tap a quick analysis above.
                The AI has access to all live sensor data, financials, and market prices.
              </Text>
            </View>
          )}

          {messages.map((msg, i) => (
            <View key={i} style={[styles.bubble, msg.role === "user" ? styles.userBubble : styles.aiBubble]}>
              <Text style={styles.bubbleMeta}>
                {msg.role === "user" ? "You" : "🤖 AI Analyst"} • {msg.time}
              </Text>
              <Text style={styles.bubbleText}>{msg.text}</Text>
            </View>
          ))}

          {isLoading && (
            <View style={[styles.bubble, styles.aiBubble]}>
              <View style={styles.loadingRow}>
                <ActivityIndicator size="small" color={colors.ai} />
                <Text style={styles.loadingText}>Analyzing farm data…</Text>
              </View>
            </View>
          )}
        </ScrollView>

        {/* Input row */}
        <View style={styles.inputRow}>
          <TextInput
            style={cs.input}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Ask about water quality, crops, financials…"
            placeholderTextColor={colors.textMuted}
            multiline
            returnKeyType="send"
            onSubmitEditing={() => sendMessage(inputText)}
            editable={!isLoading}
          />
          <TouchableOpacity
            onPress={() => sendMessage(inputText)}
            disabled={isLoading || !inputText.trim()}
            style={[styles.sendBtn, (isLoading || !inputText.trim()) && styles.sendBtnDisabled]}
            activeOpacity={0.8}
          >
            <Send size={16} color={colors.white} />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </ScreenWrapper>
  );
}
