/**
 * Service Requests — maintenance and repair request management.
 */
import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, TouchableOpacity, ScrollView, Modal, TextInput,
  ActivityIndicator,
} from "react-native";
import { Wrench, Plus, X, AlertTriangle } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import StatGrid      from "../components/ui/StatGrid";
import Badge         from "../components/ui/Badge";
import { colors, spacing, fontSize } from "../config/theme";
import { api }       from "../services/api";
import useAuthStore  from "../store/useAuthStore";
import { styles } from "./ServiceRequestsScreen.styles";
import { commonStyles as cs } from "../styles/common";

const PRIORITY_COLORS = { urgent: colors.danger, high: colors.warn, medium: colors.info, low: colors.textDim };
const STATUS_COLORS   = { open: colors.info, assigned: colors.accent, in_progress: colors.warn, pending_parts: colors.poultry, resolved: colors.primary, closed: colors.textMuted };
const CATEGORIES = ["maintenance", "repair", "installation", "cleaning", "inspection"];
const PRIORITIES = ["low", "medium", "high", "urgent"];
const DEPARTMENTS = ["aquaculture", "greenhouse", "poultry", "store", "packhouse", "maintenance", "management"];

const EMPTY_FORM = { title: "", description: "", department: "maintenance", category: "maintenance", priority: "medium", location: "", affected_equipment: "" };

