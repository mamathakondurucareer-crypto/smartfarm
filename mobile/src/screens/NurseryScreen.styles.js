import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  gap:              { height: spacing.lg },
  sectionHeader:    { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.sm },
  editButton:       { padding: spacing.xs },
  row:              { flexDirection: "row", justifyContent: "space-between", paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: colors.border + "40" },
  label:            { fontSize: fontSize.md, color: colors.textDim },
  value:            { fontSize: fontSize.md, color: colors.text, fontWeight: "500", flexShrink: 1, textAlign: "right", marginLeft: spacing.sm },
  formLabel:        { fontSize: fontSize.sm, fontWeight: "600", color: colors.text, marginBottom: spacing.xs, marginTop: spacing.md },
});
