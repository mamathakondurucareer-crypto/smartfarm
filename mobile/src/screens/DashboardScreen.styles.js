import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  alertRow: { flexDirection: "row", gap: spacing.sm, paddingVertical: spacing.sm, alignItems: "flex-start" },
  alertBody:{ flex: 1 },
  alertMsg: { fontSize: fontSize.md, color: colors.text },
  alertMeta:{ fontSize: fontSize.xs, color: colors.textMuted, marginTop: 2 },
  autoGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  autoItem: {
    flexDirection: "row", alignItems: "center", gap: spacing.sm,
    backgroundColor: colors.bg, borderRadius: radius.md,
    paddingHorizontal: spacing.md, paddingVertical: spacing.sm,
    width: "47%",
  },
  autoDot:    { width: 8, height: 8, borderRadius: 4 },
  autoName:   { fontSize: fontSize.sm, fontWeight: "600", color: colors.text, textTransform: "capitalize" },
  autoStatus: { fontSize: fontSize.xs, color: colors.textDim },
});
