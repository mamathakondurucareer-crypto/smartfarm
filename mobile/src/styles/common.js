/**
 * Shared StyleSheet — styles used identically across 3+ screens.
 *
 * Import what you need:
 *   import { commonStyles as cs } from "../styles/common";
 *   style={cs.modalOverlay}
 *
 * Screen-specific overrides live in ScreenName.styles.js.
 */
import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const commonStyles = StyleSheet.create({
  // ── Spacers ─────────────────────────────────────────────────────────────────
  gap:     { height: spacing.lg },
  cardGap: { marginBottom: spacing.md },

  // ── Card section header row ──────────────────────────────────────────────────
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: spacing.sm,
  },

  // ── Add / action button (ghost green) ───────────────────────────────────────
  addButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.sm,
    backgroundColor: colors.primary + "15",
  },
  addButtonText: {
    fontSize: fontSize.sm,
    color: colors.primary,
    fontWeight: "600",
  },

  // Touch-target padding for icon-only edit buttons
  editIcon: { padding: spacing.xs },

  // ── Bottom-sheet modal ───────────────────────────────────────────────────────
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.5)",
    justifyContent: "flex-end",
  },
  modalContent: {
    backgroundColor: colors.card,
    borderTopLeftRadius: radius.lg,
    borderTopRightRadius: radius.lg,
    padding: spacing.lg,
    maxHeight: "85%",
  },

  // Centered dialog modal (e.g. POS, Packing)
  modalOverlayCentered: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.7)",
    justifyContent: "center",
    alignItems: "center",
    padding: spacing.xl,
  },
  modalCard: {
    backgroundColor: colors.card,
    borderRadius: radius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.xl,
    width: "100%",
    maxWidth: 480,
    maxHeight: "90%",
  },

  // Modal title
  modalTitle: {
    fontSize: fontSize.lg,
    fontWeight: "700",
    color: colors.text,
    marginBottom: spacing.md,
  },

  // Form scroll area inside modals
  formScroll: { maxHeight: 350 },

  // ── Form fields ──────────────────────────────────────────────────────────────
  label: {
    fontSize: fontSize.sm,
    fontWeight: "600",
    color: colors.text,
    marginBottom: spacing.xs,
    marginTop: spacing.md,
  },
  input: {
    backgroundColor: colors.bg,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.sm,
    fontSize: fontSize.md,
    color: colors.text,
  },

  // ── Modal action buttons ─────────────────────────────────────────────────────
  modalButtonGroup: {
    flexDirection: "row",
    gap: spacing.sm,
    marginTop: spacing.lg,
  },
  cancelButton: {
    flex: 1,
    backgroundColor: colors.border,
    borderRadius: radius.md,
    paddingVertical: spacing.sm,
    alignItems: "center",
  },
  cancelButtonText: {
    fontSize: fontSize.md,
    color: colors.textDim,
    fontWeight: "600",
  },
  deleteButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    backgroundColor: colors.danger,
    borderRadius: radius.md,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
  },
  deleteButtonText: {
    fontSize: fontSize.md,
    color: colors.bg,
    fontWeight: "600",
  },
  saveButton: {
    flex: 1,
    backgroundColor: colors.primary,
    borderRadius: radius.md,
    paddingVertical: spacing.sm,
    alignItems: "center",
  },
  saveButtonText: {
    fontSize: fontSize.md,
    color: colors.bg,
    fontWeight: "600",
  },

  // ── Empty states ─────────────────────────────────────────────────────────────
  emptyState: {
    alignItems: "center",
    paddingVertical: spacing.xxl * 2,
    paddingHorizontal: spacing.xxl,
  },
  emptyTitle: {
    fontSize: fontSize.xl,
    fontWeight: "bold",
    color: colors.textDim,
    marginTop: spacing.lg,
    marginBottom: spacing.sm,
  },
  emptyText: {
    fontSize: fontSize.base,
    color: colors.textMuted,
    textAlign: "center",
    lineHeight: 20,
  },
  // Inline single-line empty state (used in list cards without icon)
  empty: {
    color: colors.textMuted,
    fontSize: fontSize.md,
    textAlign: "center",
    paddingVertical: spacing.lg,
  },

  // ── Error box ────────────────────────────────────────────────────────────────
  errorBox: {
    backgroundColor: colors.danger + "20",
    borderWidth: 1,
    borderColor: colors.danger + "40",
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  errorText: {
    color: colors.danger,
    fontSize: fontSize.md,
  },

  // ── Chip / filter rows ───────────────────────────────────────────────────────
  chipRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.xs,
    marginBottom: spacing.sm,
  },
  chip: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.bg,
  },
  chipText: {
    fontSize: fontSize.sm,
    color: colors.textDim,
  },
  chipActive: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  chipActiveText: {
    color: colors.bg,
    fontWeight: "600",
  },

  // ── Tab bars ─────────────────────────────────────────────────────────────────
  tabBar: {
    flexDirection: "row",
    gap: spacing.xs,
    marginBottom: spacing.md,
  },
  tab: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.bg,
  },
  tabText: {
    fontSize: fontSize.sm,
    color: colors.textDim,
  },
  tabActive: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  tabActiveText: {
    color: colors.bg,
    fontWeight: "600",
  },

  // ── List rows ─────────────────────────────────────────────────────────────────
  row: {
    flexDirection: "row",
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border + "40",
  },
  topRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: spacing.md,
  },
  count: {
    fontSize: fontSize.md,
    color: colors.textDim,
  },
});
