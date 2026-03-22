import { StyleSheet } from "react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";

export const styles = StyleSheet.create({
  tabBarContent: { paddingHorizontal: 8, alignItems: "center" },
  content:       { padding: 12, paddingBottom: 40 },
  error:         { color: colors.danger, marginBottom: 8, fontSize: 13 },
  empty:         { color: colors.textDim, textAlign: "center", padding: 16, fontSize: 13 },
  rowLeft:       { flex: 1 },
  rowTitle:      { color: colors.text, fontSize: 14, fontWeight: "600" },
  rowSub:        { color: colors.textDim, fontSize: 12, marginTop: 2 },
  rowActions:    { flexDirection: "row", alignItems: "center", marginLeft: 8 },
  suffRow:       { flexDirection: "row", gap: 12, marginTop: 8 },
  suffBox:       { flex: 1, borderRadius: 8, padding: 16, alignItems: "center" },
  suffPct:       { fontSize: 24, fontWeight: "700", color: colors.text },
  suffLabel:     { fontSize: 12, color: colors.textDim, marginTop: 4 },
  overlay:       { flex: 1, backgroundColor: "rgba(0,0,0,0.6)", justifyContent: "center", alignItems: "center", padding: 24 },
  sheet:         { backgroundColor: colors.card, borderRadius: 16, borderWidth: 1, borderColor: colors.border, width: "100%", maxWidth: 560, maxHeight: "90%", paddingBottom: 24 },
  sheetHeader:   { flexDirection: "row", justifyContent: "space-between", alignItems: "center", padding: 16, borderBottomWidth: 1, borderBottomColor: colors.border },
  sheetTitle:    { fontSize: 16, fontWeight: "700", color: colors.text },
  sheetBody:     { padding: 16 },
  field:         { marginBottom: 14 },
  fieldLabel:    { color: colors.textDim, fontSize: 12, marginBottom: 4 },
  inputMulti:    { minHeight: 80, textAlignVertical: "top" },
  saveBtn:       { backgroundColor: colors.primary, padding: 14, borderRadius: 8, alignItems: "center", marginTop: 8 },
  saveBtnText:   { color: "#fff", fontWeight: "700", fontSize: 15 },
});
