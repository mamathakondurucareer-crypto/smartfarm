import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  modeRow:       { flexDirection: "row", gap: spacing.sm },
  modeBtn:       { flex: 1, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: spacing.xs, borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, paddingVertical: spacing.md },
  modeBtnText:   { fontSize: fontSize.md, color: colors.textDim, fontWeight: "600" },
  inputRow:      { flexDirection: "row", gap: spacing.sm, alignItems: "center" },
  barcodeInput:  { flex: 1, backgroundColor: colors.bg, borderRadius: radius.md, borderWidth: 2, padding: spacing.md, color: colors.text, fontSize: fontSize.base, height: 48 },
  scanBtn:       { flexDirection: "row", alignItems: "center", gap: spacing.xs, borderRadius: radius.md, paddingHorizontal: spacing.lg, height: 48, justifyContent: "center" },
  scanBtnText:   { color: colors.bg, fontWeight: "700", fontSize: fontSize.base },
  clearBtn:      { padding: spacing.sm, borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, height: 48, justifyContent: "center", alignItems: "center", paddingHorizontal: spacing.md },
  resultGrid:    { flexDirection: "row", flexWrap: "wrap", gap: spacing.md },
  resultItem:    { minWidth: 120, backgroundColor: colors.bg, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, padding: spacing.md },
  resultLabel:   { fontSize: fontSize.xs, color: colors.textMuted, marginBottom: 2, textTransform: "uppercase" },
  resultVal:     { fontSize: fontSize.base, color: colors.text, fontWeight: "600" },
  historyRow:    { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingVertical: spacing.sm, borderBottomWidth: 1, borderBottomColor: colors.border + "40" },
  historyLeft:   { flex: 1 },
  historyCode:   { fontSize: fontSize.md, color: colors.text, fontWeight: "600" },
  historyMeta:   { fontSize: fontSize.xs, color: colors.textMuted },
  historyName:   { fontSize: fontSize.sm, color: colors.textDim, flex: 1, textAlign: "right" },
});
