import React from "react";
import { View, Text, StyleSheet, useWindowDimensions } from "react-native";
import { PieChart } from "react-native-chart-kit";
import { colors, fontSize, spacing } from "../../config/theme";
import Card from "../ui/Card";
import SectionHeader from "../ui/SectionHeader";

/**
 * A titled donut / pie chart card with a legend.
 *
 * @param {object} Icon     — lucide icon
 * @param {string} title    — section title
 * @param {string} color    — accent color
 * @param {Array}  segments — [{ name, value, color }]
 * @param {string} valuePrefix — prepended to legend values (e.g. "₹")
 * @param {string} valueSuffix — appended (e.g. "L")
 */
export default function PieChartCard({ Icon, title, color, segments, valuePrefix = "", valueSuffix = "" }) {
  const { width } = useWindowDimensions();

  const chartData = segments.map((s) => ({
    name:            s.name,
    population:      s.value,
    color:           s.color,
    legendFontColor: colors.textDim,
    legendFontSize:  fontSize.sm,
  }));

  const chartConfig = {
    backgroundGradientFrom: colors.card,
    backgroundGradientTo:   colors.card,
    color: () => colors.primary,
  };

  return (
    <Card>
      <SectionHeader Icon={Icon} title={title} color={color} />
      <PieChart
        data={chartData}
        width={width - 80}
        height={180}
        chartConfig={chartConfig}
        accessor="population"
        backgroundColor="transparent"
        paddingLeft="10"
        hasLegend
      />

      {/* Custom value legend */}
      <View style={styles.legend}>
        {segments.map((s) => (
          <View key={s.name} style={styles.legendRow}>
            <View style={[styles.dot, { backgroundColor: s.color }]} />
            <Text style={styles.legendName}>{s.name}</Text>
            <Text style={styles.legendValue}>
              {valuePrefix}{s.value}{valueSuffix}
            </Text>
          </View>
        ))}
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  legend: {
    marginTop: spacing.md,
    gap: spacing.xs,
  },
  legendRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 2,
  },
  legendName: {
    flex: 1,
    fontSize: fontSize.sm,
    color: colors.textDim,
  },
  legendValue: {
    fontSize: fontSize.sm,
    fontWeight: "600",
    color: colors.text,
  },
});
