/**
 * User Management screen — admin and manager roles only.
 * Create, list, activate/deactivate users; role assignment.
 */
import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, TextInput, TouchableOpacity,
  ScrollView, StyleSheet, ActivityIndicator, Modal,
} from "react-native";
import {
  Users, UserPlus, Shield, CheckCircle, XCircle,
  ChevronDown, X,
} from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import Badge         from "../components/ui/Badge";
import { colors, spacing, radius, fontSize } from "../config/theme";
import { api } from "../services/api";
import useAuthStore  from "../store/useAuthStore";

const ROLE_COLORS = {
  ADMIN:      colors.danger,
  MANAGER:    colors.accent,
  SUPERVISOR: colors.info,
  WORKER:     colors.primary,
  VIEWER:     colors.textMuted,
};

const EMPTY_FORM = {
  username: "", email: "", password: "",
  full_name: "", phone: "", role_id: 3,
};

export default function UsersScreen() {
  const token   = useAuthStore((s) => s.token);
  const myUser  = useAuthStore((s) => s.user);
  const isAdmin = myUser?.role === "ADMIN";

  const [users, setUsers]       = useState([]);
  const [roles, setRoles]       = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState("");
  const [modalOpen, setModal]   = useState(false);
  const [form, setForm]         = useState(EMPTY_FORM);
  const [saving, setSaving]     = useState(false);
  const [formError, setFormErr] = useState("");
  const [roleOpen, setRoleOpen] = useState(false);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [u, r] = await Promise.all([api.users.list(token), api.roles(token)]);
      setUsers(u);
      setRoles(r);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const toggleStatus = async (user) => {
    if (!isAdmin) return;
    try {
      await api.users.setStatus(user.id, !user.is_active, token);
      fetchUsers();
    } catch (e) {
      setError(e.message);
    }
  };

  const openCreate = () => {
    setForm(EMPTY_FORM);
    setFormErr("");
    setModal(true);
  };

  const handleCreate = async () => {
    if (!form.username || !form.email || !form.password || !form.full_name) {
      setFormErr("Username, email, password, and full name are required.");
      return;
    }
    setSaving(true);
    setFormErr("");
    try {
      await api.users.create(form, token);
      setModal(false);
      fetchUsers();
    } catch (e) {
      setFormErr(e.message);
    } finally {
      setSaving(false);
    }
  };

  const selectedRole = roles.find((r) => r.id === form.role_id);

  return (
    <ScreenWrapper title="User Management">
      {/* Header row */}
      <View style={styles.topRow}>
        <Text style={styles.count}>{users.length} users registered</Text>
        <TouchableOpacity style={styles.addBtn} onPress={openCreate} activeOpacity={0.8}>
          <UserPlus size={14} color={colors.bg} />
          <Text style={styles.addBtnText}>Create User</Text>
        </TouchableOpacity>
      </View>

      {/* Error banner */}
      {!!error && (
        <View style={styles.errorBox}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* Loading */}
      {loading
        ? <ActivityIndicator size="large" color={colors.primary} style={{ marginTop: 40 }} />
        : (
          <Card>
            <SectionHeader Icon={Users} title="All Users" color={colors.info} />

            {/* Table header */}
            <View style={[styles.row, styles.tableHead]}>
              <Text style={[styles.col, styles.colName, styles.headText]}>User</Text>
              <Text style={[styles.col, styles.colRole, styles.headText]}>Role</Text>
              <Text style={[styles.col, styles.colStatus, styles.headText]}>Status</Text>
              {isAdmin && <Text style={[styles.col, styles.colAction, styles.headText]}>Action</Text>}
            </View>

            {users.map((u) => (
              <View key={u.id} style={[styles.row, u.id === myUser?.id && styles.rowSelf]}>
                <View style={[styles.col, styles.colName]}>
                  <Text style={styles.userName}>{u.full_name}</Text>
                  <Text style={styles.userSub}>@{u.username}</Text>
                  <Text style={styles.userSub}>{u.email}</Text>
                </View>

                <View style={[styles.col, styles.colRole]}>
                  <Badge
                    label={u.role_name ?? String(u.role_id)}
                    color={ROLE_COLORS[(u.role_name ?? "").toUpperCase()] ?? colors.textDim}
                  />
                </View>

                <View style={[styles.col, styles.colStatus]}>
                  {u.is_active
                    ? <CheckCircle size={16} color={colors.primary} />
                    : <XCircle    size={16} color={colors.textMuted} />}
                  <Text style={{ color: u.is_active ? colors.primary : colors.textMuted, fontSize: fontSize.sm, marginTop: 2 }}>
                    {u.is_active ? "Active" : "Inactive"}
                  </Text>
                </View>

                {isAdmin && (
                  <View style={[styles.col, styles.colAction]}>
                    {u.id !== myUser?.id && (
                      <TouchableOpacity
                        onPress={() => toggleStatus(u)}
                        style={[styles.toggleBtn, { borderColor: u.is_active ? colors.danger : colors.primary }]}
                        activeOpacity={0.7}
                      >
                        <Text style={{ color: u.is_active ? colors.danger : colors.primary, fontSize: fontSize.xs, fontWeight: "600" }}>
                          {u.is_active ? "Disable" : "Enable"}
                        </Text>
                      </TouchableOpacity>
                    )}
                  </View>
                )}
              </View>
            ))}
          </Card>
        )}

      {/* Create User Modal */}
      <Modal visible={modalOpen} transparent animationType="fade" onRequestClose={() => setModal(false)}>
        <View style={styles.modalOverlay}>
          <View style={styles.modalCard}>
            {/* Modal header */}
            <View style={styles.modalHeader}>
              <View style={styles.modalTitle}>
                <Shield size={16} color={colors.primary} />
                <Text style={styles.modalTitleText}>Create New User</Text>
              </View>
              <TouchableOpacity onPress={() => setModal(false)} hitSlop={{ top: 8, right: 8, bottom: 8, left: 8 }}>
                <X size={18} color={colors.textDim} />
              </TouchableOpacity>
            </View>

            <ScrollView showsVerticalScrollIndicator={false}>
              {!!formError && (
                <View style={styles.errorBox}>
                  <Text style={styles.errorText}>{formError}</Text>
                </View>
              )}

              {[
                { key: "full_name",  label: "Full Name *" },
                { key: "username",   label: "Username *",  auto: "none" },
                { key: "email",      label: "Email *",     auto: "none", keyboard: "email-address" },
                { key: "phone",      label: "Phone",       keyboard: "phone-pad" },
                { key: "password",   label: "Password *",  secure: true },
              ].map(({ key, label, auto, keyboard, secure }) => (
                <View key={key}>
                  <Text style={styles.label}>{label}</Text>
                  <TextInput
                    style={styles.input}
                    value={form[key]}
                    onChangeText={(v) => setForm((f) => ({ ...f, [key]: v }))}
                    placeholder={label.replace(" *", "")}
                    placeholderTextColor={colors.textMuted}
                    autoCapitalize={auto ?? "words"}
                    keyboardType={keyboard ?? "default"}
                    secureTextEntry={!!secure}
                  />
                </View>
              ))}

              {/* Role picker */}
              <Text style={styles.label}>Role *</Text>
              <TouchableOpacity style={styles.rolePicker} onPress={() => setRoleOpen((v) => !v)} activeOpacity={0.8}>
                <Text style={{ color: colors.text, fontSize: fontSize.base }}>
                  {selectedRole?.name ?? "Select role"}
                </Text>
                <ChevronDown size={14} color={colors.textDim} />
              </TouchableOpacity>
              {roleOpen && (
                <View style={styles.roleList}>
                  {roles.map((r) => (
                    <TouchableOpacity
                      key={r.id}
                      style={[styles.roleItem, r.id === form.role_id && styles.roleItemActive]}
                      onPress={() => { setForm((f) => ({ ...f, role_id: r.id })); setRoleOpen(false); }}
                    >
                      <Text style={{ color: r.id === form.role_id ? colors.primary : colors.textDim, fontSize: fontSize.md }}>
                        {r.name}
                      </Text>
                      {r.description && <Text style={styles.roleDesc}>{r.description}</Text>}
                    </TouchableOpacity>
                  ))}
                </View>
              )}

              {/* Save */}
              <TouchableOpacity
                style={[styles.saveBtn, saving && { opacity: 0.6 }]}
                onPress={handleCreate}
                disabled={saving}
                activeOpacity={0.85}
              >
                {saving
                  ? <ActivityIndicator size="small" color={colors.bg} />
                  : <Text style={styles.saveBtnText}>Create User</Text>}
              </TouchableOpacity>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  topRow:    { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.md },
  count:     { fontSize: fontSize.md, color: colors.textDim },
  addBtn:    { flexDirection: "row", alignItems: "center", gap: spacing.xs, backgroundColor: colors.primary, borderRadius: radius.md, paddingHorizontal: spacing.md, paddingVertical: spacing.sm },
  addBtnText:{ color: colors.bg, fontSize: fontSize.md, fontWeight: "700" },
  errorBox:  { backgroundColor: colors.danger + "20", borderWidth: 1, borderColor: colors.danger + "40", borderRadius: radius.md, padding: spacing.md, marginBottom: spacing.md },
  errorText: { color: colors.danger, fontSize: fontSize.md },
  tableHead: { backgroundColor: colors.bg, borderRadius: radius.sm, marginBottom: spacing.xs },
  headText:  { fontSize: fontSize.xs, color: colors.textMuted, fontWeight: "600", textTransform: "uppercase" },
  row:       { flexDirection: "row", paddingVertical: spacing.md, borderBottomWidth: 1, borderBottomColor: colors.border + "40", alignItems: "flex-start" },
  rowSelf:   { backgroundColor: colors.primary + "08" },
  col:       { paddingHorizontal: spacing.xs },
  colName:   { flex: 3 },
  colRole:   { flex: 2, alignItems: "flex-start" },
  colStatus: { flex: 2, alignItems: "center" },
  colAction: { flex: 2, alignItems: "center" },
  userName:  { fontSize: fontSize.md, color: colors.text, fontWeight: "600" },
  userSub:   { fontSize: fontSize.xs, color: colors.textMuted, marginTop: 1 },
  toggleBtn: { borderWidth: 1, borderRadius: radius.sm, paddingHorizontal: spacing.sm, paddingVertical: 3 },

  // Modal
  modalOverlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.7)", justifyContent: "center", alignItems: "center", padding: spacing.xl },
  modalCard:    { backgroundColor: colors.card, borderRadius: radius.xl, borderWidth: 1, borderColor: colors.border, padding: spacing.xl, width: "100%", maxWidth: 480, maxHeight: "90%" },
  modalHeader:  { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.lg },
  modalTitle:   { flexDirection: "row", alignItems: "center", gap: spacing.sm },
  modalTitleText:{ fontSize: fontSize.lg, fontWeight: "700", color: colors.text },
  label:     { fontSize: fontSize.md, color: colors.textDim, marginBottom: spacing.xs, marginTop: spacing.sm },
  input:     { backgroundColor: colors.bg, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, padding: spacing.md, color: colors.text, fontSize: fontSize.base, marginBottom: spacing.xs },
  rolePicker:{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", backgroundColor: colors.bg, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, padding: spacing.md },
  roleList:  { backgroundColor: colors.bg, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, marginTop: 2, overflow: "hidden" },
  roleItem:  { padding: spacing.md, borderBottomWidth: 1, borderBottomColor: colors.border + "40" },
  roleItemActive: { backgroundColor: colors.primary + "15" },
  roleDesc:  { fontSize: fontSize.xs, color: colors.textMuted, marginTop: 2 },
  saveBtn:   { backgroundColor: colors.primary, borderRadius: radius.md, padding: spacing.md, alignItems: "center", marginTop: spacing.xl, height: 48, justifyContent: "center" },
  saveBtnText:{ color: colors.bg, fontSize: fontSize.base, fontWeight: "700" },
});
