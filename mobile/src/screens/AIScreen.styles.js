import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  chipsScroll:       { marginBottom: spacing.md, flexGrow: 0 },
  chips:             { gap: spacing.sm, paddingHorizontal: 2 },
  chip:              { backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, paddingHorizontal: spacing.md, paddingVertical: spacing.sm },
  chipDisabled:      { opacity: 0.4 },
  chipText:          { fontSize: fontSize.md, color: colors.textDim },
  chatContainer:     { flex: 1, backgroundColor: colors.card, borderRadius: radius.xl, borderWidth: 1, borderColor: colors.border, overflow: "hidden", minHeight: 400 },
  messageList:       { flex: 1 },
  messageListContent:{ padding: spacing.lg, gap: spacing.md },
  emptyBody:         { fontSize: fontSize.md, color: colors.textMuted, textAlign: "center", lineHeight: 20 },
  bubble:            { maxWidth: "88%", padding: spacing.md, borderRadius: radius.lg, borderWidth: 1 },
  userBubble:        { alignSelf: "flex-end", backgroundColor: colors.primary + "25", borderColor: colors.primary + "40" },
  aiBubble:          { alignSelf: "flex-start", backgroundColor: colors.bg, borderColor: colors.border },
  bubbleMeta:        { fontSize: fontSize.xs, color: colors.textMuted, marginBottom: 4 },
  bubbleText:        { fontSize: fontSize.md, color: colors.text, lineHeight: 20 },
  loadingRow:        { flexDirection: "row", alignItems: "center", gap: spacing.sm },
  loadingText:       { fontSize: fontSize.md, color: colors.textDim },
  inputRow:          { flexDirection: "row", gap: spacing.sm, padding: spacing.md, borderTopWidth: 1, borderTopColor: colors.border, alignItems: "flex-end" },
  sendBtn:           { width: 44, height: 44, borderRadius: radius.md, backgroundColor: colors.ai, alignItems: "center", justifyContent: "center" },
  sendBtnDisabled:   { backgroundColor: colors.border },
});
