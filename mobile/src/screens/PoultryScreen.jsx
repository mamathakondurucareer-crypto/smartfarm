import React, { useState } from "react";
import { View, Text, StyleSheet, Modal, TextInput, TouchableOpacity, ScrollView, TouchableWithoutFeedback } from "react-native";
import { Egg, Users, TrendingUp, Activity, Thermometer, AlertTriangle, Bug, Sprout, Pencil } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import StatGrid      from "../components/ui/StatGrid";
import { colors, spacing, radius, fontSize } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";

export default function PoultryScreen() {
  const farm = useFarmStore((s) => s.farm);
  const updatePoultry = useFarmStore((s) => s.updatePoultry);
  const updateDucks = useFarmStore((s) => s.updateDucks);
  const updateBees = useFarmStore((s) => s.updateBees);

  const { poultry: p, ducks: d, bees, sensors: s } = farm;

  const [modalVisible, setModalVisible] = useState(false);
  const [editingSection, setEditingSection] = useState(null);
  const [formData, setFormData] = useState({});

  const henStats = [
    { Icon: Users,         label: "Active Hens",  value: p.hens,          color: colors.poultry, compact: true },
    { Icon: Egg,           label: "Eggs Today",   value: p.eggsToday,     color: colors.accent,  compact: true, sub: `${p.eggsBroken} broken` },
    { Icon: TrendingUp,    label: "Lay Rate",     value: `${p.layRate}%`, color: colors.primary, compact: true },
    { Icon: Activity,      label: "Feed Used",    value: `${p.feedConsumed}kg`, color: colors.poultry, compact: true },
    { Icon: Thermometer,   label: "Shed Temp",    value: s.poultryTemp,   unit: "°C", color: colors.info,    compact: true },
    { Icon: AlertTriangle, label: "NH₃ Level",    value: s.poultryAmmonia, unit: "ppm", color: s.poultryAmmonia > 20 ? colors.danger : colors.primary, compact: true },
  ];

  const duckStats = [
    { Icon: Users, label: "Ducks Active", value: d.count,      color: colors.info,   compact: true },
    { Icon: Egg,   label: "Duck Eggs",    value: d.eggsToday,  color: colors.accent, compact: true },
  ];

  const beeStats = [
    { Icon: Sprout,   label: "Bee Hives",     value: bees.hives,       color: colors.accent, compact: true },
    { Icon: Activity, label: "Honey Stored",  value: `${bees.honeyStored}kg`, color: colors.accent, compact: true },
  ];

  const openEditPoultry = () => {
    setEditingSection("poultry");
    setFormData({
      hens: p.hens.toString(),
      layRate: p.layRate.toString(),
      eggsToday: p.eggsToday.toString(),
      eggsBroken: p.eggsBroken.toString(),
      feedConsumed: p.feedConsumed.toString(),
      mortality: p.mortality.toString(),
      waterUsage: p.waterUsage.toString(),
    });
    setModalVisible(true);
  };

  const openEditDucks = () => {
    setEditingSection("ducks");
    setFormData({
      count: d.count.toString(),
      eggsToday: d.eggsToday.toString(),
      pestsConsumed: d.pestsConsumed,
      area: d.area,
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
    if (editingSection === "poultry") {
      updatePoultry({
        hens: parseInt(formData.hens) || 0,
        layRate: parseFloat(formData.layRate) || 0,
        eggsToday: parseInt(formData.eggsToday) || 0,
        eggsBroken: parseInt(formData.eggsBroken) || 0,
        feedConsumed: parseInt(formData.feedConsumed) || 0,
        mortality: parseInt(formData.mortality) || 0,
        waterUsage: parseInt(formData.waterUsage) || 0,
      });
    } else if (editingSection === "ducks") {
      updateDucks({
        count: parseInt(formData.count) || 0,
        eggsToday: parseInt(formData.eggsToday) || 0,
        pestsConsumed: formData.pestsConsumed,
        area: formData.area,
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
    if (editingSection === "poultry") return "Edit Layer Hens";
    if (editingSection === "ducks") return "Edit Ducks";
    if (editingSection === "bees") return "Edit Bees";
    return "Edit";
  };

  const getFormFields = () => {
    if (editingSection === "poultry") {
      return (
        <>
          <Text style={styles.label}>Active Hens</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={formData.hens} onChangeText={(text) => setFormData({ ...formData, hens: text })} placeholderTextColor={colors.textMuted} />

          <Text style={styles.label}>Lay Rate (%)</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={formData.layRate} onChangeText={(text) => setFormData({ ...formData, layRate: text })} placeholderTextColor={colors.textMuted} />

          <Text style={styles.label}>Eggs Today</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={formData.eggsToday} onChangeText={(text) => setFormData({ ...formData, eggsToday: text })} placeholderTextColor={colors.textMuted} />

          <Text style={styles.label}>Eggs Broken</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={formData.eggsBroken} onChangeText={(text) => setFormData({ ...formData, eggsBroken: text })} placeholderTextColor={colors.textMuted} />

          <Text style={styles.label}>Feed Consumed (kg)</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={formData.feedConsumed} onChangeText={(text) => setFormData({ ...formData, feedConsumed: text })} placeholderTextColor={colors.textMuted} />

          <Text style={styles.label}>Mortality (%)</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={formData.mortality} onChangeText={(text) => setFormData({ ...formData, mortality: text })} placeholderTextColor={colors.textMuted} />

          <Text style={styles.label}>Water Usage (L)</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={formData.waterUsage} onChangeText={(text) => setFormData({ ...formData, waterUsage: text })} placeholderTextColor={colors.textMuted} />
        </>
      );
    } else if (editingSection === "ducks") {
      return (
        <>
          <Text style={styles.label}>Duck Count</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={formData.count} onChangeText={(text) => setFormData({ ...formData, count: text })} placeholderTextColor={colors.textMuted} />

          <Text style={styles.label}>Eggs Today</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={formData.eggsToday} onChangeText={(text) => setFormData({ ...formData, eggsToday: text })} placeholderTextColor={colors.textMuted} />

          <Text style={styles.label}>Pests Consumed</Text>
          <TextInput style={styles.input} value={formData.pestsConsumed} onChangeText={(text) => setFormData({ ...formData, pestsConsumed: text })} placeholderTextColor={colors.textMuted} />

          <Text style={styles.label}>Area</Text>
          <TextInput style={styles.input} value={formData.area} onChangeText={(text) => setFormData({ ...formData, area: text })} placeholderTextColor={colors.textMuted} />
        </>
      );
    } else if (editingSection === "bees") {
      return (
        <>
          <Text style={styles.label}>Hives</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={formData.hives} onChangeText={(text) => setFormData({ ...formData, hives: text })} placeholderTextColor={colors.textMuted} />

          <Text style={styles.label}>Honey Stored (kg)</Text>
          <TextInput style={styles.input} keyboardType="numeric" value={formData.honeyStored} onChangeText={(text) => setFormData({ ...formData, honeyStored: text })} placeholderTextColor={colors.textMuted} />

          <Text style={styles.label}>Active Foragers</Text>
          <TextInput style={styles.input} value={formData.activeForagers} onChangeText={(text) => setFormData({ ...formData, activeForagers: text })} placeholderTextColor={colors.textMuted} />

          <Text style={styles.label}>Last Inspection</Text>
          <TextInput style={styles.input} value={formData.lastInspection} onChangeText={(text) => setFormData({ ...formData, lastInspection: text })} placeholderTextColor={colors.textMuted} />
        </>
      );
    }
  };

  return (
    <ScreenWrapper title="Poultry & Duck">
      {/* Layer hens */}
      <Card>
        <View style={styles.sectionHeader}>
          <SectionHeader Icon={Egg} title="800 Layer Hens" color={colors.poultry} />
          <TouchableOpacity onPress={openEditPoultry} style={styles.editButton}>
            <Pencil size={16} color={colors.primary} />
          </TouchableOpacity>
        </View>
        <StatGrid stats={henStats} />
      </Card>

      <View style={styles.gap} />

      {/* Ducks */}
      <Card>
        <View style={styles.sectionHeader}>
          <SectionHeader Icon={Bug} title="Ducks — Pest Control" color={colors.info} />
          <TouchableOpacity onPress={openEditDucks} style={styles.editButton}>
            <Pencil size={16} color={colors.primary} />
          </TouchableOpacity>
        </View>
        <StatGrid stats={duckStats} />
        <View style={styles.infoBox}>
          <Text style={styles.infoText}>
            <Text style={styles.bold}>Pest Control:</Text> {d.pestsConsumed} activity at {d.area}
          </Text>
        </View>
      </Card>

      <View style={styles.gap} />

      {/* Bees */}
      <Card>
        <View style={styles.sectionHeader}>
          <SectionHeader Icon={Sprout} title="Apiculture — 20 Hives" color={colors.accent} />
          <TouchableOpacity onPress={openEditBees} style={styles.editButton}>
            <Pencil size={16} color={colors.primary} />
          </TouchableOpacity>
        </View>
        <StatGrid stats={beeStats} />
        <View style={styles.infoBox}>
          <Text style={styles.infoText}>Forager activity: {bees.activeForagers}</Text>
          <Text style={styles.infoText}>Last inspection: {bees.lastInspection}</Text>
          <Text style={styles.infoText}>Pollination boost: +18% greenhouse yield</Text>
        </View>
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

const styles = StyleSheet.create({
  gap:              { height: spacing.lg },
  sectionHeader:    { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.sm },
  editButton:       { padding: spacing.xs },
  infoBox:          { backgroundColor: colors.bg, borderRadius: radius.md, padding: spacing.md, marginTop: spacing.md },
  infoText:         { fontSize: fontSize.md, color: colors.textDim, lineHeight: 20 },
  bold:             { fontWeight: "600", color: colors.text },

  modalOverlay:     { flex: 1, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: "flex-end" },
  modalContent:     { backgroundColor: colors.card, borderTopLeftRadius: radius.lg, borderTopRightRadius: radius.lg, padding: spacing.lg, maxHeight: "85%" },
  modalTitle:       { fontSize: fontSize.lg, fontWeight: "700", color: colors.text, marginBottom: spacing.md },
  formScroll:       { maxHeight: 350 },
  label:            { fontSize: fontSize.sm, fontWeight: "600", color: colors.text, marginBottom: spacing.xs, marginTop: spacing.md },
  input:            { backgroundColor: colors.bg, borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, paddingHorizontal: spacing.sm, paddingVertical: spacing.sm, fontSize: fontSize.md, color: colors.text },

  modalButtonGroup: { flexDirection: "row", gap: spacing.sm, marginTop: spacing.lg },
  cancelButton:     { flex: 1, backgroundColor: colors.border, borderRadius: radius.md, paddingVertical: spacing.sm, alignItems: "center" },
  cancelButtonText: { fontSize: fontSize.md, color: colors.textDim, fontWeight: "600" },
  saveButton:       { flex: 1, backgroundColor: colors.primary, borderRadius: radius.md, paddingVertical: spacing.sm, alignItems: "center" },
  saveButtonText:   { fontSize: fontSize.md, color: colors.bg, fontWeight: "600" },
});
