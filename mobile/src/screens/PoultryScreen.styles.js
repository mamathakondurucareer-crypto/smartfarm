import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  gap:              { height: spacing.lg },
  sectionHeader:    { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.sm },
  editButton:       { padding: spacing.xs },
  infoBox:          { backgroundColor: colors.bg, borderRadius: radius.md, padding: spacing.md, marginTop: spacing.md },
  infoText:         { fontSize: fontSize.md, color: colors.textDim, lineHeight: 20 },
  bold:             { fontWeight: "600", color: colors.text },
});
