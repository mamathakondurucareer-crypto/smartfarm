import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  tabBar: {
    flexGrow: 0,
    marginBottom: spacing.lg,
  },
  tabBarContent: {
    gap: spacing.sm,
  },
  tab: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  tabActive: {
    borderColor: colors.reports,
    backgroundColor: colors.reports + "20",
  },
  tabText: {
    fontSize: fontSize.md,
    color: colors.textDim,
    fontWeight: "600",
  },
  tabTextActive: {
    color: colors.reports,
  },
  cell: {
    fontSize: fontSize.md,
    color: colors.text,
  },
});
