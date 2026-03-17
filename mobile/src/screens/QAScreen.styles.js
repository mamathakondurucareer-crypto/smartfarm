import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  // Screen-specific styles (gap, cardHeader, addButton, modalOverlay, modalContent,
  // modalTitle, label, input, cancelButton, saveButton, errorBox, emptyState,
  // emptyTitle, emptyText exist in common.js and should be imported as cs.xxx)

  container: {
    flex: 1,
    backgroundColor: colors.bg,
  },

  header: {
    backgroundColor: colors.info,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.lg,
  },

  headerTitle: {
    fontSize: fontSize.xxl,
    fontWeight: "bold",
    color: colors.white,
  },

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

  scrollView: {
    flex: 1,
  },

  tabContent: {
    padding: spacing.lg,
  },

  listItem: {
    backgroundColor: colors.card,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderRadius: radius.md,
    borderLeftWidth: 4,
    borderLeftColor: colors.info,
  },

  listItemContent: {
    flex: 1,
  },

  listItemHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.sm,
  },

  listItemTitle: {
    fontSize: fontSize.xl,
    fontWeight: "bold",
    marginLeft: spacing.sm,
    flex: 1,
    color: colors.text,
  },

  listItemSubtitle: {
    fontSize: fontSize.base,
    color: colors.textDim,
    marginBottom: spacing.sm,
  },

  listItemRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: spacing.sm,
  },

  listItemText: {
    fontSize: fontSize.base,
    color: colors.textDim,
  },

  listItemMeta: {
    fontSize: fontSize.md,
    color: colors.textMuted,
  },

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

  resolveButton: {
    backgroundColor: colors.warn,
    paddingVertical: spacing.xs,
    paddingHorizontal: spacing.md,
    borderRadius: radius.sm,
    marginTop: spacing.sm,
    alignItems: "center",
  },

  resolveButtonText: {
    color: colors.white,
    fontWeight: "bold",
    fontSize: fontSize.md,
  },

  centerContent: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },

  modalSubtitle: {
    fontSize: fontSize.lg,
    fontWeight: "bold",
    color: colors.info,
    marginTop: spacing.md,
    marginBottom: spacing.sm,
  },

  modalScroll: {
    paddingHorizontal: spacing.lg,
    maxHeight: 400,
  },

  traceCard: {
    backgroundColor: colors.bg,
    padding: spacing.md,
    borderRadius: radius.md,
    marginBottom: spacing.md,
    borderLeftWidth: 3,
    borderLeftColor: colors.info,
  },

  traceText: {
    fontSize: fontSize.base,
    color: colors.text,
    marginBottom: spacing.xs,
  },

  fieldLabel: {
    fontSize: fontSize.base,
    fontWeight: "bold",
    color: colors.text,
    marginTop: spacing.md,
    marginBottom: spacing.xs,
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

  checkboxContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginVertical: spacing.sm,
  },

  checkbox: {
    width: 24,
    height: 24,
    borderWidth: 2,
    borderColor: colors.border,
    borderRadius: radius.sm,
    marginRight: spacing.sm,
  },

  checkboxChecked: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },

  checkboxLabel: {
    fontSize: fontSize.lg,
    color: colors.text,
  },

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
    marginHorizontal: spacing.sm,
  },

  submitButton: {
    backgroundColor: colors.info,
  },

  closeButton: {
    backgroundColor: colors.info,
    marginHorizontal: spacing.lg,
    marginBottom: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    alignItems: "center",
  },

  closeButtonText: {
    color: colors.white,
    fontWeight: "bold",
    fontSize: fontSize.lg,
  },
});
