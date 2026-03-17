/**
 * User Management screen — admin and manager roles only.
 * Create, list, activate/deactivate users; role assignment.
 */
import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, TextInput, TouchableOpacity,
  ScrollView, ActivityIndicator, Modal,
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
import { styles } from "./UsersScreen.styles";
import { commonStyles as cs } from "../styles/common";

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
      <View style={cs.topRow}>
        <Text style={cs.count}>{users.length} users registered</Text>
        <TouchableOpacity style={styles.addBtn} onPress={openCreate} activeOpacity={0.8}>
          <UserPlus size={14} color={colors.bg} />
          <Text style={styles.addBtnText}>Create User</Text>
        </TouchableOpacity>
      </View>

      {/* Error banner */}
      {!!error && (
        <View style={cs.errorBox}>
          <Text style={cs.errorText}>{error}</Text>
        </View>
      )}

      {/* Loading */}
      {loading
        ? <ActivityIndicator size="large" color={colors.primary} style={{ marginTop: 40 }} />
        : (
          <Card>
            <SectionHeader Icon={Users} title="All Users" color={colors.info} />

            {/* Table header */}
            <View style={[cs.row, styles.tableHead]}>
              <Text style={[styles.col, styles.colName, styles.headText]}>User</Text>
              <Text style={[styles.col, styles.colRole, styles.headText]}>Role</Text>
              <Text style={[styles.col, styles.colStatus, styles.headText]}>Status</Text>
              {isAdmin && <Text style={[styles.col, styles.colAction, styles.headText]}>Action</Text>}
            </View>

            {users.map((u) => (
              <View key={u.id} style={[cs.row, u.id === myUser?.id && styles.rowSelf]}>
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
        <View style={cs.modalOverlayCentered}>
          <View style={cs.modalCard}>
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
                <View style={cs.errorBox}>
                  <Text style={cs.errorText}>{formError}</Text>
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
                  <Text style={cs.label}>{label}</Text>
                  <TextInput
                    style={cs.input}
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
              <Text style={cs.label}>Role *</Text>
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
