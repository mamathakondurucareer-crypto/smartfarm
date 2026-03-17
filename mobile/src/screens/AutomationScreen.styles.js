import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  cardWrap:   { marginBottom: spacing.md },
  header:     { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: spacing.md },
  headerLeft: { flexDirection: "row", alignItems: "center", gap: spacing.md },
  iconBox:    { width: 40, height: 40, borderRadius: radius.md, alignItems: "center", justifyContent: "center" },
  sysName:    { fontSize: fontSize.base, fontWeight: "700", color: colors.text, marginBottom: 4 },
  statusDot:  { width: 10, height: 10, borderRadius: 5 },
  details:    { gap: spacing.xs },
  detailLine: { fontSize: fontSize.sm, color: colors.textDim },
});
