import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  addBtn:           { flexDirection: "row", alignItems: "center", gap: spacing.xs, backgroundColor: colors.packing, borderRadius: radius.md, paddingHorizontal: spacing.md, paddingVertical: spacing.sm },
  addBtnText:       { color: colors.bg, fontSize: fontSize.md, fontWeight: "700" },
  orderRow:         { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingVertical: spacing.md, borderBottomWidth: 1, borderBottomColor: colors.border + "40" },
  orderInfo:        { flex: 1 },
  orderTopRow:      { flexDirection: "row", alignItems: "center", gap: spacing.sm, marginBottom: 2 },
  orderCode:        { fontSize: fontSize.base, color: colors.text, fontWeight: "600" },
  orderMeta:        { fontSize: fontSize.xs, color: colors.textMuted },
  orderActions:     { flexDirection: "row", gap: spacing.xs },
  actionBtn:        { flexDirection: "row", alignItems: "center", gap: 3, borderWidth: 1, borderRadius: radius.sm, paddingHorizontal: spacing.sm, paddingVertical: 4 },
  actionBtnText:    { fontSize: fontSize.xs, fontWeight: "600" },
  modalHeader:      { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.lg },
  modalTitleText:   { fontSize: fontSize.lg, fontWeight: "700", color: colors.text },
  picker:           { flexDirection: "row", justifyContent: "space-between", alignItems: "center", backgroundColor: colors.bg, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, padding: spacing.md },
  pickerList:       { backgroundColor: colors.bg, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, marginTop: 2, overflow: "hidden" },
  pickerItem:       { padding: spacing.md, borderBottomWidth: 1, borderBottomColor: colors.border + "40" },
  pickerItemActive: { backgroundColor: colors.primary + "15" },
  itemRow:          { flexDirection: "row", gap: spacing.xs, alignItems: "center", marginBottom: spacing.xs },
  removeBtn:        { padding: spacing.xs },
  addItemBtn:       { flexDirection: "row", alignItems: "center", gap: spacing.xs, marginTop: spacing.sm },
  saveBtn:          { backgroundColor: colors.packing, borderRadius: radius.md, padding: spacing.md, alignItems: "center", marginTop: spacing.xl, height: 48, justifyContent: "center" },
  saveBtnText:      { color: colors.bg, fontSize: fontSize.base, fontWeight: "700" },
});
