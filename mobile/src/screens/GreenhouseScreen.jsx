import React, { useState } from "react";
import { View, Text, StyleSheet, Modal, TextInput, TouchableOpacity, ScrollView, TouchableWithoutFeedback } from "react-native";
import { Leaf, Thermometer, Droplets, Activity, Sun, Plus, Pencil, Trash2 } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import StatGrid      from "../components/ui/StatGrid";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import Badge         from "../components/ui/Badge";
import ProgressBar   from "../components/ui/ProgressBar";
import { colors, spacing, radius, fontSize } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";

const STAGE_COLORS = {
  Harvesting: colors.primary,
  Fruiting:   colors.accent,
  Flowering:  colors.info,
  Vegetative: colors.crop,
  Seedling:   colors.textDim,
};

const STAGES = ["Seedling", "Vegetative", "Flowering", "Fruiting", "Harvesting"];

export default function GreenhouseScreen() {
  const farm = useFarmStore((s) => s.farm);
  const addGreenhouse = useFarmStore((s) => s.addGreenhouse);
  const updateGreenhouse = useFarmStore((s) => s.updateGreenhouse);
  const removeGreenhouse = useFarmStore((s) => s.removeGreenhouse);

  const s    = farm.sensors;

  const [modalVisible, setModalVisible] = useState(false);
  const [editingCrop, setEditingCrop] = useState(null);
  const [formData, setFormData] = useState({
    crop: "",
    stage: "Seedling",
    daysPlanted: "",
    health: "",
    yieldKg: "",
    targetKg: "",
  });

  const envStats = [
    { Icon: Thermometer, label: "GH Temperature", value: s.ghTemp,       unit: "°C",   color: s.ghTemp > 36 ? colors.danger : colors.crop },
    { Icon: Droplets,    label: "GH Humidity",    value: s.ghHumidity,   unit: "%",    color: colors.water },
    { Icon: Activity,    label: "CO₂ Level",      value: s.ghCO2,        unit: "ppm",  color: colors.crop },
    { Icon: Sun,         label: "Light (PAR)",    value: s.ghLight,      unit: "µmol", color: colors.solar },
    { Icon: Droplets,    label: "Soil Moisture",  value: s.soilMoisture, unit: "%",    color: colors.water },
    { Icon: Thermometer, label: "Soil Temp",      value: s.soilTemp,     unit: "°C",   color: colors.poultry },
  ];

  const openEditModal = (crop) => {
    setEditingCrop(crop);
    setFormData({
      crop: crop.crop,
      stage: crop.stage,
      daysPlanted: crop.daysPlanted.toString(),
      health: crop.health.toString(),
      yieldKg: crop.yieldKg.toString(),
      targetKg: crop.targetKg.toString(),
    });
    setModalVisible(true);
  };

  const openAddModal = () => {
    setEditingCrop(null);
    setFormData({
      crop: "",
      stage: "Seedling",
      daysPlanted: "",
      health: "",
      yieldKg: "",
      targetKg: "",
    });
    setModalVisible(true);
  };

  const handleSave = () => {
    if (!formData.crop) {
      alert("Please enter crop name");
      return;
    }

    const cropData = {
      crop: formData.crop,
      stage: formData.stage,
      daysPlanted: parseInt(formData.daysPlanted) || 0,
      health: parseInt(formData.health) || 0,
      yieldKg: parseInt(formData.yieldKg) || 0,
      targetKg: parseInt(formData.targetKg) || 0,
    };

    if (editingCrop) {
      updateGreenhouse(editingCrop.id, cropData);
    } else {
      const newId = `GH-${formData.crop}-${Date.now()}`;
      addGreenhouse({ id: newId, ...cropData });
    }

    setModalVisible(false);
  };

  const handleDelete = () => {
    if (editingCrop) {
      removeGreenhouse(editingCrop.id);
      setModalVisible(false);
    }
  };

  return (
    <ScreenWrapper title="Greenhouse">
      <StatGrid stats={envStats} />

      <View style={styles.gap} />

      <Card>
        <View style={styles.cardHeader}>
          <SectionHeader Icon={Leaf} title="Crop Status" color={colors.crop} />
          <TouchableOpacity onPress={openAddModal} style={styles.addButton}>
            <Plus size={18} color={colors.primary} />
            <Text style={styles.addButtonText}>Add</Text>
          </TouchableOpacity>
        </View>

        {farm.greenhouse.map((crop) => (
          <View key={crop.id} style={styles.cropCard}>
            <View style={styles.cropHeader}>
              <View style={styles.cropTitleRow}>
                <Text style={styles.cropName}>{crop.crop}</Text>
                <TouchableOpacity onPress={() => openEditModal(crop)} style={styles.editIconSmall}>
                  <Pencil size={14} color={colors.primary} />
                </TouchableOpacity>
              </View>
              <Badge label={crop.stage} color={STAGE_COLORS[crop.stage] ?? colors.info} />
            </View>

            <View style={styles.cropMeta}>
              <Text style={styles.metaText}>Day {crop.daysPlanted}</Text>
              <Text style={[styles.healthText, { color: healthColor(crop.health) }]}>
                Health: {crop.health}%
              </Text>
            </View>

            <Text style={styles.yieldText}>
              Yield: {crop.yieldKg.toLocaleString()} / {crop.targetKg.toLocaleString()} kg
            </Text>
            <View style={styles.progressWrap}>
              <ProgressBar value={crop.yieldKg} max={crop.targetKg} color={colors.crop} />
            </View>
          </View>
        ))}
      </Card>

      {/* Edit/Add Crop Modal */}
      <Modal visible={modalVisible} animationType="fade" transparent onRequestClose={() => setModalVisible(false)}>
        <TouchableWithoutFeedback onPress={() => setModalVisible(false)}>
          <View style={styles.modalOverlay}>
            <TouchableWithoutFeedback>
              <View style={styles.modalContent}>
                <Text style={styles.modalTitle}>{editingCrop ? "Edit Crop" : "Add New Crop"}</Text>

                <ScrollView style={styles.formScroll} showsVerticalScrollIndicator={false}>
                  <Text style={styles.label}>Crop Name *</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="e.g., Tomato"
                    value={formData.crop}
                    onChangeText={(text) => setFormData({ ...formData, crop: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={styles.label}>Stage</Text>
                  <View style={styles.stagePicker}>
                    {STAGES.map((stage) => (
                      <TouchableOpacity
                        key={stage}
                        onPress={() => setFormData({ ...formData, stage })}
                        style={[styles.stageOption, formData.stage === stage && styles.stageOptionActive]}
                      >
                        <Text style={[styles.stageOptionText, formData.stage === stage && styles.stageOptionTextActive]}>
                          {stage}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </View>

                  <Text style={styles.label}>Days Planted</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="e.g., 85"
                    keyboardType="numeric"
                    value={formData.daysPlanted}
                    onChangeText={(text) => setFormData({ ...formData, daysPlanted: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={styles.label}>Health (%)</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="e.g., 92"
                    keyboardType="numeric"
                    value={formData.health}
                    onChangeText={(text) => setFormData({ ...formData, health: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={styles.label}>Yield (kg)</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="e.g., 2400"
                    keyboardType="numeric"
                    value={formData.yieldKg}
                    onChangeText={(text) => setFormData({ ...formData, yieldKg: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={styles.label}>Target (kg)</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="e.g., 9000"
                    keyboardType="numeric"
                    value={formData.targetKg}
                    onChangeText={(text) => setFormData({ ...formData, targetKg: text })}
                    placeholderTextColor={colors.textMuted}
                  />
                </ScrollView>

                <View style={styles.modalButtonGroup}>
                  <TouchableOpacity onPress={() => setModalVisible(false)} style={styles.cancelButton}>
                    <Text style={styles.cancelButtonText}>Cancel</Text>
                  </TouchableOpacity>

                  {editingCrop && (
                    <TouchableOpacity onPress={handleDelete} style={styles.deleteButton}>
                      <Trash2 size={16} color={colors.bg} />
                      <Text style={styles.deleteButtonText}>Delete</Text>
                    </TouchableOpacity>
                  )}

                  <TouchableOpacity onPress={handleSave} style={styles.saveButton}>
                    <Text style={styles.saveButtonText}>{editingCrop ? "Update" : "Add"}</Text>
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

function healthColor(pct) {
  if (pct > 90) return colors.primary;
  if (pct > 80) return colors.accent;
  return colors.danger;
}

const styles = StyleSheet.create({
  gap:           { height: spacing.lg },
  cardHeader:    { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.sm },
  addButton:     { flexDirection: "row", alignItems: "center", gap: spacing.xs, paddingHorizontal: spacing.sm, paddingVertical: spacing.xs, borderRadius: radius.sm, backgroundColor: colors.primary + "15" },
  addButtonText: { fontSize: fontSize.sm, color: colors.primary, fontWeight: "600" },

  cropCard:        { backgroundColor: colors.bg, borderRadius: radius.lg, padding: spacing.md, marginBottom: spacing.sm, borderWidth: 1, borderColor: colors.border },
  cropHeader:      { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start", marginBottom: spacing.sm },
  cropTitleRow:    { flexDirection: "row", alignItems: "center", gap: spacing.sm, flex: 1 },
  cropName:        { fontSize: fontSize.lg, fontWeight: "700", color: colors.text },
  editIconSmall:   { padding: spacing.xs },
  cropMeta:        { flexDirection: "row", justifyContent: "space-between", marginBottom: spacing.xs },
  metaText:        { fontSize: fontSize.md, color: colors.textDim },
  healthText:      { fontSize: fontSize.md, fontWeight: "600" },
  yieldText:       { fontSize: fontSize.sm, color: colors.textDim, marginBottom: spacing.xs },
  progressWrap:    { marginTop: 2 },

  modalOverlay:    { flex: 1, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: "flex-end" },
  modalContent:    { backgroundColor: colors.card, borderTopLeftRadius: radius.lg, borderTopRightRadius: radius.lg, padding: spacing.lg, maxHeight: "85%" },
  modalTitle:      { fontSize: fontSize.lg, fontWeight: "700", color: colors.text, marginBottom: spacing.md },
  formScroll:      { maxHeight: 350 },
  label:           { fontSize: fontSize.sm, fontWeight: "600", color: colors.text, marginBottom: spacing.xs, marginTop: spacing.md },
  input:           { backgroundColor: colors.bg, borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, paddingHorizontal: spacing.sm, paddingVertical: spacing.sm, fontSize: fontSize.md, color: colors.text },

  stagePicker:         { flexDirection: "row", flexWrap: "wrap", gap: spacing.xs, marginBottom: spacing.md },
  stageOption:         { paddingHorizontal: spacing.sm, paddingVertical: spacing.xs, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.bg },
  stageOptionActive:   { backgroundColor: colors.primary, borderColor: colors.primary },
  stageOptionText:     { fontSize: fontSize.sm, color: colors.textDim },
  stageOptionTextActive: { color: colors.bg, fontWeight: "600" },

  modalButtonGroup:  { flexDirection: "row", gap: spacing.sm, marginTop: spacing.lg },
  cancelButton:      { flex: 1, backgroundColor: colors.border, borderRadius: radius.md, paddingVertical: spacing.sm, alignItems: "center" },
  cancelButtonText:  { fontSize: fontSize.md, color: colors.textDim, fontWeight: "600" },
  deleteButton:      { flexDirection: "row", alignItems: "center", gap: spacing.xs, backgroundColor: colors.danger, borderRadius: radius.md, paddingVertical: spacing.sm, paddingHorizontal: spacing.md },
  deleteButtonText:  { fontSize: fontSize.md, color: colors.bg, fontWeight: "600" },
  saveButton:        { flex: 1, backgroundColor: colors.primary, borderRadius: radius.md, paddingVertical: spacing.sm, alignItems: "center" },
  saveButtonText:    { fontSize: fontSize.md, color: colors.bg, fontWeight: "600" },
});
