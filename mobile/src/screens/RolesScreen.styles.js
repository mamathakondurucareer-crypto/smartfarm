import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  cardGap: { marginBottom: spacing.md },
  cardHint: {
    fontSize: fontSize.sm,
    color: colors.textMuted,
    marginBottom: spacing.md,
    lineHeight: 18,
  },

  // ── Add button ────────────────────────────────────────────────────────────
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

  // ── Role card ─────────────────────────────────────────────────────────────
  roleCard: {
    flexDirection: "row",
    alignItems: "flex-start",
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border + "40",
    gap: spacing.sm,
  },
  roleCardLeft: {
    flex: 1,
    gap: 4,
  },
  roleCardActions: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    paddingTop: 2,
  },
  roleBadge: {
    alignSelf: "flex-start",
    paddingHorizontal: spacing.sm,
    paddingVertical: 3,
    borderRadius: radius.sm,
    borderWidth: 1,
  },
  roleBadgeText: {
    fontWeight: "700",
    letterSpacing: 0.3,
  },
  roleDesc: {
    fontSize: fontSize.sm,
    color: colors.textMuted,
    lineHeight: 18,
  },
  roleScreenCount: {
    fontSize: fontSize.xs,
    color: colors.textDim,
    marginTop: 2,
  },
  iconBtn: {
    padding: spacing.xs,
  },

  // ── Edit modal ────────────────────────────────────────────────────────────
  editModal: {
    maxHeight: "92%",
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: spacing.md,
  },
  modalTitleRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    flex: 1,
  },
  descInput: {
    minHeight: 60,
    textAlignVertical: "top",
  },

  // ── Color picker ──────────────────────────────────────────────────────────
  colorRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    marginTop: spacing.xs,
  },
  colorDot: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
  },
  colorDotActive: {
    borderWidth: 2,
    borderColor: colors.text,
  },

  // ── Screen toggles ────────────────────────────────────────────────────────
  screenHint: {
    fontSize: fontSize.xs,
    color: colors.textMuted,
    marginBottom: spacing.sm,
  },
  sectionGroup: {
    marginBottom: spacing.xs,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border + "60",
    overflow: "hidden",
  },
  sectionGroupHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    backgroundColor: colors.bg,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs + 2,
  },
  sectionGroupLabel: {
    flex: 1,
    fontSize: fontSize.sm,
    fontWeight: "600",
    color: colors.textDim,
  },
  allBtn: {
    paddingHorizontal: spacing.xs,
  },
  allBtnText: {
    fontSize: fontSize.xs,
    color: colors.textMuted,
  },
  allBtnActive: {
    color: colors.primary,
  },
  toggleRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    paddingHorizontal: spacing.sm,
    paddingVertical: 7,
    borderTopWidth: 1,
    borderTopColor: colors.border + "30",
  },
  screenIcon: {
    width: 22,
    height: 22,
    borderRadius: 6,
    alignItems: "center",
    justifyContent: "center",
  },
  screenLabel: {
    flex: 1,
    fontSize: fontSize.sm,
    color: colors.text,
  },
  switch: {
    transform: [{ scaleX: 0.8 }, { scaleY: 0.8 }],
  },

  // ── Save button ───────────────────────────────────────────────────────────
  saveBtn: {
    borderRadius: radius.md,
    padding: spacing.md,
    alignItems: "center",
    marginTop: spacing.xl,
    marginBottom: spacing.md,
    height: 48,
    justifyContent: "center",
  },
  saveBtnText: {
    color: "#fff",
    fontSize: fontSize.base,
    fontWeight: "700",
  },
});
