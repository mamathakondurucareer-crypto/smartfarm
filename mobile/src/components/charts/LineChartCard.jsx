import React from "react";
import { View, StyleSheet } from "react-native";
import { LineChart } from "react-native-chart-kit";
import { colors } from "../../config/theme";
import Card from "../ui/Card";
import SectionHeader from "../ui/SectionHeader";
import { useResponsive } from "../../hooks/useResponsive";

/**
 * A titled line chart card supporting multiple datasets.
 *
 * @param {object}   Icon      — lucide icon
 * @param {string}   title     — section title
 * @param {string}   color     — accent color
 * @param {string[]} labels    — x-axis labels
 * @param {Array}    datasets  — [{ data: number[], color: string, label: string }]
 * @param {number}   height    — chart height (default 200)
 */
export default function LineChartCard({ Icon, title, color, labels, datasets, height = 200 }) {
  const { chartWidth } = useResponsive();

  const chartData = {
    labels,
    datasets: datasets.map((ds) => ({
      data:          ds.data,
      color:         (opacity = 1) => ds.color + Math.round(opacity * 255).toString(16).padStart(2, "0"),
      strokeWidth:   2,
    })),
    legend: datasets.map((ds) => ds.label),
  };

  const chartConfig = {
    backgroundGradientFrom: colors.card,
    backgroundGradientTo:   colors.card,
    color: (opacity = 1) => `rgba(46, 204, 113, ${opacity})`,
    labelColor:  () => colors.textDim,
    decimalPlaces: 1,
    propsForBackgroundLines: { stroke: colors.border },
  };

  return (
    <Card>
      <SectionHeader Icon={Icon} title={title} color={color} />
      <LineChart
        data={chartData}
        width={chartWidth}
        height={height}
        chartConfig={chartConfig}
        style={styles.chart}
        bezier
        withDots={false}
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
