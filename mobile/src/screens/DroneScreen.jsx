import React, { useState, useCallback, useEffect } from "react";
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  Modal, TextInput, ActivityIndicator, RefreshControl,
} from "react-native";
import { Plane, MapPin, Droplets, Plus, Edit2, Trash2, X } from "lucide-react-native";
import useAuthStore from "../store/useAuthStore";
import { api } from "../services/api";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import { colors } from "../config/theme";

const TABS = ["Drones", "Flights", "Spray Logs"];

export default function DroneScreen() {
  const token = useAuthStore((s) => s.token);
  const user = useAuthStore((s) => s.user);
  const canEdit = user?.role && ["ADMIN", "MANAGER", "SUPERVISOR"].includes(user.role);

  const [activeTab, setActiveTab] = useState("Drones");
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState({ drones: [], flights: [], sprays: [] });
  const [modal, setModal] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [form, setForm] = useState({});
  const [saving, setSaving] = useState(false);

  const fetchAll = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const [drones, flights, sprays] = await Promise.all([
        api.drones.list(token),
        api.drones.flights.list(token),
        api.drones.sprays.list(token),
      ]);
      setData({ drones, flights, sprays });
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [token]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const openCreate = () => {
    const defaults = {
      Drones: { drone_code: "", name: "", drone_type: "spray", battery_health_pct: "100", last_maintenance: "", status: "ready" },
      Flights: { drone_id: "", flight_date: new Date().toISOString().split("T")[0], mission_type: "survey", area_covered_ha: "0", duration_mins: "0", pilot: "", zone: "" },
      "Spray Logs": { flight_id: "", agent_name: "", agent_type: "bio", dosage_per_ha: "0", total_volume_l: "0" },
    };
    setEditItem(null);
    setForm(defaults[activeTab] || {});
    setModal(true);
  };

  const openEdit = (item) => {
    const f = {};
    Object.keys(item).forEach((k) => {
      f[k] = String(item[k] ?? "");
    });
    setEditItem(item);
    setForm(f);
    setModal(true);
  };

  const handleSave = async () => {
    setSaving(true);
    setError("");
    try {
      const numKeys = ["battery_health_pct", "total_flight_hours", "area_covered_ha", "duration_mins", "ndvi_score", "dosage_per_ha", "total_volume_l"];
      const payload = { ...form };
      numKeys.forEach((k) => {
        if (payload[k] !== undefined) payload[k] = Number(payload[k]);
      });
      if (payload.drone_id !== undefined) payload.drone_id = Number(payload.drone_id);
      if (payload.flight_id !== undefined) payload.flight_id = Number(payload.flight_id);

      if (activeTab === "Drones") {
        if (editItem) await api.drones.update(editItem.id, payload, token);
        else await api.drones.create(payload, token);
      } else if (activeTab === "Flights") {
        await api.drones.flights.create(payload, token);
      } else if (activeTab === "Spray Logs") {
        await api.drones.sprays.create(payload, token);
      }
      setModal(false);
      fetchAll();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (item) => {
    try {
      if (activeTab === "Drones") await api.drones.delete(item.id, token);
      else if (activeTab === "Flights") await api.drones.flights.delete(item.id, token);
      fetchAll();
    } catch (e) {
      setError(e.message);
    }
  };

  const getDroneNameById = (droneId) => {
    const drone = data.drones.find((d) => d.id === droneId);
    return drone ? `${drone.drone_code} (${drone.name})` : `Drone #${droneId}`;
  };

  const renderContent = () => {
    if (loading) return <ActivityIndicator color={colors.primary} style={{ marginTop: 40 }} />;
    switch (activeTab) {
      case "Drones":
        return (
          <Card>
            <SectionHeader Icon={Plane} title={`Drones (${data.drones.length})`} action={canEdit && <TouchableOpacity onPress={openCreate}><Plus size={18} color={colors.primary} /></TouchableOpacity>} />
            {data.drones.length === 0 && <Text style={styles.empty}>No drones registered</Text>}
            {data.drones.map((d) => (
              <View key={d.id} style={styles.row}>
                <View style={styles.rowLeft}>
                  <Text style={styles.rowTitle}>{d.drone_code}</Text>
                  <Text style={styles.rowSub}>{d.name} • Type: {d.drone_type}</Text>
                  <Text style={styles.rowSub}>Battery: {d.battery_health_pct}% • Status: {d.status}</Text>
                  <Text style={styles.rowSub}>Flight Hours: {d.total_flight_hours} h{d.last_maintenance ? ` • Last Maint: ${d.last_maintenance}` : ""}</Text>
                </View>
                {canEdit && (
                  <View style={styles.rowActions}>
                    <TouchableOpacity onPress={() => openEdit(d)}><Edit2 size={16} color={colors.textDim} /></TouchableOpacity>
                    <TouchableOpacity onPress={() => handleDelete(d)} style={{ marginLeft: 8 }}><Trash2 size={16} color={colors.danger} /></TouchableOpacity>
                  </View>
                )}
              </View>
            ))}
          </Card>
        );
      case "Flights":
        return (
          <Card>
            <SectionHeader Icon={MapPin} title={`Flight Logs (${data.flights.length})`} action={canEdit && <TouchableOpacity onPress={openCreate}><Plus size={18} color={colors.primary} /></TouchableOpacity>} />
            {data.flights.length === 0 && <Text style={styles.empty}>No flight logs</Text>}
            {data.flights.map((f) => (
              <View key={f.id} style={styles.row}>
                <View style={styles.rowLeft}>
                  <Text style={styles.rowTitle}>{f.flight_date} • {getDroneNameById(f.drone_id)}</Text>
                  <Text style={styles.rowSub}>Mission: {f.mission_type} • Pilot: {f.pilot}</Text>
                  <Text style={styles.rowSub}>Area: {f.area_covered_ha} ha • Duration: {f.duration_mins} min{f.zone ? ` • Zone: ${f.zone}` : ""}</Text>
                  {f.ndvi_score !== null && f.ndvi_score !== undefined && <Text style={styles.rowSub}>NDVI Score: {f.ndvi_score}</Text>}
                </View>
                {canEdit && (
                  <TouchableOpacity onPress={() => handleDelete(f)}><Trash2 size={16} color={colors.danger} /></TouchableOpacity>
                )}
              </View>
            ))}
          </Card>
        );
      case "Spray Logs":
        return (
          <Card>
            <SectionHeader Icon={Droplets} title={`Spray Logs (${data.sprays.length})`} action={canEdit && <TouchableOpacity onPress={openCreate}><Plus size={18} color={colors.primary} /></TouchableOpacity>} />
            {data.sprays.length === 0 && <Text style={styles.empty}>No spray logs</Text>}
            {data.sprays.map((s) => (
              <View key={s.id} style={styles.row}>
                <View style={styles.rowLeft}>
                  <Text style={styles.rowTitle}>{s.agent_name}</Text>
                  <Text style={styles.rowSub}>Type: {s.agent_type} • Flight ID: {s.flight_id}</Text>
                  <Text style={styles.rowSub}>Dosage: {s.dosage_per_ha} kg/ha • Volume: {s.total_volume_l} L</Text>
                  {s.gps_zone_coords && <Text style={styles.rowSub}>GPS Coords: {s.gps_zone_coords.substring(0, 30)}...</Text>}
                </View>
              </View>
            ))}
          </Card>
        );
      default:
        return null;
    }
  };

  const formFields = {
    Drones: [
      { key: "drone_code", label: "Drone Code", edit: false },
      { key: "name", label: "Drone Name" },
      { key: "drone_type", label: "Type (spray/survey/multi)" },
      { key: "battery_health_pct", label: "Battery Health %", numeric: true },
      { key: "status", label: "Status (ready/in_flight/maintenance/retired)" },
      { key: "last_maintenance", label: "Last Maintenance (YYYY-MM-DD)" },
      { key: "notes", label: "Notes", multiline: true },
    ],
    Flights: [
      { key: "drone_id", label: "Drone ID", numeric: true },
      { key: "flight_date", label: "Flight Date (YYYY-MM-DD)" },
      { key: "mission_type", label: "Mission Type (spray/survey/ndvi/inspection)" },
      { key: "area_covered_ha", label: "Area Covered (ha)", numeric: true },
      { key: "duration_mins", label: "Duration (minutes)", numeric: true },
      { key: "pilot", label: "Pilot Name" },
      { key: "zone", label: "Zone / Location" },
      { key: "ndvi_score", label: "NDVI Score (0-1, optional)", numeric: true },
      { key: "notes", label: "Notes", multiline: true },
    ],
    "Spray Logs": [
      { key: "flight_id", label: "Flight ID", numeric: true },
      { key: "agent_name", label: "Agent Name" },
      { key: "agent_type", label: "Agent Type (bio/chemical/fertiliser)" },
      { key: "dosage_per_ha", label: "Dosage (kg/ha)", numeric: true },
      { key: "total_volume_l", label: "Total Volume (L)", numeric: true },
      { key: "gps_zone_coords", label: "GPS Zone Coords (JSON, optional)", multiline: true },
      { key: "notes", label: "Notes", multiline: true },
    ],
  };

  return (
    <ScreenWrapper title="Drone Management">
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tabBar} contentContainerStyle={styles.tabBarContent}>
        {TABS.map((t) => (
          <TouchableOpacity key={t} style={[styles.tab, activeTab === t && styles.tabActive]} onPress={() => setActiveTab(t)}>
            <Text style={[styles.tabText, activeTab === t && styles.tabTextActive]}>{t}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <ScrollView
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetchAll(); }} />}
        contentContainerStyle={styles.content}
      >
        {error ? <Text style={styles.error}>{error}</Text> : null}
        {renderContent()}
      </ScrollView>

      <Modal visible={modal} transparent animationType="slide">
        <View style={styles.overlay}>
          <View style={styles.sheet}>
            <View style={styles.sheetHeader}>
              <Text style={styles.sheetTitle}>{editItem ? `Edit ${activeTab}` : `Add ${activeTab}`}</Text>
              <TouchableOpacity onPress={() => setModal(false)}><X size={20} color={colors.text} /></TouchableOpacity>
            </View>
            <ScrollView style={styles.sheetBody}>
              {error ? <Text style={styles.error}>{error}</Text> : null}
              {(formFields[activeTab] || []).map((f) => {
                if (f.edit === false && editItem) return null;
                return (
                  <View key={f.key} style={styles.field}>
                    <Text style={styles.fieldLabel}>{f.label}</Text>
                    <TextInput
                      style={[styles.input, f.multiline && styles.inputMulti]}
                      value={String(form[f.key] ?? "")}
                      onChangeText={(v) => setForm((prev) => ({ ...prev, [f.key]: v }))}
                      keyboardType={f.numeric ? "numeric" : "default"}
                      multiline={f.multiline}
                    />
                  </View>
                );
              })}
              <TouchableOpacity style={[styles.saveBtn, saving && { opacity: 0.6 }]} onPress={handleSave} disabled={saving}>
                <Text style={styles.saveBtnText}>{saving ? "Saving..." : "Save"}</Text>
              </TouchableOpacity>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  tabBar: { backgroundColor: colors.card, maxHeight: 48 },
  tabBarContent: { paddingHorizontal: 8, alignItems: "center" },
  tab: { paddingHorizontal: 14, paddingVertical: 12, marginHorizontal: 2 },
  tabActive: { borderBottomWidth: 2, borderBottomColor: colors.primary },
  tabText: { fontSize: 13, color: colors.textDim },
  tabTextActive: { color: colors.primary, fontWeight: "600" },
  content: { padding: 12, paddingBottom: 40 },
  error: { color: colors.danger, marginBottom: 8, fontSize: 13 },
  empty: { color: colors.textDim, textAlign: "center", padding: 16, fontSize: 13 },
  row: { flexDirection: "row", alignItems: "flex-start", justifyContent: "space-between", paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: colors.border },
  rowLeft: { flex: 1 },
  rowTitle: { color: colors.text, fontSize: 14, fontWeight: "600" },
  rowSub: { color: colors.textDim, fontSize: 12, marginTop: 2 },
  rowActions: { flexDirection: "row", alignItems: "center", marginLeft: 8 },
  overlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: "flex-end" },
  sheet: { backgroundColor: colors.card, borderTopLeftRadius: 16, borderTopRightRadius: 16, maxHeight: "90%", paddingBottom: 24 },
  sheetHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", padding: 16, borderBottomWidth: 1, borderBottomColor: colors.border },
  sheetTitle: { fontSize: 16, fontWeight: "700", color: colors.text },
  sheetBody: { padding: 16 },
  field: { marginBottom: 14 },
  fieldLabel: { color: colors.textDim, fontSize: 12, marginBottom: 4 },
  input: { backgroundColor: colors.background, color: colors.text, borderRadius: 8, padding: 10, borderWidth: 1, borderColor: colors.border, fontSize: 14 },
  inputMulti: { minHeight: 80, textAlignVertical: "top" },
  saveBtn: { backgroundColor: colors.primary, padding: 14, borderRadius: 8, alignItems: "center", marginTop: 8 },
  saveBtnText: { color: "#fff", fontWeight: "700", fontSize: 15 },
});
