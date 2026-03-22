import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../../config/theme";
import { useResponsive } from "../../hooks/useResponsive";

/**
 * A compact metric card showing an icon, label, value, and optional sub-text.
 *
 * @param {React.Component} Icon  — lucide-react-native icon
 * @param {string}  label         — metric name
 * @param {string|number} value   — primary display value
 * @param {string}  unit          — appended to value (e.g. "°C")
 * @param {string}  color         — accent color
 * @param {string}  sub           — secondary line below value
 * @param {boolean} compact       — smaller variant for dense layouts
 */
export default function StatCard({ Icon, icon, label, value, unit, color = colors.primary, sub, compact }) {
  if (!Icon && icon) Icon = icon;
  const { isDesktop } = useResponsive();
  const iconSize  = compact ? 32 : isDesktop ? 44 : 38;
  const iconInner = compact ? 16 : isDesktop ? 20 : 18;
  const valueSize = compact ? fontSize.xl : isDesktop ? fontSize.h1 + 2 : fontSize.h1;

  return (
    <View style={styles.card}>
      {Icon && (
        <View style={[styles.iconWrap, { width: iconSize, height: iconSize, backgroundColor: color + "22" }]}>
          <Icon size={iconInner} color={color} />
        </View>
      )}
      <View style={styles.body}>
        <Text style={styles.label} numberOfLines={1}>{label}</Text>
        <View style={styles.valueRow}>
          <Text style={[styles.value, { fontSize: valueSize }]}>{value}</Text>
          {unit && <Text style={styles.unit}>{unit}</Text>}
        </View>
        {sub && <Text style={styles.sub} numberOfLines={1}>{sub}</Text>}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
  },
  iconWrap: {
    borderRadius: radius.md,
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  body: {
    flex: 1,
    minWidth: 0,
  },
  label: {
    fontSize: fontSize.sm,
    color: colors.textDim,
  },
  valueRow: {
    flexDirection: "row",
    alignItems: "flex-end",
    gap: 3,
  },
  value: {
    fontWeight: "700",
    color: colors.text,
  },
  unit: {
    fontSize: fontSize.sm,
    color: colors.textDim,
    marginBottom: 2,
  },
  sub: {
    fontSize: fontSize.xs,
    color: colors.textMuted,
    marginTop: 1,
  },
});
