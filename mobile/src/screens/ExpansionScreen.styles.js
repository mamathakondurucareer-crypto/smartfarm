import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  milestoneRow:        { marginBottom: spacing.lg, borderBottomWidth: 1, borderBottomColor: colors.border, paddingBottom: spacing.md },
  milestoneName:       { fontSize: fontSize.md, color: colors.text, fontWeight: "600" },
  milestoneMeta:       { fontSize: fontSize.xs, color: colors.textMuted, marginTop: 4 },
  progressContainer:   { marginTop: spacing.md },
  progressText:        { fontSize: fontSize.xs, color: colors.textDim, marginTop: 4, textAlign: "center" },

  phaseName:           { fontSize: fontSize.md, color: colors.text, fontWeight: "600" },
  phaseMeta:           { fontSize: fontSize.xs, color: colors.textMuted, marginTop: 2 },
  phaseProgress:       { fontSize: fontSize.md, color: colors.accent, fontWeight: "700" },

  capexRow:            { flexDirection: "row", gap: spacing.md, marginBottom: spacing.lg },
  capexCol:            { flex: 1, backgroundColor: colors.card, borderRadius: radius.sm, padding: spacing.md, alignItems: "center" },
  capexLabel:          { fontSize: fontSize.xs, color: colors.textDim, marginBottom: 4 },
  capexValue:          { fontSize: fontSize.lg, color: colors.accent, fontWeight: "700" },

  capexProgressContainer: { marginTop: spacing.md },
  capexProgressText:   { fontSize: fontSize.xs, color: colors.textDim, marginTop: 4, textAlign: "center" },
});
