import React from "react";
import { View, StyleSheet } from "react-native";
import { colors } from "../../config/theme";

/** Thin horizontal progress bar. */
export default function ProgressBar({ value, max, color = colors.primary, height = 6 }) {
  const pct = Math.min((value / max) * 100, 100);

  return (
    <View style={[styles.track, { height, borderRadius: height }]}>
      <View style={[styles.fill, { width: `${pct}%`, backgroundColor: color, borderRadius: height }]} />
    </View>
  );
}

const styles = StyleSheet.create({
  track: {
    width: "100%",
    backgroundColor: colors.bg,
    overflow: "hidden",
  },
  fill: {
    height: "100%",
  },
});
