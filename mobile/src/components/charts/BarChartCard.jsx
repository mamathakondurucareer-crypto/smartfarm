import React from "react";
import { View, Text, useWindowDimensions, StyleSheet } from "react-native";
import { BarChart } from "react-native-chart-kit";
import { colors, fontSize } from "../../config/theme";
import Card from "../ui/Card";
import SectionHeader from "../ui/SectionHeader";

const CHART_CONFIG = {
  backgroundGradientFrom: colors.card,
  backgroundGradientTo:   colors.card,
  color: (opacity = 1) => `rgba(46, 204, 113, ${opacity})`,
  labelColor: () => colors.textDim,
  decimalPlaces: 0,
  propsForBackgroundLines: { stroke: colors.border },
};

/**
 * A titled bar chart card.
 *
 * @param {object}  Icon    — lucide icon
 * @param {string}  title   — section header title
 * @param {string}  color   — accent color
 * @param {string[]} labels — x-axis labels
 * @param {number[]} data   — bar values
 * @param {string}  yLabel  — y-axis unit suffix
 * @param {number}  height  — chart height (default 200)
 */
export default function BarChartCard({ Icon, title, color, labels, data, yLabel = "", height = 200 }) {
  const { width } = useWindowDimensions();

  const chartData = {
    labels,
    datasets: [{ data }],
  };

  const barConfig = {
    ...CHART_CONFIG,
    color: (opacity = 1) => (color || colors.primary) + Math.round(opacity * 255).toString(16).padStart(2, "0"),
  };

  return (
    <Card>
      <SectionHeader Icon={Icon} title={title} color={color} />
      <BarChart
        data={chartData}
        width={width - 80}
        height={height}
        chartConfig={barConfig}
        style={styles.chart}
        showValuesOnTopOfBars
        fromZero
        yAxisSuffix={yLabel}
      />
    </Card>
  );
}

const styles = StyleSheet.create({
  chart: {
    borderRadius: 8,
    marginLeft: -12,
  },
});
