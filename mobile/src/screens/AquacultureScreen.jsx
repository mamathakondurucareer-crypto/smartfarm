import React, { useState } from "react";
import { View, Text, Modal, TextInput, TouchableOpacity, ScrollView, TouchableWithoutFeedback } from "react-native";
import { Fish, Activity, Thermometer, Droplets, AlertTriangle, BarChart3, Plus, Pencil, Trash2 } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import StatGrid      from "../components/ui/StatGrid";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import DataTable     from "../components/ui/DataTable";
import Badge         from "../components/ui/Badge";
import LineChartCard from "../components/charts/LineChartCard";
import { colors, spacing, fontSize, radius } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";
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

  const s    = farm.sensors;

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

  const totalStock   = farm.ponds.reduce((sum, p) => sum + p.stock, 0);
  const totalBiomass = farm.ponds.reduce((sum, p) => sum + p.stock * p.avgWeight, 0);

  const summaryStats = [
    { Icon: Fish,          label: "Total Stock",  value: totalStock.toLocaleString(), color: colors.fish,    sub: `${farm.ponds.length} ponds` },
    { Icon: Activity,      label: "Biomass",      value: `${(totalBiomass / 1000).toFixed(1)}T`, color: colors.primary },
    { Icon: Thermometer,   label: "Water Temp",   value: s.waterTemp,  unit: "°C",    color: colors.info },
    { Icon: Droplets,      label: "Avg DO",       value: s.dissolvedO2, unit: "mg/L", color: s.dissolvedO2 < 5 ? colors.danger : colors.water },
    { Icon: Activity,      label: "pH",           value: s.ph,                        color: colors.primary },
    { Icon: AlertTriangle, label: "Ammonia",      value: s.ammonia,    unit: "mg/L",  color: s.ammonia > 0.05 ? colors.danger : colors.primary },
  ];

  const tableHeaders = ["Pond", "Species", "Stock", "Wt (kg)", "FCR", "DO", "Feed (kg)", "Mort %", ""];
  const tableRows    = farm.ponds.map((p) => [
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

  const handleSave = () => {
    if (!formData.id || !formData.species || !formData.stock) {
      alert("Please fill in all required fields");
      return;
    }

    const pondData = {
      id: formData.id,
      species: formData.species,
      stock: parseInt(formData.stock) || 0,
      avgWeight: parseFloat(formData.avgWeight) || 0,
      fcr: parseFloat(formData.fcr) || 0,
      do: parseFloat(formData.do) || 0,
      feedToday: parseInt(formData.feedToday) || 0,
      mortality: parseFloat(formData.mortality) || 0,
    };

    if (editingPond) {
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

