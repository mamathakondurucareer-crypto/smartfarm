import React, { useState } from "react";
import { View, Text, Modal, TextInput, TouchableOpacity, ScrollView, TouchableWithoutFeedback } from "react-native";
import { Sprout, Thermometer, Droplets, Activity, Plus, Pencil, Trash2 } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import StatGrid      from "../components/ui/StatGrid";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import Badge         from "../components/ui/Badge";
import { colors, spacing, radius, fontSize } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";
import { styles } from "./VerticalFarmScreen.styles";
import { commonStyles as cs } from "../styles/common";

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

      <View style={cs.gap} />

      <Card>
        <View style={cs.cardHeader}>
          <SectionHeader Icon={Sprout} title="Vertical Farm Tiers" color={colors.verticalFarm} />
          <TouchableOpacity onPress={openAddModal} style={cs.addButton}>
            <Plus size={18} color={colors.primary} />
            <Text style={cs.addButtonText}>Add</Text>
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
          <View style={cs.modalOverlay}>
            <TouchableWithoutFeedback>
              <View style={cs.modalContent}>
                <Text style={cs.modalTitle}>{editingBatch ? "Edit Batch" : "Add New Batch"}</Text>

                <ScrollView style={cs.formScroll} showsVerticalScrollIndicator={false}>
                  <Text style={cs.label}>Crop Name *</Text>
                  <TextInput
                    style={cs.input}
                    placeholder="e.g., Spinach"
                    editable={!editingBatch}
                    value={formData.crop}
                    onChangeText={(text) => setFormData({ ...formData, crop: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={cs.label}>Tier *</Text>
                  <TextInput
                    style={cs.input}
                    placeholder="e.g., 1-2"
                    value={formData.tier}
                    onChangeText={(text) => setFormData({ ...formData, tier: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={cs.label}>Cycle Day</Text>
                  <TextInput
                    style={cs.input}
                    placeholder="e.g., 18"
                    keyboardType="numeric"
                    value={formData.cycleDay}
                    onChangeText={(text) => setFormData({ ...formData, cycleDay: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={cs.label}>Health (%)</Text>
                  <TextInput
                    style={cs.input}
                    placeholder="e.g., 96"
                    keyboardType="numeric"
                    value={formData.health}
                    onChangeText={(text) => setFormData({ ...formData, health: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={cs.label}>Batch (kg)</Text>
                  <TextInput
                    style={cs.input}
                    placeholder="e.g., 120"
                    keyboardType="numeric"
                    value={formData.batchKg}
                    onChangeText={(text) => setFormData({ ...formData, batchKg: text })}
                    placeholderTextColor={colors.textMuted}
                  />

                  <Text style={cs.label}>Cycles Left</Text>
                  <TextInput
                    style={cs.input}
                    placeholder="e.g., 2"
                    keyboardType="numeric"
                    value={formData.cyclesLeft}
                    onChangeText={(text) => setFormData({ ...formData, cyclesLeft: text })}
                    placeholderTextColor={colors.textMuted}
                  />
                </ScrollView>

                <View style={cs.modalButtonGroup}>
                  <TouchableOpacity onPress={() => setModalVisible(false)} style={cs.cancelButton}>
                    <Text style={cs.cancelButtonText}>Cancel</Text>
                  </TouchableOpacity>

                  {editingBatch && (
                    <TouchableOpacity onPress={handleDelete} style={cs.deleteButton}>
                      <Trash2 size={16} color={colors.bg} />
                      <Text style={cs.deleteButtonText}>Delete</Text>
                    </TouchableOpacity>
                  )}

                  <TouchableOpacity onPress={handleSave} style={cs.saveButton}>
                    <Text style={cs.saveButtonText}>{editingBatch ? "Update" : "Add"}</Text>
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

