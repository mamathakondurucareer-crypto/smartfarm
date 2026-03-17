import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  filterBar: {
    flexDirection: "row",
    gap: spacing.sm,
    marginBottom: spacing.sm,
    alignItems: "center",
  },
  searchWrap: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    backgroundColor: colors.card,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
  },
  searchInput: {
    flex: 1,
    color: colors.text,
    fontSize: fontSize.base,
    paddingVertical: spacing.sm,
  },
  refreshBtn: {
    padding: spacing.sm,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  logRow: {
    flexDirection: "row",
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border + "40",
    gap: spacing.sm,
  },
  failureRow: {
    backgroundColor: colors.danger + "08",
  },
  logLeft: {
    paddingTop: 4,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  logBody: {
    flex: 1,
  },
  logTop: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    marginBottom: 4,
  },
  logAction: {
    fontSize: fontSize.md,
    color: colors.text,
    fontWeight: "600",
  },
  logDesc: {
    fontSize: fontSize.sm,
    color: colors.textDim,
    marginBottom: 4,
  },
  logBottom: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  logMeta: {
    fontSize: fontSize.xs,
    color: colors.textMuted,
  },
  logEntity: {
    fontSize: fontSize.xs,
    color: colors.textMuted,
    marginTop: 2,
  },
  loadMore: {
    padding: spacing.md,
    alignItems: "center",
    marginTop: spacing.sm,
  },
  loadMoreText: {
    color: colors.primary,
    fontSize: fontSize.md,
    fontWeight: "600",
  },
});
