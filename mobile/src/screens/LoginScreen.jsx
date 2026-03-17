/**
 * Login screen — authenticates against the FastAPI backend.
 */
import React, { useState } from "react";
import {
  View, Text, TextInput, TouchableOpacity,
  ActivityIndicator, KeyboardAvoidingView, Platform,
} from "react-native";
import { Leaf, AlertCircle } from "lucide-react-native";
import { colors } from "../config/theme";
import useAuthStore from "../store/useAuthStore";
import { styles } from "./LoginScreen.styles";
import { commonStyles as cs } from "../styles/common";

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
          <View style={cs.errorBox}>
            <AlertCircle size={14} color={colors.danger} />
            <Text style={cs.errorText}>{error}</Text>
          </View>
        )}

        {/* Fields */}
        <Text style={cs.label}>Username</Text>
        <TextInput
          style={cs.input}
          value={username}
          onChangeText={setUsername}
          placeholder="Enter username"
          placeholderTextColor={colors.textMuted}
          autoCapitalize="none"
          autoCorrect={false}
          editable={!loading}
        />

        <Text style={cs.label}>Password</Text>
        <TextInput
          style={cs.input}
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
