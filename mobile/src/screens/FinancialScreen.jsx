import React from "react";
import { View, StyleSheet } from "react-native";
import { TrendingUp, DollarSign, BarChart3 } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import StatGrid      from "../components/ui/StatGrid";
import BarChartCard  from "../components/charts/BarChartCard";
import PieChartCard  from "../components/charts/PieChartCard";
import { colors, spacing, chartColors } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";

export default function FinancialScreen() {
  const f = useFarmStore((s) => s.farm.financial);
  const margin = f.ytdRevenue > 0 ? ((f.ytdProfit / f.ytdRevenue) * 100).toFixed(1) : "0.0";

  const kpiStats = [
    { Icon: TrendingUp, label: "YTD Revenue",  value: `₹${f.ytdRevenue}L`, color: colors.primary },
    { Icon: DollarSign, label: "YTD Expenses", value: `₹${f.ytdExpense}L`, color: colors.danger },
    { Icon: DollarSign, label: "YTD Profit",   value: `₹${f.ytdProfit}L`,  color: colors.accent, sub: `${margin}% margin` },
    { Icon: TrendingUp, label: "Monthly Avg",  value: `₹${(f.ytdRevenue / 6).toFixed(1)}L`, color: colors.info },
  ];

  // Stacked bar: total revenue per month
  const monthlyTotals = f.monthlyRevenue.map((m) =>
    m.aqua + m.gh + m.vf + m.field + m.poultry + m.nursery + m.other
  );

  // Expense pie
  const expenseSegments = Object.entries(f.expenses).map(([key, val], i) => ({
    name:  key.charAt(0).toUpperCase() + key.slice(1),
    value: val,
    color: chartColors[i % chartColors.length],
  }));

  return (
    <ScreenWrapper title="Financials">
      <StatGrid stats={kpiStats} />

      <View style={styles.gap} />

      <BarChartCard
        Icon={BarChart3}
        title="Monthly Revenue (₹L)"
        color={colors.accent}
        labels={f.monthlyRevenue.map((m) => m.month)}
        data={monthlyTotals}
        yLabel="L"
        height={240}
      />

      <View style={styles.gap} />

      <PieChartCard
        Icon={DollarSign}
        title="Monthly Expense Breakdown"
        color={colors.danger}
        segments={expenseSegments}
        valuePrefix="₹"
        valueSuffix="L"
      />
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  gap: { height: spacing.lg },
});
