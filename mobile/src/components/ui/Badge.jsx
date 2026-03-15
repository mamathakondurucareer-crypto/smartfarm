import React from "react";
import { Text, View, StyleSheet } from "react-native";
import { colors, fontSize } from "../../config/theme";

/**
 * A small pill label with a tinted background.
 * @param {string} label   — text to display
 * @param {string} color   — foreground + tint base color
 */
export default function Badge({ label, color = colors.primary }) {
  return (
    <View style={[styles.pill, { backgroundColor: color + "22" }]}>
      <Text style={[styles.text, { color }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  pill: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    alignSelf: "flex-start",
  },
  text: {
    fontSize: fontSize.xs,
    fontWeight: "600",
  },
});
