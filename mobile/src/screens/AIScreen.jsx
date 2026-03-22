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
import useAuthStore  from "../store/useAuthStore";
import { styles } from "./AIScreen.styles";
import { commonStyles as cs } from "../styles/common";
import { api } from "../services/api";

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

// ─── Component ────────────────────────────────────────────────────
export default function AIScreen() {
  const aiConversations   = useFarmStore((s) => s.farm.aiConversations);
  const saveConversations = useFarmStore((s) => s.saveAIConversations);
  const token             = useAuthStore((s) => s.token);

  const [messages, setMessages]   = useState(aiConversations ?? []);
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
      // Build conversation history (last 6 turns, excluding the new message)
      const history = messages
        .filter((m) => m.role === "user" || m.role === "assistant")
        .slice(-6)
        .map((m) => ({ role: m.role, content: m.text }));

      const data = await api.ai.analyze(trimmed, history, token);
      const aiText = data.response ?? "Analysis complete. No specific issues detected at this time.";

      const aiMsg     = { role: "assistant", text: aiText, time: new Date().toLocaleTimeString() };
      const withReply = [...updated, aiMsg];
      setMessages(withReply);
      saveConversations(withReply);
    } catch (err) {
      const errMsg = {
        role: "assistant",
        text: `⚠️ Analysis temporarily unavailable.\n\nError: ${err.message}\n\nEnsure the backend server is running and the AI service is configured.`,
        time: new Date().toLocaleTimeString(),
      };
      setMessages([...updated, errMsg]);
    }

    setIsLoading(false);
  }, [messages, isLoading, token, saveConversations]);

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
