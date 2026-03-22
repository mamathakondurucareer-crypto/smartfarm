import React, { useEffect, useState } from "react";
import { View, Text, Modal, TextInput, TouchableOpacity, ScrollView, TouchableWithoutFeedback } from "react-native";
import { Fish, Activity, Thermometer, Droplets, AlertTriangle, BarChart3, Plus, Pencil, Trash2, WifiOff } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import StatGrid      from "../components/ui/StatGrid";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import DataTable     from "../components/ui/DataTable";
import Badge         from "../components/ui/Badge";
import LineChartCard from "../components/charts/LineChartCard";
import { colors, spacing, fontSize, radius } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";
import useAuthStore  from "../store/useAuthStore";
import { api } from "../services/api";
import { styles } from "./AquacultureScreen.styles";
import { commonStyles as cs } from "../styles/common";

// Generate 24 hours of simulated water quality data
const waterQuality24hr = Array.from({ length: 24 }, (_, i) => ({
  hour: `${i}:00`,
  do:   +(5.5 + Math.sin(i / 4) * 1.2).toFixed(1),
  ph:   +(7.2 + Math.sin(i / 6) * 0.3).toFixed(2),
}));

export default function AquacultureScreen() {
  const farm = useFarmStore((s) => s.farm);
  const addPond = useFarmStore((s) => s.addPond);
  const updatePond = useFarmStore((s) => s.updatePond);
  const removePond = useFarmStore((s) => s.removePond);
  const token = useAuthStore((s) => s.token);

  const s    = farm.sensors;

  const [apiSummary, setApiSummary] = useState(null);
  const [apiPonds, setApiPonds]     = useState(null);
  const [staleData, setStaleData]   = useState(false);

  useEffect(() => {
    if (!token) return;
    api.aquaculture.summary(token).then(setApiSummary).catch(() => setStaleData(true));
    api.aquaculture.ponds(token)
      .then((rows) => {
        if (rows && rows.length > 0) {
          const mapped = rows.map((p) => ({
            _backendId: p.id,
            id:         p.pond_code || String(p.id),
            species:    p.fish_species || "—",
            stock:      p.current_stock ?? 0,
            avgWeight:  p.avg_weight_kg ?? 0,
            fcr:        p.fcr ?? 0,
            do:         s.dissolvedO2,
            feedToday:  p.today_feed_kg ?? 0,
            mortality:  p.mortality_pct ?? 0,
          }));
          setApiPonds(mapped);
        }
      })
      .catch(() => setStaleData(true));
  }, [token]);

  const [modalVisible, setModalVisible] = useState(false);
  const [editingPond, setEditingPond] = useState(null);
  const [formData, setFormData] = useState({
    id: "",
    species: "",
    stock: "",
    avgWeight: "",
    fcr: "",
    do: "",
    feedToday: "",
    mortality: "",
  });

  const displayPonds = apiPonds ?? farm.ponds;
  const totalStock   = apiSummary?.total_stock    ?? displayPonds.reduce((sum, p) => sum + (p.stock ?? 0), 0);
  const totalBiomass = apiSummary?.total_biomass_kg != null
    ? apiSummary.total_biomass_kg * 1000
    : displayPonds.reduce((sum, p) => sum + (p.stock ?? 0) * (p.avgWeight ?? 0), 0);
  const pondCount    = apiSummary?.active_ponds    ?? displayPonds.length;

  const summaryStats = [
    { Icon: Fish,          label: "Total Stock",  value: totalStock.toLocaleString(),          color: colors.fish,    sub: `${pondCount} ponds` },
    { Icon: Activity,      label: "Biomass",      value: `${(totalBiomass / 1000).toFixed(1)}T`, color: colors.primary },
    { Icon: Thermometer,   label: "Water Temp",   value: s.waterTemp,   unit: "°C",   color: colors.info },
    { Icon: Droplets,      label: "Avg DO",       value: s.dissolvedO2, unit: "mg/L", color: s.dissolvedO2 < 5 ? colors.danger : colors.water },
    { Icon: Activity,      label: "pH",           value: s.ph,                        color: colors.primary },
    { Icon: AlertTriangle, label: "Ammonia",      value: s.ammonia,     unit: "mg/L", color: s.ammonia > 0.05 ? colors.danger : colors.primary },
  ];

  const tableHeaders = ["Pond", "Species", "Stock", "Wt (kg)", "FCR", "DO", "Feed (kg)", "Mort %", ""];
  const tableRows    = displayPonds.map((p) => [
    <Text style={{ fontWeight: "700", color: colors.fish }}>{p.id}</Text>,
    p.species,
    p.stock.toLocaleString(),
    p.avgWeight.toFixed(2),
    p.fcr.toFixed(2),
    <Text style={{ color: p.do < 5 ? colors.danger : colors.primary, fontWeight: "600" }}>{p.do}</Text>,
    p.feedToday,
    <Text style={{ color: p.mortality > 2 ? colors.danger : colors.textDim }}>{p.mortality}%</Text>,
    <TouchableOpacity onPress={() => openEditModal(p)} style={cs.editIcon}>
      <Pencil size={14} color={colors.primary} />
    </TouchableOpacity>,
  ]);

  const openEditModal = (pond) => {
    setEditingPond(pond);
    setFormData({
      id: pond.id,
      species: pond.species,
      stock: pond.stock.toString(),
      avgWeight: pond.avgWeight.toString(),
      fcr: pond.fcr.toString(),
      do: pond.do.toString(),
      feedToday: pond.feedToday.toString(),
      mortality: pond.mortality.toString(),
    });
    setModalVisible(true);
  };

  const openAddModal = () => {
    setEditingPond(null);
    setFormData({
      id: "",
      species: "",
      stock: "",
      avgWeight: "",
      fcr: "",
      do: "",
      feedToday: "",
      mortality: "",
    });
    setModalVisible(true);
  };

  const handleSave = async () => {
    if (!formData.id || !formData.species || !formData.stock) {
      alert("Please fill in all required fields");
      return;
    }

    const pondData = {
      id:         formData.id,
      species:    formData.species,
      stock:      parseInt(formData.stock) || 0,
      avgWeight:  parseFloat(formData.avgWeight) || 0,
      fcr:        parseFloat(formData.fcr) || 0,
      do:         parseFloat(formData.do) || 0,
      feedToday:  parseInt(formData.feedToday) || 0,
      mortality:  parseFloat(formData.mortality) || 0,
    };

    if (editingPond) {
      // Persist to backend if we have a backend id
      if (editingPond._backendId && token) {
        try {
          await api.aquaculture.updatePond(editingPond._backendId, {
            species:               pondData.species,
            current_count:         pondData.stock,
            current_avg_weight_kg: pondData.avgWeight,
            fcr:                   pondData.fcr,
            mortality_pct:         pondData.mortality,
          }, token);
        } catch (e) {
          console.warn("Pond API update failed:", e.message);
        }
      }
      // Update React state so display reflects the change immediately
      setApiPonds((prev) =>
        prev
          ? prev.map((p) =>
              p.id === editingPond.id
                ? { ...p, ...pondData, _backendId: editingPond._backendId }
                : p
            )
          : prev
      );
      updatePond(editingPond.id, pondData);
    } else {
      addPond(pondData);
    }

    setModalVisible(false);
  };

  const handleDelete = () => {
    if (editingPond) {
      removePond(editingPond.id);
      setModalVisible(false);
    }
  };

  const wqHours   = waterQuality24hr.filter((_, i) => i % 3 === 0).map((d) => d.hour);
  const doValues  = waterQuality24hr.filter((_, i) => i % 3 === 0).map((d) => d.do);
  const phValues  = waterQuality24hr.filter((_, i) => i % 3 === 0).map((d) => d.ph);

  return (
    <ScreenWrapper title="Aquaculture">
      {staleData && (
        <View style={cs.warnBox}>
          <WifiOff size={14} color={colors.warn} />
          <Text style={cs.warnText}>Live data unavailable — showing cached data</Text>
        </View>
      )}

      <StatGrid stats={summaryStats} />

      <View style={cs.gap} />

      {/* Pond table with Add button */}
      <Card>
        <View style={cs.cardHeader}>
          <SectionHeader Icon={Fish} title="Pond Status" color={colors.fish} />
          <TouchableOpacity onPress={openAddModal} style={cs.addButton}>
            <Plus size={18} color={colors.primary} />
            <Text style={cs.addButtonText}>Add</Text>
          </TouchableOpacity>
        </View>
        <DataTable headers={tableHeaders} rows={tableRows} />
      </Card>

      <View style={cs.gap} />

      {/* Water quality chart */}
      <LineChartCard
        Icon={Activity}
        title="Water Quality — 24 hr"
        color={colors.water}
        labels={wqHours}
        datasets={[
          { data: doValues, color: colors.water,  label: "DO (mg/L)" },
          { data: phValues, color: colors.accent,  label: "pH" },
        ]}
        height={220}
      />

      {/* Edit/Add Pond Modal */}
      <Modal visible={modalVisible} animationType="fade" transparent onRequestClose={() => setModalVisible(false)}>
        <TouchableWithoutFeedback onPress={() => setModalVisible(false)}>
          <View style={cs.modalOverlay}>
            <TouchableWithoutFeedback>
              <View style={cs.modalContent}>
                <Text style={cs.modalTitle}>{editingPond ? "Edit Pond" : "Add New Pond"}</Text>

                <ScrollView style={cs.formScroll} showsVerticalScrollIndicator={false}>
                  <Text style={cs.label}>Pond Code *</Text>
                  <TextInput
                    style={cs.input}
                    placeholder="e.g., P1"
                    editable={!editingPond}
                    value={formData.id}
                    onChangeText={(text) => setFormData({ ...formData, id: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={cs.label}>Species *</Text>
                  <TextInput
                    style={cs.input}
                    placeholder="e.g., Murrel"
                    value={formData.species}
                    onChangeText={(text) => setFormData({ ...formData, species: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={cs.label}>Stock Count *</Text>
                  <TextInput
                    style={cs.input}
                    placeholder="e.g., 3800"
                    keyboardType="numeric"
                    value={formData.stock}
                    onChangeText={(text) => setFormData({ ...formData, stock: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={cs.label}>Avg Weight (kg)</Text>
                  <TextInput
                    style={cs.input}
                    placeholder="e.g., 0.62"
                    keyboardType="numeric"
                    value={formData.avgWeight}
                    onChangeText={(text) => setFormData({ ...formData, avgWeight: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={cs.label}>FCR</Text>
                  <TextInput
                    style={cs.input}
                    placeholder="e.g., 1.78"
                    keyboardType="numeric"
                    value={formData.fcr}
                    onChangeText={(text) => setFormData({ ...formData, fcr: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={cs.label}>DO (mg/L)</Text>
                  <TextInput
                    style={cs.input}
                    placeholder="e.g., 5.8"
                    keyboardType="numeric"
                    value={formData.do}
                    onChangeText={(text) => setFormData({ ...formData, do: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={cs.label}>Feed Today (kg)</Text>
                  <TextInput
                    style={cs.input}
                    placeholder="e.g., 42"
                    keyboardType="numeric"
                    value={formData.feedToday}
                    onChangeText={(text) => setFormData({ ...formData, feedToday: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={cs.label}>Mortality (%)</Text>
                  <TextInput
                    style={cs.input}
                    placeholder="e.g., 1.2"
                    keyboardType="numeric"
                    value={formData.mortality}
                    onChangeText={(text) => setFormData({ ...formData, mortality: text })}
                    placeholderTextColor={colors.textMuted}
                  />
                </ScrollView>

                <View style={cs.modalButtonGroup}>
                  <TouchableOpacity onPress={() => setModalVisible(false)} style={cs.cancelButton}>
                    <Text style={cs.cancelButtonText}>Cancel</Text>
                  </TouchableOpacity>

                  {editingPond && (
                    <TouchableOpacity onPress={handleDelete} style={cs.deleteButton}>
                      <Trash2 size={16} color={colors.bg} />
                      <Text style={cs.deleteButtonText}>Delete</Text>
                    </TouchableOpacity>
                  )}

                  <TouchableOpacity onPress={handleSave} style={cs.saveButton}>
                    <Text style={cs.saveButtonText}>{editingPond ? "Update" : "Add"}</Text>
                  </TouchableOpacity>
                </View>
              </View>
            </TouchableWithoutFeedback>
          </View>
        </TouchableWithoutFeedback>
      </Modal>
    </ScreenWrapper>
  );
}

