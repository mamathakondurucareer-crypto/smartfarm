import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  hint:        { fontSize: fontSize.sm, color: colors.textMuted, marginTop: spacing.xs },
  section:     {},
  catLabel:    { fontSize: fontSize.xs, fontWeight: "700", color: colors.textMuted, textTransform: "uppercase", letterSpacing: 0.8, marginBottom: spacing.xs, paddingHorizontal: spacing.xs },
  rowBorder:   { borderBottomWidth: 1, borderBottomColor: colors.border },
  rowLeft:     { flexDirection: "row", alignItems: "center", gap: spacing.sm },
  iconBox:     { width: 28, height: 28, borderRadius: radius.sm, alignItems: "center", justifyContent: "center" },
  rowLabel:    { fontSize: fontSize.md, color: colors.text },
  rowLabelOff: { color: colors.textMuted },
});
