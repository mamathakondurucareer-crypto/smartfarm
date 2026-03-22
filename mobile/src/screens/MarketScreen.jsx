/**
 * Market Screen — live market prices across 5 cities.
 * Custom price-board table with color-coded highs/lows,
 * summary stat cards, and bar charts per product.
 */
import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, ActivityIndicator, TouchableOpacity, StyleSheet,
} from "react-native";
import {
  Truck, MapPin, BarChart3, RefreshCw,
  TrendingUp, TrendingDown, Minus,
} from "lucide-react-native";
import ScreenWrapper  from "../components/layout/ScreenWrapper";
import Card           from "../components/ui/Card";
import SectionHeader  from "../components/ui/SectionHeader";
import BarChartCard   from "../components/charts/BarChartCard";
import { colors, spacing, radius, fontSize } from "../config/theme";
import { api }        from "../services/api";
import useAuthStore   from "../store/useAuthStore";
import { commonStyles as cs } from "../styles/common";

// ── Config ────────────────────────────────────────────────────────
const CITIES = [
  { key: "hyderabad",  name: "Hyderabad",  short: "HYD", dist: "400 km" },
  { key: "chennai",    name: "Chennai",    short: "MAA", dist: "180 km" },
  { key: "vijayawada", name: "Vijayawada", short: "VJA", dist: "280 km" },
  { key: "kadapa",     name: "Kadapa",     short: "CDP", dist: "200 km" },
  { key: "nellore",    name: "Nellore",    short: "NLR", dist: "15 km"  },
];

const PRODUCTS = [
  { key: "murrel", label: "Murrel", color: colors.fish    },
  { key: "rohu",   label: "Rohu",   color: colors.primary },
  { key: "tomato", label: "Tomato", color: colors.warn    },
  { key: "chilli", label: "Chilli", color: colors.danger  },
];

const EMPTY_CITY = {
  lastPrice: { murrel: 0, rohu: 0, tomato: 0, chilli: 0 },
  trend: "stable",
};

// ── Helpers ───────────────────────────────────────────────────────
function transformPrices(records) {
  const map = {};
  for (const r of records) {
    const city = r.market_city?.toLowerCase();
    if (!city) continue;
    if (!map[city]) {
      map[city] = { lastPrice: { murrel: 0, rohu: 0, tomato: 0, chilli: 0 }, trend: r.trend ?? "stable" };
    }
    const product = r.product?.toLowerCase();
    if (product && map[city].lastPrice[product] !== undefined) {
      map[city].lastPrice[product] = Math.round(r.avg_price ?? 0);
      map[city].trend = r.trend ?? map[city].trend;
    }
  }
  return map;
}

function TrendIcon({ trend, size = 13 }) {
  if (trend === "up")   return <TrendingUp   size={size} color={colors.primary} />;
  if (trend === "down") return <TrendingDown  size={size} color={colors.danger}  />;
  return                       <Minus         size={size} color={colors.accent}  />;
}

function TrendLabel({ trend }) {
  const cfg = {
    up:     { label: "Rising",  color: colors.primary },
    down:   { label: "Falling", color: colors.danger  },
    stable: { label: "Stable",  color: colors.accent  },
  }[trend] ?? { label: "Stable", color: colors.accent };
  return (
    <View style={[st.trendPill, { borderColor: cfg.color + "50", backgroundColor: cfg.color + "15" }]}>
      <TrendIcon trend={trend} size={10} />
      <Text style={[st.trendText, { color: cfg.color }]}>{cfg.label}</Text>
    </View>
  );
}

/** Best city (highest avg_price) for a given product */
function bestCity(markets, product) {
  let best = null, bestPrice = -1;
  for (const c of CITIES) {
    const p = (markets[c.key] ?? EMPTY_CITY).lastPrice[product];
    if (p > bestPrice) { bestPrice = p; best = c; }
  }
  return { city: best, price: bestPrice };
}

