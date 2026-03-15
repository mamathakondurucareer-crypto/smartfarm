import React from "react";
import { View, StyleSheet } from "react-native";
import { spacing } from "../../config/theme";
import { useResponsive } from "../../hooks/useResponsive";
import StatCard from "./StatCard";

/**
 * Responsive grid of StatCards.
 * Adapts column count based on screen width automatically.
 *
 * @param {Array} stats — array of StatCard props objects
 */
export default function StatGrid({ stats }) {
  const { statColumns } = useResponsive();

  return (
    <View style={styles.grid}>
      {stats.map((s, i) => (
        <View key={i} style={{ width: `${100 / statColumns}%`, padding: spacing.xs }}>
          <StatCard {...s} />
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    marginHorizontal: -spacing.xs,
  },
});
