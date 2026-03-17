import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  addBtn:           { flexDirection: "row", alignItems: "center", gap: spacing.xs, backgroundColor: colors.logistics, borderRadius: radius.md, paddingHorizontal: spacing.md, paddingVertical: spacing.sm },
  addBtnText:       { color: colors.bg, fontSize: fontSize.md, fontWeight: "700" },
  tripCode:         { fontSize: fontSize.md, color: colors.text, fontWeight: "600" },
  tripMeta:         { fontSize: fontSize.xs, color: colors.textMuted, marginTop: 2 },
  actionBtn:        { borderWidth: 1, borderRadius: radius.sm, paddingHorizontal: spacing.sm, paddingVertical: 3 },
  modalHeader:      { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.lg },
  typeRow:          { flexDirection: "row", flexWrap: "wrap", gap: spacing.xs, marginTop: spacing.xs },
  typeChip:         { borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, paddingHorizontal: spacing.md, paddingVertical: spacing.xs },
  typeChipActive:   { borderColor: colors.primary, backgroundColor: colors.primary + "15" },
  saveBtn:          { backgroundColor: colors.logistics, borderRadius: radius.md, padding: spacing.md, alignItems: "center", marginTop: spacing.xl, height: 48, justifyContent: "center" },
  saveBtnText:      { color: colors.bg, fontSize: fontSize.base, fontWeight: "700" },
});
