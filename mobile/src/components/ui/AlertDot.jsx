import React from "react";
import { View } from "react-native";
import { colors } from "../../config/theme";

const TYPE_COLORS = {
  danger:  colors.danger,
  warning: colors.warn,
  info:    colors.info,
  success: colors.primary,
};

/** Small colored dot indicating alert severity. */
export default function AlertDot({ type, size = 8 }) {
  return (
    <View style={{
      width: size,
      height: size,
      borderRadius: size / 2,
      backgroundColor: TYPE_COLORS[type] ?? colors.info,
      flexShrink: 0,
      marginTop: 3,
    }} />
  );
}
