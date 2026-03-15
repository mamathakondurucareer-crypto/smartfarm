/**
 * Login screen — authenticates against the FastAPI backend.
 */
import React, { useState } from "react";
import {
  View, Text, TextInput, TouchableOpacity,
  StyleSheet, ActivityIndicator, KeyboardAvoidingView, Platform,
} from "react-native";
import { Leaf, AlertCircle } from "lucide-react-native";
import { colors, spacing, radius, fontSize } from "../config/theme";
import useAuthStore from "../store/useAuthStore";

export default function LoginScreen() {
  const login = useAuthStore((s) => s.login);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) {
      setError("Please enter username and password.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await login(username.trim(), password);
      // NavigationContext will re-render automatically once token is set
    } catch (err) {
      setError(err.message || "Login failed. Check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <View style={styles.card}>
        {/* Brand */}
        <View style={styles.brand}>
          <Leaf size={36} color={colors.primary} />
          <Text style={styles.brandName}>SmartFarm OS</Text>
          <Text style={styles.brandSub}>Integrated Regenerative Farm · Nellore, AP</Text>
        </View>

        {/* Error */}
        {!!error && (
          <View style={styles.errorBox}>
            <AlertCircle size={14} color={colors.danger} />
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        {/* Fields */}
        <Text style={styles.label}>Username</Text>
        <TextInput
          style={styles.input}
          value={username}
          onChangeText={setUsername}
          placeholder="Enter username"
          placeholderTextColor={colors.textMuted}
          autoCapitalize="none"
          autoCorrect={false}
          editable={!loading}
        />

        <Text style={styles.label}>Password</Text>
        <TextInput
          style={styles.input}
          value={password}
          onChangeText={setPassword}
          placeholder="Enter password"
          placeholderTextColor={colors.textMuted}
          secureTextEntry
          editable={!loading}
          onSubmitEditing={handleLogin}
          returnKeyType="go"
        />

        {/* Submit */}
        <TouchableOpacity
          style={[styles.btn, loading && styles.btnDisabled]}
          onPress={handleLogin}
          disabled={loading}
          activeOpacity={0.85}
        >
          {loading
            ? <ActivityIndicator size="small" color={colors.bg} />
            : <Text style={styles.btnText}>Sign In</Text>}
        </TouchableOpacity>

        <Text style={styles.hint}>
          Default admin: <Text style={styles.hintBold}>admin / admin123</Text>
        </Text>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
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
  errorBox: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    backgroundColor: colors.danger + "20",
    borderWidth: 1,
    borderColor: colors.danger + "40",
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  errorText: {
    flex: 1,
    color: colors.danger,
    fontSize: fontSize.md,
  },
  label: {
    fontSize: fontSize.md,
    color: colors.textDim,
    marginBottom: spacing.xs,
    marginTop: spacing.sm,
  },
  input: {
    backgroundColor: colors.bg,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    color: colors.text,
    fontSize: fontSize.base,
    marginBottom: spacing.sm,
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
