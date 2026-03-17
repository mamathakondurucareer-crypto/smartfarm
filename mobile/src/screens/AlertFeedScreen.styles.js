import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  alertHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    marginBottom: spacing.sm,
  },
  severityBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.sm,
  },
  severityText: {
    fontSize: fontSize.xs,
    fontWeight: "700",
    color: colors.bg,
  },
  module: {
    fontSize: fontSize.md,
    fontWeight: "600",
    color: colors.text,
    flex: 1,
  },
  message: {
    fontSize: fontSize.md,
    color: colors.text,
    lineHeight: 20,
    marginBottom: spacing.sm,
  },
  timestamp: {
    fontSize: fontSize.xs,
    color: colors.textMuted,
  },
});
