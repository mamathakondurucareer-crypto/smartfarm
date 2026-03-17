import React, { useState } from "react";
import { View, Text, StyleSheet, Modal, TextInput, TouchableOpacity, ScrollView, TouchableWithoutFeedback } from "react-native";
import { Sprout, Thermometer, Droplets, Activity, Plus, Pencil, Trash2 } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import StatGrid      from "../components/ui/StatGrid";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import Badge         from "../components/ui/Badge";
import { colors, spacing, radius, fontSize } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";

export default function VerticalFarmScreen() {
  const farm = useFarmStore((s) => s.farm);
  const addVerticalFarm = useFarmStore((s) => s.addVerticalFarm);
  const updateVerticalFarm = useFarmStore((s) => s.updateVerticalFarm);
  const removeVerticalFarm = useFarmStore((s) => s.removeVerticalFarm);

  const s    = farm.sensors;

  const [modalVisible, setModalVisible] = useState(false);
  const [editingBatch, setEditingBatch] = useState(null);
  const [formData, setFormData] = useState({
    crop: "",
    tier: "",
    cycleDay: "",
    health: "",
    batchKg: "",
    cyclesLeft: "",
  });

  const envStats = [
    { Icon: Thermometer, label: "VF Temp",      value: s.vfTemp,        unit: "°C",  color: colors.verticalFarm },
    { Icon: Droplets,    label: "VF Humidity",  value: s.vfHumidity,    unit: "%",   color: colors.water },
    { Icon: Activity,    label: "Nutrient EC",  value: s.vfNutrientEC,  unit: "mS",  color: colors.primary },
    { Icon: Activity,    label: "Solution pH",  value: s.vfPH,                       color: colors.accent },
  ];

  const openEditModal = (batch) => {
    setEditingBatch(batch);
    setFormData({
      crop: batch.crop,
      tier: batch.tier,
      cycleDay: batch.cycleDay.toString(),
      health: batch.health.toString(),
      batchKg: batch.batchKg.toString(),
      cyclesLeft: batch.cyclesLeft.toString(),
    });
    setModalVisible(true);
  };

  const openAddModal = () => {
    setEditingBatch(null);
    setFormData({
      crop: "",
      tier: "",
      cycleDay: "",
      health: "",
      batchKg: "",
      cyclesLeft: "",
    });
    setModalVisible(true);
  };

  const handleSave = () => {
    if (!formData.crop || !formData.tier) {
      alert("Please enter crop name and tier");
      return;
    }

    const batchData = {
      crop: formData.crop,
      tier: formData.tier,
      cycleDay: parseInt(formData.cycleDay) || 0,
      health: parseInt(formData.health) || 0,
      batchKg: parseInt(formData.batchKg) || 0,
      cyclesLeft: parseInt(formData.cyclesLeft) || 0,
    };

    if (editingBatch) {
      updateVerticalFarm(editingBatch.crop, batchData);
    } else {
      addVerticalFarm(batchData);
    }

    setModalVisible(false);
  };

  const handleDelete = () => {
    if (editingBatch) {
      removeVerticalFarm(editingBatch.crop);
      setModalVisible(false);
    }
  };

  return (
    <ScreenWrapper title="Vertical Farm">
      <StatGrid stats={envStats} />

      <View style={styles.gap} />

      <Card>
        <View style={styles.cardHeader}>
          <SectionHeader Icon={Sprout} title="Vertical Farm Tiers" color={colors.verticalFarm} />
          <TouchableOpacity onPress={openAddModal} style={styles.addButton}>
            <Plus size={18} color={colors.primary} />
            <Text style={styles.addButtonText}>Add</Text>
          </TouchableOpacity>
        </View>

        {farm.verticalFarm.map((tier) => (
          <View key={tier.crop} style={styles.tierCard}>
            <View style={styles.tierHeader}>
              <View style={styles.tierTitleRow}>
                <Text style={styles.tierCrop}>{tier.crop}</Text>
                <TouchableOpacity onPress={() => openEditModal(tier)} style={styles.editIconSmall}>
                  <Pencil size={14} color={colors.primary} />
                </TouchableOpacity>
              </View>
              <Badge label={`Tier ${tier.tier}`} color={colors.verticalFarm} />
            </View>
            <View style={styles.tierGrid}>
              <MetaItem label="Cycle Day"   value={`Day ${tier.cycleDay}`} />
              <MetaItem label="Health"      value={`${tier.health}%`} valueColor={colors.primary} />
              <MetaItem label="Batch"       value={`${tier.batchKg} kg`} />
              <MetaItem label="Cycles Left" value={tier.cyclesLeft} />
            </View>
          </View>
        ))}
      </Card>

      {/* Edit/Add Batch Modal */}
      <Modal visible={modalVisible} animationType="fade" transparent onRequestClose={() => setModalVisible(false)}>
        <TouchableWithoutFeedback onPress={() => setModalVisible(false)}>
          <View style={styles.modalOverlay}>
            <TouchableWithoutFeedback>
              <View style={styles.modalContent}>
                <Text style={styles.modalTitle}>{editingBatch ? "Edit Batch" : "Add New Batch"}</Text>

                <ScrollView style={styles.formScroll} showsVerticalScrollIndicator={false}>
                  <Text style={styles.label}>Crop Name *</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="e.g., Spinach"
                    editable={!editingBatch}
                    value={formData.crop}
                    onChangeText={(text) => setFormData({ ...formData, crop: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={styles.label}>Tier *</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="e.g., 1-2"
                    value={formData.tier}
                    onChangeText={(text) => setFormData({ ...formData, tier: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={styles.label}>Cycle Day</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="e.g., 18"
                    keyboardType="numeric"
                    value={formData.cycleDay}
                    onChangeText={(text) => setFormData({ ...formData, cycleDay: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={styles.label}>Health (%)</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="e.g., 96"
                    keyboardType="numeric"
                    value={formData.health}
                    onChangeText={(text) => setFormData({ ...formData, health: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={styles.label}>Batch (kg)</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="e.g., 120"
                    keyboardType="numeric"
                    value={formData.batchKg}
                    onChangeText={(text) => setFormData({ ...formData, batchKg: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={styles.label}>Cycles Left</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="e.g., 2"
                    keyboardType="numeric"
                    value={formData.cyclesLeft}
                    onChangeText={(text) => setFormData({ ...formData, cyclesLeft: text })}
                    placeholderTextColor={colors.textMuted}
                  />
                </ScrollView>

                <View style={styles.modalButtonGroup}>
                  <TouchableOpacity onPress={() => setModalVisible(false)} style={styles.cancelButton}>
                    <Text style={styles.cancelButtonText}>Cancel</Text>
                  </TouchableOpacity>

                  {editingBatch && (
                    <TouchableOpacity onPress={handleDelete} style={styles.deleteButton}>
                      <Trash2 size={16} color={colors.bg} />
                      <Text style={styles.deleteButtonText}>Delete</Text>
                    </TouchableOpacity>
                  )}

                  <TouchableOpacity onPress={handleSave} style={styles.saveButton}>
                    <Text style={styles.saveButtonText}>{editingBatch ? "Update" : "Add"}</Text>
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

function MetaItem({ label, value, valueColor }) {
  return (
    <View style={styles.metaItem}>
      <Text style={styles.metaLabel}>{label}</Text>
      <Text style={[styles.metaValue, valueColor ? { color: valueColor, fontWeight: "600" } : null]}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  gap:           { height: spacing.lg },
  cardHeader:    { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.sm },
  addButton:     { flexDirection: "row", alignItems: "center", gap: spacing.xs, paddingHorizontal: spacing.sm, paddingVertical: spacing.xs, borderRadius: radius.sm, backgroundColor: colors.primary + "15" },
  addButtonText: { fontSize: fontSize.sm, color: colors.primary, fontWeight: "600" },

  tierCard:        { backgroundColor: colors.bg, borderRadius: radius.lg, padding: spacing.md, marginBottom: spacing.sm, borderWidth: 1, borderColor: colors.border },
  tierHeader:      { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start", marginBottom: spacing.sm },
  tierTitleRow:    { flexDirection: "row", alignItems: "center", gap: spacing.sm },
  tierCrop:        { fontSize: fontSize.lg, fontWeight: "700", color: colors.text },
  editIconSmall:   { padding: spacing.xs },
  tierGrid:        { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  metaItem:        { width: "47%" },
  metaLabel:       { fontSize: fontSize.xs, color: colors.textMuted },
  metaValue:       { fontSize: fontSize.sm, color: colors.textDim, marginTop: 1 },

  modalOverlay:    { flex: 1, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: "flex-end" },
  modalContent:    { backgroundColor: colors.card, borderTopLeftRadius: radius.lg, borderTopRightRadius: radius.lg, padding: spacing.lg, maxHeight: "85%" },
  modalTitle:      { fontSize: fontSize.lg, fontWeight: "700", color: colors.text, marginBottom: spacing.md },
  formScroll:      { maxHeight: 350 },
  label:           { fontSize: fontSize.sm, fontWeight: "600", color: colors.text, marginBottom: spacing.xs, marginTop: spacing.md },
  input:           { backgroundColor: colors.bg, borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, paddingHorizontal: spacing.sm, paddingVertical: spacing.sm, fontSize: fontSize.md, color: colors.text },

  modalButtonGroup: { flexDirection: "row", gap: spacing.sm, marginTop: spacing.lg },
  cancelButton:     { flex: 1, backgroundColor: colors.border, borderRadius: radius.md, paddingVertical: spacing.sm, alignItems: "center" },
  cancelButtonText: { fontSize: fontSize.md, color: colors.textDim, fontWeight: "600" },
  deleteButton:     { flexDirection: "row", alignItems: "center", gap: spacing.xs, backgroundColor: colors.danger, borderRadius: radius.md, paddingVertical: spacing.sm, paddingHorizontal: spacing.md },
  deleteButtonText: { fontSize: fontSize.md, color: colors.bg, fontWeight: "600" },
  saveButton:       { flex: 1, backgroundColor: colors.primary, borderRadius: radius.md, paddingVertical: spacing.sm, alignItems: "center" },
  saveButtonText:   { fontSize: fontSize.md, color: colors.bg, fontWeight: "600" },
});