// ── Sub-components ────────────────────────────────────────────────
function SummaryCards({ markets }) {
  return (
    <View style={st.summaryRow}>
      {PRODUCTS.map(({ key, label, color }) => {
        const { city, price } = bestCity(markets, key);
        return (
          <View key={key} style={[st.summaryCard, { borderTopColor: color }]}>
            <Text style={[st.summaryProduct, { color }]}>{label}</Text>
            <Text style={st.summaryPrice}>
              {price > 0 ? `₹${price}` : "—"}
            </Text>
            <Text style={st.summaryCity} numberOfLines={1}>
              {price > 0 ? (city?.short ?? "—") : "No data"}
            </Text>
          </View>
        );
      })}
    </View>
  );
}

/** Color-coded price cell: highest = green, lowest = red */
function PriceCell({ value, isHigh, isLow }) {
  const color = isHigh ? colors.primary : isLow ? colors.danger : colors.text;
  return (
    <Text style={[st.priceCell, { color }]}>
      {value > 0 ? `₹${value}` : <Text style={{ color: colors.textMuted }}>—</Text>}
    </Text>
  );
}

function PriceTable({ markets }) {
  // Pre-compute highs and lows per product
  const extremes = {};
  for (const p of PRODUCTS) {
    const vals = CITIES.map((c) => (markets[c.key] ?? EMPTY_CITY).lastPrice[p.key]).filter(Boolean);
    extremes[p.key] = { high: Math.max(...vals, 0), low: Math.min(...vals, Infinity) };
  }

  return (
    <View style={st.table}>
      {/* Header */}
      <View style={[st.row, st.headerRow]}>
        <Text style={[st.cell, st.colCity, st.headText]}>City</Text>
        <Text style={[st.cell, st.colDist, st.headText]}>Dist</Text>
        {PRODUCTS.map((p) => (
          <Text key={p.key} style={[st.cell, st.colPrice, st.headText, { color: p.color }]}>
            {p.label}
          </Text>
        ))}
        <Text style={[st.cell, st.colTrend, st.headText]}>Trend</Text>
      </View>

      {/* Rows */}
      {CITIES.map((c, idx) => {
        const data = markets[c.key] ?? EMPTY_CITY;
        const trend = ["up", "down", "stable"].includes(data.trend) ? data.trend : "stable";
        return (
          <View key={c.key} style={[st.row, st.dataRow, idx % 2 === 1 && st.altRow]}>
            <View style={[st.cell, st.colCity]}>
              <Text style={st.cityName}>{c.name}</Text>
              <Text style={st.cityShort}>{c.short}</Text>
            </View>
            <Text style={[st.cell, st.colDist, st.distText]}>{c.dist}</Text>
            {PRODUCTS.map((p) => {
              const v = data.lastPrice[p.key];
              const { high, low } = extremes[p.key];
              return (
                <View key={p.key} style={[st.cell, st.colPrice, { alignItems: "center" }]}>
                  <PriceCell
                    value={v}
                    isHigh={v > 0 && v === high}
                    isLow={v > 0 && v === low}
                  />
                </View>
              );
            })}
            <View style={[st.cell, st.colTrend, { alignItems: "center" }]}>
              <TrendLabel trend={trend} />
            </View>
          </View>
        );
      })}
    </View>
  );
}

