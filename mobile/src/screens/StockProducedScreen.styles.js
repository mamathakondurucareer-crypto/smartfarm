import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  filterRow:      { flexDirection: "row", gap: spacing.sm, alignItems: "flex-end", flexWrap: "wrap" },
  filterField:    { flex: 1, minWidth: 120 },
  refreshBtn:     { flexDirection: "row", alignItems: "center", gap: spacing.xs, backgroundColor: colors.packing, borderRadius: radius.md, paddingHorizontal: spacing.md, paddingVertical: spacing.md, marginTop: spacing.lg },
  refreshBtnText: { color: colors.bg, fontWeight: "700", fontSize: fontSize.md },
});
