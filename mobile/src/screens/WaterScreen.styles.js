import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  flowRow:      { flexDirection: "row", alignItems: "center", gap: spacing.xs, paddingVertical: spacing.sm },
  flowItem:     { flexDirection: "row", alignItems: "center", gap: spacing.xs },
  flowNode:     { alignItems: "center", padding: spacing.md, borderRadius: radius.lg, borderWidth: 1, minWidth: 90 },
  flowLabel:    { fontSize: fontSize.xs, fontWeight: "700", color: colors.text, marginTop: 4, textAlign: "center" },
  recycleLabel: { paddingHorizontal: spacing.sm, paddingVertical: spacing.xs, borderWidth: 1, borderStyle: "dashed", borderColor: colors.water, borderRadius: radius.sm },
  recycleTxt:   { fontSize: fontSize.sm, fontWeight: "600" },
});