export default function ServiceRequestsScreen() {
  const token = useAuthStore((s) => s.token);
  const [requests, setRequests] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState("");
  const [modalOpen, setModal]   = useState(false);
  const [form, setForm]         = useState(EMPTY_FORM);
  const [saving, setSaving]     = useState(false);
  const [formErr, setFormErr]   = useState("");

  const fetchData = useCallback(async () => {
    setLoading(true); setError("");
    try { setRequests(await api.serviceRequests.list(token)); }
    catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const openCount    = requests.filter((r) => r.status === "open").length;
  const inProgress   = requests.filter((r) => r.status === "in_progress" || r.status === "assigned").length;
  const resolved     = requests.filter((r) => r.status === "resolved" || r.status === "closed").length;
  const urgentCount  = requests.filter((r) => r.priority === "urgent" && r.status !== "resolved" && r.status !== "closed").length;

  const stats = [
    { Icon: Wrench,        label: "Open",        value: String(openCount),   color: colors.info },
    { Icon: Wrench,        label: "In Progress", value: String(inProgress),  color: colors.warn },
    { Icon: Wrench,        label: "Resolved",    value: String(resolved),    color: colors.primary },
    { Icon: AlertTriangle, label: "Urgent",      value: String(urgentCount), color: colors.danger },
  ];

  const handleCreate = async () => {
    if (!form.title || !form.description) { setFormErr("Title and description required."); return; }
    setSaving(true); setFormErr("");
    try {
      await api.serviceRequests.create(form, token);
      setModal(false); fetchData();
    } catch (e) { setFormErr(e.message); }
    finally { setSaving(false); }
  };

  return (
    <ScreenWrapper title="Service Requests">
      <StatGrid stats={stats} />
      <View style={{ height: spacing.lg }} />

      <View style={styles.topRow}>
        <Text style={styles.count}>{requests.length} requests</Text>
        <TouchableOpacity style={styles.addBtn} onPress={() => { setForm(EMPTY_FORM); setFormErr(""); setModal(true); }} activeOpacity={0.8}>
          <Plus size={14} color={colors.bg} />
          <Text style={styles.addBtnText}>New Request</Text>
        </TouchableOpacity>
      </View>

      {!!error && <View style={cs.errorBox}><Text style={cs.errorText}>{error}</Text></View>}

      {loading ? <ActivityIndicator size="large" color={colors.primary} style={{ marginTop: 40 }} /> : (
        <Card>
          <SectionHeader Icon={Wrench} title="All Requests" color={colors.service} />
          {requests.length === 0 ? (
            <Text style={styles.empty}>No service requests.</Text>
          ) : requests.map((r) => (
            <View key={r.id} style={styles.row}>
              <View style={{ flex: 4 }}>
                <Text style={styles.reqTitle}>{r.title}</Text>
                <Text style={styles.reqMeta}>{r.category} • {r.department} • {r.location || "N/A"}</Text>
              </View>
              <View style={{ flex: 2, alignItems: "center" }}>
                <Badge label={r.priority} color={PRIORITY_COLORS[r.priority]} />
              </View>
              <View style={{ flex: 2, alignItems: "center" }}>
                <Badge label={r.status.replace("_", " ")} color={STATUS_COLORS[r.status] ?? colors.textDim} />
              </View>
            </View>
          ))}
        </Card>
      )}

      {/* Create Request Modal */}
      <Modal visible={modalOpen} transparent animationType="fade" onRequestClose={() => setModal(false)}>
        <View style={cs.modalOverlay}>
          <View style={cs.modalCard}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitleText}>New Service Request</Text>
              <TouchableOpacity onPress={() => setModal(false)}><X size={18} color={colors.textDim} /></TouchableOpacity>
            </View>
            <ScrollView showsVerticalScrollIndicator={false}>
              {!!formErr && <View style={cs.errorBox}><Text style={cs.errorText}>{formErr}</Text></View>}

              <Text style={cs.label}>Title *</Text>
              <TextInput style={cs.input} value={form.title} onChangeText={(v) => setForm((f) => ({ ...f, title: v }))} placeholder="Brief title" placeholderTextColor={colors.textMuted} />

              <Text style={cs.label}>Description *</Text>
              <TextInput style={[cs.input, { minHeight: 80 }]} value={form.description} onChangeText={(v) => setForm((f) => ({ ...f, description: v }))} placeholder="Detailed description" placeholderTextColor={colors.textMuted} multiline />

              <Text style={cs.label}>Priority</Text>
              <View style={styles.chipRow}>
                {PRIORITIES.map((p) => (
                  <TouchableOpacity key={p} style={[styles.chip, form.priority === p && { borderColor: PRIORITY_COLORS[p], backgroundColor: PRIORITY_COLORS[p] + "15" }]} onPress={() => setForm((f) => ({ ...f, priority: p }))}>
                    <Text style={{ color: form.priority === p ? PRIORITY_COLORS[p] : colors.textDim, fontSize: fontSize.sm }}>{p}</Text>
                  </TouchableOpacity>
                ))}
              </View>

              <Text style={cs.label}>Category</Text>
              <View style={styles.chipRow}>
                {CATEGORIES.map((c) => (
                  <TouchableOpacity key={c} style={[styles.chip, form.category === c && styles.chipActive]} onPress={() => setForm((f) => ({ ...f, category: c }))}>
                    <Text style={{ color: form.category === c ? colors.primary : colors.textDim, fontSize: fontSize.sm }}>{c}</Text>
                  </TouchableOpacity>
                ))}
              </View>

              <Text style={cs.label}>Department</Text>
              <View style={styles.chipRow}>
                {DEPARTMENTS.map((d) => (
                  <TouchableOpacity key={d} style={[styles.chip, form.department === d && styles.chipActive]} onPress={() => setForm((f) => ({ ...f, department: d }))}>
                    <Text style={{ color: form.department === d ? colors.primary : colors.textDim, fontSize: fontSize.sm }}>{d}</Text>
                  </TouchableOpacity>
                ))}
              </View>

              <Text style={cs.label}>Location</Text>
              <TextInput style={cs.input} value={form.location} onChangeText={(v) => setForm((f) => ({ ...f, location: v }))} placeholder="e.g. Pond A3, GH-1" placeholderTextColor={colors.textMuted} />

              <Text style={cs.label}>Affected Equipment</Text>
              <TextInput style={cs.input} value={form.affected_equipment} onChangeText={(v) => setForm((f) => ({ ...f, affected_equipment: v }))} placeholder="e.g. Aerator #2" placeholderTextColor={colors.textMuted} />

              <TouchableOpacity style={[styles.saveBtn, saving && { opacity: 0.6 }]} onPress={handleCreate} disabled={saving} activeOpacity={0.85}>
                {saving ? <ActivityIndicator size="small" color={colors.bg} /> : <Text style={styles.saveBtnText}>Submit Request</Text>}
              </TouchableOpacity>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </ScreenWrapper>
  );
}
