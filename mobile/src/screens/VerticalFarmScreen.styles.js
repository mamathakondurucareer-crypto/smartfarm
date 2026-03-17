import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  // Note: gap, cardHeader, addButton, addButtonText are imported from commonStyles

  tierCard: {
    backgroundColor: colors.bg,
    borderRadius: radius.lg,
    padding: spacing.md,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  tierHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: spacing.sm,
  },
  tierTitleRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  tierCrop: {
    fontSize: fontSize.lg,
    fontWeight: "700",
    color: colors.text,
  },
  editIconSmall: { padding: spacing.xs },
  tierGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
  },
  metaItem: { width: "47%" },
  metaLabel: {
    fontSize: fontSize.xs,
    color: colors.textMuted,
  },
  metaValue: {
    fontSize: fontSize.sm,
    color: colors.textDim,
    marginTop: 1,
  },

  // Note: modalOverlay, modalContent, modalTitle, formScroll, label, input are imported from commonStyles

  // Note: modalButtonGroup, cancelButton, cancelButtonText, deleteButton, deleteButtonText, saveButton, saveButtonText are imported from commonStyles
});
