import React, { useState } from "react";
import { View, Text, StyleSheet, Modal, TextInput, TouchableOpacity, ScrollView, TouchableWithoutFeedback } from "react-native";
import { Sprout, Truck, Activity, Leaf, Pencil } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import StatGrid      from "../components/ui/StatGrid";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import { colors, spacing, radius, fontSize } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";

export default function NurseryScreen() {
  const farm = useFarmStore((s) => s.farm);
  const updateNursery = useFarmStore((s) => s.updateNursery);
  const updateBees = useFarmStore((s) => s.updateBees);

  const { nursery: n, bees } = farm;

  const [modalVisible, setModalVisible] = useState(false);
  const [editingSection, setEditingSection] = useState(null);
  const [formData, setFormData] = useState({});

  const stats = [
    { Icon: Sprout,   label: "Seedlings Ready",    value: `${(n.seedlingsReady / 1000).toFixed(0)}K`, color: colors.primary, sub: "of 300K capacity" },
    { Icon: Truck,    label: "Orders This Month",  value: n.ordersThisMonth, color: colors.accent },
    { Icon: Activity, label: "Capacity Used",      value: `${n.capacityUsed}%`, color: colors.info },
    { Icon: Leaf,     label: "Species Available",  value: n.species,          color: colors.crop },
  ];

  const openEditNursery = () => {
    setEditingSection("nursery");
    setFormData({
      seedlingsReady: n.seedlingsReady.toString(),
      ordersThisMonth: n.ordersThisMonth.toString(),
      capacityUsed: n.capacityUsed.toString(),
      species: n.species.toString(),
    });
    setModalVisible(true);
  };

  const openEditBees = () => {
    setEditingSection("bees");
    setFormData({
      hives: bees.hives.toString(),
      honeyStored: bees.honeyStored.toString(),
      activeForagers: bees.activeForagers,
      lastInspection: bees.lastInspection,
    });
    setModalVisible(true);
  };

  const handleSave = () => {
    if (editingSection === "nursery") {
      updateNursery({
        seedlingsReady: parseInt(formData.seedlingsReady) || 0,
        ordersThisMonth: parseInt(formData.ordersThisMonth) || 0,
        capacityUsed: parseInt(formData.capacityUsed) || 0,
        species: parseInt(formData.species) || 0,
      });
    } else if (editingSection === "bees") {
      updateBees({
        hives: parseInt(formData.hives) || 0,
        honeyStored: parseInt(formData.honeyStored) || 0,
        activeForagers: formData.activeForagers,
        lastInspection: formData.lastInspection,
      });
    }
    setModalVisible(false);
  };

  const getSectionTitle = () => {
    if (editingSection === "nursery") return "Edit Nursery";
    if (editingSection === "bees") return "Edit Apiculture";
    return "Edit";
  };

  const getFormFields = () => {
    if (editingSection === "nursery") {
      return (
        <>
          <Text style={styles.formLabel}>Seedlings Ready</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={formData.seedlingsReady} onChangeText={(text) => setFormData({ ...formData, seedlingsReady: text })} placeholderTextColor={colors.textMuted} />

          <Text style={styles.formLabel}>Orders This Month</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={formData.ordersThisMonth} onChangeText={(text) => setFormData({ ...formData, ordersThisMonth: text })} placeholderTextColor={colors.textMuted} />

          <Text style={styles.formLabel}>Capacity Used (%)</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={formData.capacityUsed} onChangeText={(text) => setFormData({ ...formData, capacityUsed: text })} placeholderTextColor={colors.textMuted} />

          <Text style={styles.formLabel}>Species Available</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={formData.species} onChangeText={(text) => setFormData({ ...formData, species: text })} placeholderTextColor={colors.textMuted} />
        </>
      );
    } else if (editingSection === "bees") {
      return (
        <>
          <Text style={styles.formLabel}>Active Hives</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={formData.hives} onChangeText={(text) => setFormData({ ...formData, hives: text })} placeholderTextColor={colors.textMuted} />

          <Text style={styles.formLabel}>Honey Stored (kg)</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={formData.honeyStored} onChangeText={(text) => setFormData({ ...formData, honeyStored: text })} placeholderTextColor={colors.textMuted} />

          <Text style={styles.formLabel}>Forager Activity</Text>
          <TextInput style={styles.input} value={formData.activeForagers} onChangeText={(text) => setFormData({ ...formData, activeForagers: text })} placeholderTextColor={colors.textMuted} />

          <Text style={styles.formLabel}>Last Inspection</Text>
          <TextInput style={styles.input} value={formData.lastInspection} onChangeText={(text) => setFormData({ ...formData, lastInspection: text })} placeholderTextColor={colors.textMuted} />
        </>
      );
    }
  };

  return (
    <ScreenWrapper title="Nursery & Bees">
      <StatGrid stats={stats} />

      <View style={styles.gap} />

      <Card>
        <View style={styles.sectionHeader}>
          <SectionHeader Icon={Sprout} title="Seedling Nursery" color={colors.primary} />
          <TouchableOpacity onPress={openEditNursery} style={styles.editButton}>
            <Pencil size={16} color={colors.primary} />
          </TouchableOpacity>
        </View>
        <InfoItem label="Monthly Capacity"  value="300,000 seedlings" />
        <InfoItem label="Current Readiness" value={n.seedlingsReady.toLocaleString()} />
        <InfoItem label="Active Species"    value={`${n.species} varieties`} />
        <InfoItem label="Revenue / Month"   value="₹5.2 Lakh" />
        <InfoItem label="Top Sellers"       value="Tomato, Chilli, Brinjal, Marigold" />
      </Card>

      <View style={styles.gap} />

      <Card>
        <View style={styles.sectionHeader}>
          <SectionHeader Icon={Sprout} title="Apiculture — 20 Hives" color={colors.accent} />
          <TouchableOpacity onPress={openEditBees} style={styles.editButton}>
            <Pencil size={16} color={colors.primary} />
          </TouchableOpacity>
        </View>
        <InfoItem label="Active Hives"      value={bees.hives} />
        <InfoItem label="Forager Activity"  value={bees.activeForagers} />
        <InfoItem label="Honey Stored"      value={`${bees.honeyStored} kg`} />
        <InfoItem label="Last Inspection"   value={bees.lastInspection} />
        <InfoItem label="Pollination Boost" value="+18% greenhouse yield" />
      </Card>

      {/* Edit Modal */}
      <Modal visible={modalVisible} animationType="fade" transparent onRequestClose={() => setModalVisible(false)}>
        <TouchableWithoutFeedback onPress={() => setModalVisible(false)}>
          <View style={styles.modalOverlay}>
            <TouchableWithoutFeedback>
              <View style={styles.modalContent}>
                <Text style={styles.modalTitle}>{getSectionTitle()}</Text>

                <ScrollView style={styles.formScroll} showsVerticalScrollIndicator={false}>
                  {getFormFields()}
                </ScrollView>

                <View style={styles.modalButtonGroup}>
                  <TouchableOpacity onPress={() => setModalVisible(false)} style={styles.cancelButton}>
                    <Text style={styles.cancelButtonText}>Cancel</Text>
                  </TouchableOpacity>

                  <TouchableOpacity onPress={handleSave} style={styles.saveButton}>
                    <Text style={styles.saveButtonText}>Save</Text>
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

function InfoItem({ label, value }) {
  return (
    <View style={styles.row}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  gap:              { height: spacing.lg },
  sectionHeader:    { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.sm },
  editButton:       { padding: spacing.xs },
  row:              { flexDirection: "row", justifyContent: "space-between", paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: colors.border + "40" },
  label:            { fontSize: fontSize.md, color: colors.textDim },
  value:            { fontSize: fontSize.md, color: colors.text, fontWeight: "500", flexShrink: 1, textAlign: "right", marginLeft: spacing.sm },

  modalOverlay:     { flex: 1, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: "flex-end" },
  modalContent:     { backgroundColor: colors.card, borderTopLeftRadius: radius.lg, borderTopRightRadius: radius.lg, padding: spacing.lg, maxHeight: "85%" },
  modalTitle:       { fontSize: fontSize.lg, fontWeight: "700", color: colors.text, marginBottom: spacing.md },
  formScroll:       { maxHeight: 350 },
  formLabel:        { fontSize: fontSize.sm, fontWeight: "600", color: colors.text, marginBottom: spacing.xs, marginTop: spacing.md },
  input:            { backgroundColor: colors.bg, borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, paddingHorizontal: spacing.sm, paddingVertical: spacing.sm, fontSize: fontSize.md, color: colors.text },

  modalButtonGroup: { flexDirection: "row", gap: spacing.sm, marginTop: spacing.lg },
  cancelButton:     { flex: 1, backgroundColor: colors.border, borderRadius: radius.md, paddingVertical: spacing.sm, alignItems: "center" },
  cancelButtonText: { fontSize: fontSize.md, color: colors.textDim, fontWeight: "600" },
  saveButton:       { flex: 1, backgroundColor: colors.primary, borderRadius: radius.md, paddingVertical: spacing.sm, alignItems: "center" },
  saveButtonText:   { fontSize: fontSize.md, color: colors.bg, fontWeight: "600" },
});
