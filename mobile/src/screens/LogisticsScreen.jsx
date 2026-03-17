/**
 * Logistics — delivery trip management, route tracking, driver dispatch.
 */
import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, TouchableOpacity, ScrollView, Modal, TextInput,
  ActivityIndicator,
} from "react-native";
import { Truck, Plus, X, MapPin } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import StatGrid      from "../components/ui/StatGrid";
import Badge         from "../components/ui/Badge";
import { colors, spacing, radius, fontSize } from "../config/theme";
import { api }       from "../services/api";
import useAuthStore  from "../store/useAuthStore";
import { styles } from "./LogisticsScreen.styles";
import { commonStyles as cs } from "../styles/common";

const STATUS_COLORS = {
  scheduled: colors.info, loading: colors.warn,
  in_transit: colors.accent, delivered: colors.primary, returned: colors.textMuted,
};
const VEHICLE_TYPES = ["bike", "auto", "tempo", "truck", "refrigerated_truck"];

export default function LogisticsScreen() {
  const token = useAuthStore((s) => s.token);
  const [trips, setTrips]       = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState("");
  const [modalOpen, setModal]   = useState(false);
  const [form, setForm]         = useState({ vehicle_number: "", vehicle_type: "tempo", driver_id: "" });
  const [saving, setSaving]     = useState(false);

  const fetchTrips = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const response = await api.logistics.trips.list(token);
      setTrips(Array.isArray(response) ? response : []);
    }
    catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchTrips(); }, [fetchTrips]);

  const scheduled  = trips.filter((t) => t.status === "scheduled").length;
  const inTransit  = trips.filter((t) => t.status === "in_transit").length;
  const delivered  = trips.filter((t) => t.status === "delivered").length;

  const stats = [
    { Icon: Truck,  label: "Scheduled",  value: String(scheduled),  color: colors.info },
    { Icon: MapPin, label: "In Transit", value: String(inTransit),  color: colors.accent },
    { Icon: Truck,  label: "Delivered",  value: String(delivered),  color: colors.primary },
    { Icon: Truck,  label: "Total",      value: String(trips.length), color: colors.logistics },
  ];

  const updateStatus = async (trip, newStatus) => {
    try {
      await api.logistics.trips.status(trip.id, { status: newStatus }, token);
      fetchTrips();
    } catch (e) { setError(e.message); }
  };

  const handleCreate = async () => {
    if (!form.vehicle_number || !form.driver_id) return;
    setSaving(true);
    try {
      await api.logistics.trips.create({ ...form, driver_id: parseInt(form.driver_id) }, token);
      setModal(false); fetchTrips();
    } catch (e) { setError(e.message); }
    finally { setSaving(false); }
  };

  const nextStatus = { scheduled: "loading", loading: "in_transit", in_transit: "delivered" };

  return (
    <ScreenWrapper title="Logistics">
      <StatGrid stats={stats} />
      <View style={{ height: spacing.lg }} />

      <View style={cs.topRow}>
        <Text style={cs.count}>{trips.length} trips</Text>
        <TouchableOpacity style={styles.addBtn} onPress={() => setModal(true)} activeOpacity={0.8}>
          <Plus size={14} color={colors.bg} />
          <Text style={styles.addBtnText}>New Trip</Text>
        </TouchableOpacity>
      </View>

      {!!error && <View style={cs.errorBox}><Text style={cs.errorText}>{error}</Text></View>}

      {loading ? <ActivityIndicator size="large" color={colors.primary} style={{ marginTop: 40 }} /> : (
        <Card>
          <SectionHeader Icon={Truck} title="Delivery Trips" color={colors.logistics} />
          {trips.length === 0 ? (
            <Text style={cs.empty}>No delivery trips yet.</Text>
          ) : trips.map((t) => (
            <View key={t.id} style={cs.row}>
              <View style={{ flex: 3 }}>
                <Text style={styles.tripCode}>{t.trip_code}</Text>
                <Text style={styles.tripMeta}>{t.vehicle_type} • {t.vehicle_number}</Text>
              </View>
              <View style={{ flex: 2, alignItems: "center" }}>
                <Badge label={t.status} color={STATUS_COLORS[t.status] ?? colors.textDim} />
              </View>
              <View style={{ flex: 2, alignItems: "center" }}>
                {nextStatus[t.status] && (
                  <TouchableOpacity
                    style={[styles.actionBtn, { borderColor: STATUS_COLORS[nextStatus[t.status]] }]}
                    onPress={() => updateStatus(t, nextStatus[t.status])}
                    activeOpacity={0.7}
                  >
                    <Text style={{ color: STATUS_COLORS[nextStatus[t.status]], fontSize: fontSize.xs, fontWeight: "600" }}>
                      {nextStatus[t.status].replace("_", " ").toUpperCase()}
                    </Text>
                  </TouchableOpacity>
                )}
              </View>
            </View>
          ))}
        </Card>
      )}

      {/* Create Trip Modal */}
      <Modal visible={modalOpen} transparent animationType="fade" onRequestClose={() => setModal(false)}>
        <View style={cs.modalOverlayCentered}>
          <View style={cs.modalCard}>
            <View style={styles.modalHeader}>
              <Text style={cs.modalTitle}>New Delivery Trip</Text>
              <TouchableOpacity onPress={() => setModal(false)}><X size={18} color={colors.textDim} /></TouchableOpacity>
            </View>
            <Text style={cs.label}>Driver Employee ID *</Text>
            <TextInput style={cs.input} value={form.driver_id} onChangeText={(v) => setForm((f) => ({ ...f, driver_id: v }))} placeholder="e.g. 1" placeholderTextColor={colors.textMuted} keyboardType="numeric" />
            <Text style={cs.label}>Vehicle Number *</Text>
            <TextInput style={cs.input} value={form.vehicle_number} onChangeText={(v) => setForm((f) => ({ ...f, vehicle_number: v }))} placeholder="AP-01-AB-1234" placeholderTextColor={colors.textMuted} />
            <Text style={cs.label}>Vehicle Type</Text>
            <View style={styles.typeRow}>
              {VEHICLE_TYPES.map((vt) => (
                <TouchableOpacity key={vt} style={[styles.typeChip, form.vehicle_type === vt && styles.typeChipActive]} onPress={() => setForm((f) => ({ ...f, vehicle_type: vt }))}>
                  <Text style={{ color: form.vehicle_type === vt ? colors.primary : colors.textDim, fontSize: fontSize.sm }}>{vt}</Text>
                </TouchableOpacity>
              ))}
            </View>
            <TouchableOpacity style={[styles.saveBtn, saving && { opacity: 0.6 }]} onPress={handleCreate} disabled={saving} activeOpacity={0.85}>
              {saving ? <ActivityIndicator size="small" color={colors.bg} /> : <Text style={styles.saveBtnText}>Create Trip</Text>}
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </ScreenWrapper>
  );
}
