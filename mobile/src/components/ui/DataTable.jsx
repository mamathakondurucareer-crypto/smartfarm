import React from "react";
import { View, Text, ScrollView, StyleSheet } from "react-native";
import { colors, fontSize, spacing } from "../../config/theme";

/**
 * A scrollable data table.
 *
 * @param {string[]}   headers  — column header labels
 * @param {any[][]}    rows     — 2D array; cells can be strings or React elements
 */
export default function DataTable({ headers, rows }) {
  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false}>
      <View>
        {/* Header row */}
        <View style={styles.headerRow}>
          {headers.map((h, i) => (
            <Text key={i} style={[styles.headerCell, i === 0 ? styles.left : styles.right, i !== 0 && styles.headerCenterText]}>
              {h}
            </Text>
          ))}
        </View>

        {/* Data rows */}
        {rows.map((row, ri) => (
          <View key={ri} style={[styles.dataRow, ri % 2 === 1 && styles.altRow]}>
            {row.map((cell, ci) => (
              <View key={ci} style={[styles.dataCell, ci === 0 ? styles.left : styles.right]}>
                {typeof cell === "string" || typeof cell === "number"
                  ? <Text style={[styles.cellText, ci !== 0 && styles.headerCenterText]}>{cell}</Text>
                  : cell}
              </View>
            ))}
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const CELL_MIN_WIDTH = 90;

const styles = StyleSheet.create({
  headerRow: {
    flexDirection: "row",
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingBottom: spacing.sm,
    marginBottom: 2,
  },
  headerCell: {
    minWidth: CELL_MIN_WIDTH,
    paddingHorizontal: spacing.sm,
    fontSize: fontSize.sm,
    fontWeight: "600",
    color: colors.textDim,
  },
  dataRow: {
    flexDirection: "row",
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: colors.border + "40",
  },
  altRow: {
    backgroundColor: colors.bg + "60",
  },
  dataCell: {
    minWidth: CELL_MIN_WIDTH,
    paddingHorizontal: spacing.sm,
    justifyContent: "center",
  },
  cellText: {
    fontSize: fontSize.md,
    color: colors.text,
  },
  left:           { alignItems: "flex-start" },
  right:          { alignItems: "center" },
  headerCenterText: { textAlign: "center" },
});