// ── Main Screen ───────────────────────────────────────────────────
export default function MarketScreen() {
  const token = useAuthStore((s) => s.token);
  const [markets, setMarkets]   = useState({});
  const [loading, setLoading]   = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError]       = useState("");

  const fetchPrices = useCallback(async (isRefresh = false) => {
    isRefresh ? setRefreshing(true) : setLoading(true);
    setError("");
    try {
      const records = await api.market.latestPrices(token);
      setMarkets(transformPrices(records));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [token]);

  useEffect(() => { fetchPrices(); }, [fetchPrices]);

  const hasData = CITIES.some((c) => markets[c.key]?.lastPrice?.murrel > 0);

  return (
    <ScreenWrapper title="Markets">
      {/* Error */}
      {!!error && (
        <View style={cs.errorBox}>
          <Text style={cs.errorText}>{error}</Text>
        </View>
      )}

      {loading ? (
        <ActivityIndicator size="large" color={colors.primary} style={{ marginTop: 40 }} />
      ) : (
        <>
          {/* Best-price summary cards */}
          {hasData && <SummaryCards markets={markets} />}

          {/* Price board */}
          <Card>
            <View style={st.cardHeaderRow}>
              <SectionHeader Icon={MapPin} title="Five-City Market Prices (₹/kg)" color={colors.market} />
              <TouchableOpacity
                onPress={() => fetchPrices(true)}
                style={[st.refreshBtn, refreshing && { opacity: 0.5 }]}
                disabled={refreshing}
                activeOpacity={0.7}
              >
                <RefreshCw size={14} color={colors.textDim} />
              </TouchableOpacity>
            </View>

            {/* Legend */}
            <View style={st.legend}>
              <View style={st.legendItem}>
                <View style={[st.legendDot, { backgroundColor: colors.primary }]} />
                <Text style={st.legendText}>Highest</Text>
              </View>
              <View style={st.legendItem}>
                <View style={[st.legendDot, { backgroundColor: colors.danger }]} />
                <Text style={st.legendText}>Lowest</Text>
              </View>
            </View>

            <PriceTable markets={markets} />
          </Card>

          <View style={cs.gap} />

          {/* Charts */}
          <BarChartCard
            Icon={BarChart3}
            title="Murrel Price Comparison (₹/kg)"
            color={colors.fish}
            labels={CITIES.map((c) => c.short)}
            data={CITIES.map((c) => (markets[c.key] ?? EMPTY_CITY).lastPrice.murrel)}
            yLabel="₹"
            height={200}
          />

          <View style={cs.gap} />

          <BarChartCard
            Icon={Truck}
            title="Rohu Price Comparison (₹/kg)"
            color={colors.primary}
            labels={CITIES.map((c) => c.short)}
            data={CITIES.map((c) => (markets[c.key] ?? EMPTY_CITY).lastPrice.rohu)}
            yLabel="₹"
            height={200}
          />
        </>
      )}
    </ScreenWrapper>
  );
}

// ── Styles ────────────────────────────────────────────────────────
const st = StyleSheet.create({
  // Summary cards
  summaryRow: {
    flexDirection: "row",
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  summaryCard: {
    flex: 1,
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    borderTopWidth: 3,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.sm,
    alignItems: "center",
    gap: 2,
  },
  summaryProduct: {
    fontSize: fontSize.xs,
    fontWeight: "700",
    letterSpacing: 0.5,
    textTransform: "uppercase",
  },
  summaryPrice: {
    fontSize: fontSize.xl,
    fontWeight: "700",
    color: colors.text,
  },
  summaryCity: {
    fontSize: fontSize.xs,
    color: colors.textMuted,
  },

  // Card header
  cardHeaderRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  refreshBtn: {
    padding: spacing.xs,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
  },

  // Legend
  legend: {
    flexDirection: "row",
    gap: spacing.md,
    marginBottom: spacing.sm,
    paddingHorizontal: spacing.xs,
  },
  legendItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  legendDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  legendText: {
    fontSize: fontSize.xs,
    color: colors.textMuted,
  },

  // Table
  table: {
    borderRadius: radius.md,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: colors.border + "60",
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
  },
  headerRow: {
    backgroundColor: colors.bg,
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  dataRow: {
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: colors.border + "30",
  },
  altRow: {
    backgroundColor: colors.bg + "80",
  },
  headText: {
    fontSize: fontSize.xs,
    fontWeight: "700",
    color: colors.textDim,
    textAlign: "center",
    letterSpacing: 0.3,
  },

  // Columns
  cell:     { paddingHorizontal: spacing.sm },
  colCity:  { width: 100 },
  colDist:  { width: 60, alignItems: "center" },
  colPrice: { width: 72 },
  colTrend: { width: 80 },

  cityName:  { fontSize: fontSize.md, fontWeight: "700", color: colors.market },
  cityShort: { fontSize: fontSize.xs, color: colors.textMuted, marginTop: 1 },
  distText:  { fontSize: fontSize.sm, color: colors.textDim, textAlign: "center" },
  priceCell: { fontSize: fontSize.base, fontWeight: "600", textAlign: "center" },

  // Trend pill
  trendPill: {
    flexDirection: "row",
    alignItems: "center",
    gap: 3,
    paddingHorizontal: 7,
    paddingVertical: 3,
    borderRadius: radius.sm,
    borderWidth: 1,
  },
  trendText: {
    fontSize: fontSize.xs,
    fontWeight: "600",
  },
});
