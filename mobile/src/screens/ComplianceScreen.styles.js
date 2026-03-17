import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
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

  alertBanner: {
    backgroundColor: colors.danger + "20",
    borderLeftWidth: 4,
    borderLeftColor: colors.danger,
    flexDirection: "row",
    padding: spacing.md,
    borderRadius: radius.md,
    marginBottom: spacing.lg,
    alignItems: "center",
  },

  alertContent: {
    marginLeft: spacing.md,
    flex: 1,
  },

  alertTitle: {
    fontSize: fontSize.lg,
    fontWeight: "bold",
    color: colors.danger,
  },

  alertText: {
    fontSize: fontSize.md,
    color: colors.warn,
  },

  filterButtons: {
    flexDirection: "row",
    marginBottom: spacing.lg,
  },

  filterButton: {
    flex: 1,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    backgroundColor: colors.border,
    borderRadius: radius.sm,
    marginHorizontal: spacing.xs,
    alignItems: "center",
  },

  filterButtonActive: {
    backgroundColor: colors.info,
  },

  filterButtonText: {
    fontSize: fontSize.base,
    color: colors.textDim,
    fontWeight: "500",
  },

  filterButtonActiveText: {
    color: colors.white,
  },

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
    marginBottom: spacing.sm,
  },

  listItemTitle: {
    fontSize: fontSize.xl,
    fontWeight: "bold",
    marginLeft: spacing.sm,
    flex: 1,
    color: colors.text,
  },

  completedText: {
    textDecorationLine: "line-through",
    color: colors.textMuted,
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
    marginBottom: spacing.sm,
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

  completeButton: {
    backgroundColor: colors.success,
  },

  uncompleteButton: {
    backgroundColor: colors.textMuted,
  },

  editButton: {
    backgroundColor: colors.warn,
  },

  deleteButton: {
    backgroundColor: colors.danger,
  },

  smallButtonText: {
    color: colors.white,
    fontWeight: "bold",
    fontSize: fontSize.md,
  },

  centerContent: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },

  modalScroll: {
    paddingHorizontal: spacing.lg,
    maxHeight: 400,
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
