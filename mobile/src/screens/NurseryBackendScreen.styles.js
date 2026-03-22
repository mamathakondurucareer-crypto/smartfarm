import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  // ── Container ────────────────────────────────────────────────────────────
  container: {
    flex: 1,
    backgroundColor: colors.bg,
  },

  // ── Header ───────────────────────────────────────────────────────────────
  header: {
    backgroundColor: colors.info,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg,
  },
  headerTitle: {
    fontSize: fontSize.h1,
    fontWeight: "bold",
    color: colors.white,
  },

  // ── Tab Bar ──────────────────────────────────────────────────────────────
  tabBar: {
    flexDirection: "row",
    backgroundColor: colors.card,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  tabButton: {
    flex: 1,
    paddingVertical: spacing.md,
    alignItems: "center",
  },
  tabActive: {
    borderBottomWidth: 3,
    borderBottomColor: colors.info,
  },
  tabButtonText: {
    fontSize: fontSize.lg,
    color: colors.textDim,
    fontWeight: "500",
  },
  tabActiveText: {
    color: colors.info,
  },

  // ── Scroll View ──────────────────────────────────────────────────────────
  scrollView: {
    flex: 1,
  },
  tabContent: {
    padding: spacing.lg,
  },
  centerContent: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },

  // ── Summary Card (Batches) ───────────────────────────────────────────────
  summaryCard: {
    backgroundColor: colors.card,
    borderRadius: radius.md,
    flexDirection: "row",
    marginBottom: spacing.lg,
    padding: spacing.md,
    borderLeftWidth: 4,
    borderLeftColor: colors.primary,
  },
  summaryItem: {
    flex: 1,
    alignItems: "center",
  },
  summaryLabel: {
    fontSize: fontSize.md,
    color: colors.textDim,
    marginBottom: spacing.xs,
  },
  summaryValue: {
    fontSize: fontSize.xxl,
    fontWeight: "bold",
    color: colors.primary,
  },

  // ── Revenue Card (Orders) ────────────────────────────────────────────────
  revenueCard: {
    backgroundColor: colors.card,
    borderRadius: radius.md,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    borderLeftWidth: 4,
    borderLeftColor: colors.info,
    alignItems: "center",
  },
  revenueLabel: {
    fontSize: fontSize.md,
    color: colors.textDim,
    marginBottom: spacing.md,
  },
  revenueValue: {
    fontSize: 24,
    fontWeight: "bold",
    color: colors.info,
  },

  // ── Add Button ───────────────────────────────────────────────────────────
  addButton: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: radius.md,
    marginBottom: spacing.lg,
    alignItems: "center",
  },
  addButtonText: {
    color: colors.white,
    fontWeight: "bold",
    fontSize: fontSize.lg,
  },

  // ── List Item ────────────────────────────────────────────────────────────
  listItem: {
    backgroundColor: colors.card,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderRadius: radius.md,
    borderLeftWidth: 4,
  },
  listItemContent: {
    flex: 1,
  },
  listItemHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.md,
  },
  listItemTitle: {
    fontSize: fontSize.xl,
    fontWeight: "bold",
    marginLeft: spacing.md,
    flex: 1,
    color: colors.text,
  },
  listItemSubtitle: {
    fontSize: fontSize.base,
    color: colors.textDim,
    marginBottom: spacing.md,
  },
  listItemRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: spacing.md,
  },
  listItemText: {
    fontSize: fontSize.base,
    color: colors.textDim,
  },
  listItemMeta: {
    fontSize: fontSize.md,
    color: colors.textMuted,
    marginBottom: spacing.xs,
  },

  // ── Status Badge ─────────────────────────────────────────────────────────
  statusBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.sm,
  },
  statusText: {
    color: colors.white,
    fontSize: fontSize.md,
    fontWeight: "bold",
  },

  // ── Action Buttons ───────────────────────────────────────────────────────
  actionButtons: {
    flexDirection: "row",
    marginTop: spacing.md,
  },
  smallButton: {
    flex: 1,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: radius.sm,
    alignItems: "center",
    marginHorizontal: spacing.xs,
  },
  editButton: {
    backgroundColor: colors.warn,
  },
  deleteButton: {
    backgroundColor: colors.service,
  },
  smallButtonText: {
    color: colors.white,
    fontWeight: "bold",
    fontSize: fontSize.md,
  },

  // ── Empty State ──────────────────────────────────────────────────────────
  emptyState: {
    alignItems: "center",
    paddingVertical: spacing.xxl * 2,
    paddingHorizontal: spacing.xxl,
  },
  emptyTitle: {
    fontSize: fontSize.xl,
    fontWeight: "bold",
    color: colors.textDim,
    marginTop: spacing.lg,
    marginBottom: spacing.sm,
  },
  emptyText: {
    fontSize: fontSize.base,
    color: colors.textMuted,
    textAlign: "center",
    lineHeight: 20,
  },

  // ── Modal ────────────────────────────────────────────────────────────────
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.6)",
    justifyContent: "center",
    alignItems: "center",
    padding: spacing.xl,
  },
  modalContent: {
    backgroundColor: colors.card,
    borderRadius: radius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    width: "100%",
    maxWidth: 560,
    maxHeight: "88%",
    paddingTop: spacing.lg,
  },
  modalTitle: {
    fontSize: fontSize.xxl,
    fontWeight: "bold",
    marginHorizontal: spacing.lg,
    marginBottom: spacing.md,
    color: colors.text,
  },
  modalScroll: {
    paddingHorizontal: spacing.lg,
    maxHeight: 400,
  },

  // ── Form Fields ──────────────────────────────────────────────────────────
  fieldLabel: {
    fontSize: fontSize.base,
    fontWeight: "bold",
    color: colors.text,
    marginTop: spacing.md,
    marginBottom: spacing.sm,
  },
  fieldInput: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    fontSize: fontSize.lg,
    backgroundColor: colors.bg,
    color: colors.text,
  },

  // ── Modal Actions ────────────────────────────────────────────────────────
  modalActions: {
    flexDirection: "row",
    padding: spacing.lg,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  button: {
    flex: 1,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    alignItems: "center",
    marginHorizontal: spacing.md,
  },
  cancelButton: {
    backgroundColor: colors.border,
  },
  submitButton: {
    backgroundColor: colors.info,
  },
  buttonText: {
    color: colors.white,
    fontWeight: "bold",
    fontSize: fontSize.lg,
  },
});
