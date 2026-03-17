import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  addBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    backgroundColor: colors.primary,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  addBtnText: {
    color: colors.bg,
    fontSize: fontSize.md,
    fontWeight: "700",
  },
  tableHead: {
    backgroundColor: colors.bg,
    borderRadius: radius.sm,
    marginBottom: spacing.xs,
  },
  headText: {
    fontSize: fontSize.xs,
    color: colors.textMuted,
    fontWeight: "600",
    textTransform: "uppercase",
  },
  rowSelf: {
    backgroundColor: colors.primary + "08",
  },
  col: {
    paddingHorizontal: spacing.xs,
  },
  colName: {
    flex: 3,
  },
  colRole: {
    flex: 2,
    alignItems: "flex-start",
  },
  colStatus: {
    flex: 2,
    alignItems: "center",
  },
  colAction: {
    flex: 2,
    alignItems: "center",
  },
  userName: {
    fontSize: fontSize.md,
    color: colors.text,
    fontWeight: "600",
  },
  userSub: {
    fontSize: fontSize.xs,
    color: colors.textMuted,
    marginTop: 1,
  },
  toggleBtn: {
    borderWidth: 1,
    borderRadius: radius.sm,
    paddingHorizontal: spacing.sm,
    paddingVertical: 3,
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: spacing.lg,
  },
  modalTitle: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  modalTitleText: {
    fontSize: fontSize.lg,
    fontWeight: "700",
    color: colors.text,
  },
  rolePicker: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: colors.bg,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
  },
  roleList: {
    backgroundColor: colors.bg,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    marginTop: 2,
    overflow: "hidden",
  },
  roleItem: {
    padding: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border + "40",
  },
  roleItemActive: {
    backgroundColor: colors.primary + "15",
  },
  roleDesc: {
    fontSize: fontSize.xs,
    color: colors.textMuted,
    marginTop: 2,
  },
  saveBtn: {
    backgroundColor: colors.primary,
    borderRadius: radius.md,
    padding: spacing.md,
    alignItems: "center",
    marginTop: spacing.xl,
    height: 48,
    justifyContent: "center",
  },
  saveBtnText: {
    color: colors.bg,
    fontSize: fontSize.base,
    fontWeight: "700",
  },
});
