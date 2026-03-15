import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../../config/theme";

/**
 * Section title row with a tinted icon on the left and
 * optional action slot on the right.
 */
export default function SectionHeader({ Icon, title, color = colors.primary, action }) {
  return (
    <View style={styles.row}>
      <View style={styles.left}>
        <View style={[styles.iconWrap, { backgroundColor: color + "22" }]}>
          <Icon size={16} color={color} />
        </View>
        <Text style={styles.title}>{title}</Text>
      </View>
      {action && <View>{action}</View>}
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: spacing.lg,
  },
  left: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  iconWrap: {
    width: 32,
    height: 32,
    borderRadius: radius.md,
    alignItems: "center",
    justifyContent: "center",
  },
  title: {
    fontSize: fontSize.xxl,
    fontWeight: "700",
    color: colors.text,
  },
});
