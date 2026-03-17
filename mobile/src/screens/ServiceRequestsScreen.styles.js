import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  topRow:        { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.md },
  count:         { fontSize: fontSize.md, color: colors.textDim },
  addBtn:        { flexDirection: "row", alignItems: "center", gap: spacing.xs, backgroundColor: colors.service, borderRadius: radius.md, paddingHorizontal: spacing.md, paddingVertical: spacing.sm },
  addBtnText:    { color: colors.bg, fontSize: fontSize.md, fontWeight: "700" },
  empty:         { color: colors.textMuted, fontSize: fontSize.md, textAlign: "center", paddingVertical: 30 },
  row:           { flexDirection: "row", paddingVertical: spacing.md, borderBottomWidth: 1, borderBottomColor: colors.border + "40", alignItems: "center" },
  reqTitle:      { fontSize: fontSize.md, color: colors.text, fontWeight: "600" },
  reqMeta:       { fontSize: fontSize.xs, color: colors.textMuted, marginTop: 2 },
  modalHeader:   { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.lg },
  modalTitleText:{ fontSize: fontSize.lg, fontWeight: "700", color: colors.text },
  chipRow:       { flexDirection: "row", flexWrap: "wrap", gap: spacing.xs },
  chip:          { borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, paddingHorizontal: spacing.md, paddingVertical: spacing.xs },
  chipActive:    { borderColor: colors.primary, backgroundColor: colors.primary + "15" },
  saveBtn:       { backgroundColor: colors.service, borderRadius: radius.md, padding: spacing.md, alignItems: "center", marginTop: spacing.xl, height: 48, justifyContent: "center" },
  saveBtnText:   { color: colors.bg, fontSize: fontSize.base, fontWeight: "700" },
});
