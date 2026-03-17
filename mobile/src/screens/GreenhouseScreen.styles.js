import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  // Note: gap, cardHeader, addButton, addButtonText are imported from commonStyles

  cropCard: {
    backgroundColor: colors.bg,
    borderRadius: radius.lg,
    padding: spacing.md,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  cropHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: spacing.sm,
  },
  cropTitleRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    flex: 1,
  },
  cropName: {
    fontSize: fontSize.lg,
    fontWeight: "700",
    color: colors.text,
  },
  editIconSmall: { padding: spacing.xs },
  cropMeta: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: spacing.xs,
  },
  metaText: {
    fontSize: fontSize.md,
    color: colors.textDim,
  },
  healthText: {
    fontSize: fontSize.md,
    fontWeight: "600",
  },
  yieldText: {
    fontSize: fontSize.sm,
    color: colors.textDim,
    marginBottom: spacing.xs,
  },
  progressWrap: { marginTop: 2 },

  // Note: modalOverlay, modalContent, modalTitle, formScroll, label, input are imported from commonStyles

  stagePicker: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.xs,
    marginBottom: spacing.md,
  },
  stageOption: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.bg,
  },
  stageOptionActive: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  stageOptionText: {
    fontSize: fontSize.sm,
    color: colors.textDim,
  },
  stageOptionTextActive: {
    color: colors.bg,
    fontWeight: "600",
  },

  // Note: modalButtonGroup, cancelButton, cancelButtonText, deleteButton, deleteButtonText, saveButton, saveButtonText are imported from commonStyles
});
