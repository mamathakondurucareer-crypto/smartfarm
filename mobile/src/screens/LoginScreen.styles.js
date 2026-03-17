import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bg,
    justifyContent: "center",
    alignItems: "center",
    padding: spacing.xxl,
  },
  card: {
    width: "100%",
    maxWidth: 400,
    backgroundColor: colors.card,
    borderRadius: radius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.xxl,
  },
  brand: {
    alignItems: "center",
    marginBottom: spacing.xxl,
    gap: spacing.sm,
  },
  brandName: {
    fontSize: fontSize.h1,
    fontWeight: "700",
    color: colors.primary,
  },
  brandSub: {
    fontSize: fontSize.sm,
    color: colors.textMuted,
    textAlign: "center",
  },
  btn: {
    backgroundColor: colors.primary,
    borderRadius: radius.md,
    padding: spacing.md,
    alignItems: "center",
    marginTop: spacing.lg,
    height: 48,
    justifyContent: "center",
  },
  btnDisabled: { opacity: 0.6 },
  btnText: {
    color: colors.bg,
    fontSize: fontSize.base,
    fontWeight: "700",
  },
  hint: {
    textAlign: "center",
    marginTop: spacing.lg,
    fontSize: fontSize.sm,
    color: colors.textMuted,
  },
  hintBold: { color: colors.textDim, fontWeight: "600" },
});
