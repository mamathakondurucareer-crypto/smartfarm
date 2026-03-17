import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  empName:  { fontSize: fontSize.md, color: colors.text, fontWeight: "600" },
  empMeta:  { fontSize: fontSize.xs, color: colors.textMuted, marginTop: 2 },
});
