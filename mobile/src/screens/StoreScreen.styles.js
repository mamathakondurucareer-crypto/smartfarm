import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  actionRow:      { flexDirection: "row", gap: spacing.md, marginBottom: spacing.md },
  actionBtn:      { flex: 1, borderWidth: 1, borderRadius: radius.md, paddingVertical: spacing.md, alignItems: "center" },
  actionBtnText:  { fontSize: fontSize.base, fontWeight: "700" },
  stockRow:       { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingVertical: spacing.sm, borderBottomWidth: 1, borderBottomColor: colors.border + "40" },
  stockName:      { fontSize: fontSize.base, color: colors.text, flex: 1 },
  stockRight:     { flexDirection: "row", alignItems: "center", gap: spacing.sm },
  stockQty:       { fontSize: fontSize.md, color: colors.warn, fontWeight: "600" },
});
