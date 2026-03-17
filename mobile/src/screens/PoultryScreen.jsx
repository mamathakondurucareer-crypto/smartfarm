import React, { useEffect, useState } from "react";
import { View, Text, Modal, TextInput, TouchableOpacity, ScrollView, TouchableWithoutFeedback } from "react-native";
import { Egg, Users, TrendingUp, Activity, Thermometer, AlertTriangle, Bug, Sprout, Pencil } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import StatGrid      from "../components/ui/StatGrid";
import { colors } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";
import useAuthStore  from "../store/useAuthStore";
import { api } from "../services/api";
import { styles } from "./PoultryScreen.styles";
import { commonStyles as cs } from "../styles/common";

export default function PoultryScreen() {
  const farm = useFarmStore((s) => s.farm);
  const updatePoultry = useFarmStore((s) => s.updatePoultry);
  const updateDucks = useFarmStore((s) => s.updateDucks);
  const updateBees = useFarmStore((s) => s.updateBees);
  const token = useAuthStore((s) => s.token);

  const { poultry: p, ducks: d, bees, sensors: s } = farm;

  const [apiPoultry, setApiPoultry] = useState(null);
  const [apiDucks, setApiDucks]     = useState(null);
  const [apiBees, setApiBees]       = useState(null);

  useEffect(() => {
    if (!token) return;
    api.poultry.flocks(token)
      .then((rows) => {
        if (rows && rows.length > 0) {
          // Aggregate all flocks
          const totalHens  = rows.reduce((sum, f) => sum + (f.current_count ?? 0), 0);
          const avgLayRate = rows.reduce((sum, f) => sum + (f.lay_rate_pct ?? 0), 0) / rows.length;
          const totalEggs  = rows.reduce((sum, f) => sum + (f.total_eggs_produced ?? 0), 0);
          setApiPoultry({ hens: totalHens, layRate: +avgLayRate.toFixed(1), eggsToday: totalEggs });
        }
      })
      .catch(() => {});
    api.poultry.ducks(token)
      .then((rows) => {
        if (rows && rows.length > 0) {
          const first = rows[0];
          setApiDucks({
            count:      first.current_count ?? 0,
            eggsToday:  first.eggs_today ?? 0,
            area:       first.deployment_area ?? d.area,
          });
        }
      })
      .catch(() => {});
    api.poultry.bees(token)
      .then((rows) => {
        if (rows && rows.length > 0) {
          const totalHoney = rows.reduce((sum, h) => sum + (h.total_honey_harvested_kg ?? 0), 0);
          setApiBees({
            hives:          rows.length,
            honeyStored:    +totalHoney.toFixed(1),
            lastInspection: rows[0].last_inspection_date ?? bees.lastInspection,
          });
        }
      })
      .catch(() => {});
  }, [token]);

  const henData  = apiPoultry ?? p;
  const duckData = apiDucks   ?? d;
  const beeData  = apiBees    ?? bees;

  const [modalVisible, setModalVisible] = useState(false);
  const [editingSection, setEditingSection] = useState(null);
  const [formData, setFormData] = useState({});

  const henStats = [
    { Icon: Users,         label: "Active Hens",  value: henData.hens,               color: colors.poultry, compact: true },
    { Icon: Egg,           label: "Eggs Today",   value: henData.eggsToday,          color: colors.accent,  compact: true, sub: `${p.eggsBroken} broken` },
    { Icon: TrendingUp,    label: "Lay Rate",     value: `${henData.layRate}%`,      color: colors.primary, compact: true },
    { Icon: Activity,      label: "Feed Used",    value: `${p.feedConsumed}kg`,      color: colors.poultry, compact: true },
    { Icon: Thermometer,   label: "Shed Temp",    value: s.poultryTemp,              unit: "°C",   color: colors.info,    compact: true },
    { Icon: AlertTriangle, label: "NH₃ Level",    value: s.poultryAmmonia,           unit: "ppm",  color: s.poultryAmmonia > 20 ? colors.danger : colors.primary, compact: true },
  ];

  const duckStats = [
    { Icon: Users, label: "Ducks Active", value: duckData.count,     color: colors.info,   compact: true },
    { Icon: Egg,   label: "Duck Eggs",    value: duckData.eggsToday, color: colors.accent, compact: true },
  ];

  const beeStats = [
    { Icon: Sprout,   label: "Bee Hives",    value: beeData.hives,                    color: colors.accent, compact: true },
    { Icon: Activity, label: "Honey Stored", value: `${beeData.honeyStored}kg`,       color: colors.accent, compact: true },
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
          <Text style={cs.label}>Active Hens</Text>
          <TextInput style={cs.input} keyboardType="numeric" value={formData.hens} onChangeText={(text) => setFormData({ ...formData, hens: text })} placeholderTextColor={colors.textMuted} />

          <Text style={cs.label}>Lay Rate (%)</Text>
          <TextInput style={cs.input} keyboardType="numeric" value={formData.layRate} onChangeText={(text) => setFormData({ ...formData, layRate: text })} placeholderTextColor={colors.textMuted} />

          <Text style={cs.label}>Eggs Today</Text>
          <TextInput style={cs.input} keyboardType="numeric" value={formData.eggsToday} onChangeText={(text) => setFormData({ ...formData, eggsToday: text })} placeholderTextColor={colors.textMuted} />

          <Text style={cs.label}>Eggs Broken</Text>
          <TextInput style={cs.input} keyboardType="numeric" value={formData.eggsBroken} onChangeText={(text) => setFormData({ ...formData, eggsBroken: text })} placeholderTextColor={colors.textMuted} />

          <Text style={cs.label}>Feed Consumed (kg)</Text>
          <TextInput style={cs.input} keyboardType="numeric" value={formData.feedConsumed} onChangeText={(text) => setFormData({ ...formData, feedConsumed: text })} placeholderTextColor={colors.textMuted} />

          <Text style={cs.label}>Mortality (%)</Text>
          <TextInput style={cs.input} keyboardType="numeric" value={formData.mortality} onChangeText={(text) => setFormData({ ...formData, mortality: text })} placeholderTextColor={colors.textMuted} />

          <Text style={cs.label}>Water Usage (L)</Text>
          <TextInput style={cs.input} keyboardType="numeric" value={formData.waterUsage} onChangeText={(text) => setFormData({ ...formData, waterUsage: text })} placeholderTextColor={colors.textMuted} />
        </>
      );
    } else if (editingSection === "ducks") {
      return (
        <>
          <Text style={cs.label}>Duck Count</Text>
          <TextInput style={cs.input} keyboardType="numeric" value={formData.count} onChangeText={(text) => setFormData({ ...formData, count: text })} placeholderTextColor={colors.textMuted} />

          <Text style={cs.label}>Eggs Today</Text>
          <TextInput style={cs.input} keyboardType="numeric" value={formData.eggsToday} onChangeText={(text) => setFormData({ ...formData, eggsToday: text })} placeholderTextColor={colors.textMuted} />

          <Text style={cs.label}>Pests Consumed</Text>
          <TextInput style={cs.input} value={formData.pestsConsumed} onChangeText={(text) => setFormData({ ...formData, pestsConsumed: text })} placeholderTextColor={colors.textMuted} />

          <Text style={cs.label}>Area</Text>
          <TextInput style={cs.input} value={formData.area} onChangeText={(text) => setFormData({ ...formData, area: text })} placeholderTextColor={colors.textMuted} />
        </>
      );
    } else if (editingSection === "bees") {
      return (
        <>
          <Text style={cs.label}>Hives</Text>
          <TextInput style={cs.input} keyboardType="numeric" value={formData.hives} onChangeText={(text) => setFormData({ ...formData, hives: text })} placeholderTextColor={colors.textMuted} />

          <Text style={cs.label}>Honey Stored (kg)</Text>
          <TextInput style={cs.input} keyboardType="numeric" value={formData.honeyStored} onChangeText={(text) => setFormData({ ...formData, honeyStored: text })} placeholderTextColor={colors.textMuted} />

          <Text style={cs.label}>Active Foragers</Text>
          <TextInput style={cs.input} value={formData.activeForagers} onChangeText={(text) => setFormData({ ...formData, activeForagers: text })} placeholderTextColor={colors.textMuted} />

          <Text style={cs.label}>Last Inspection</Text>
          <TextInput style={cs.input} value={formData.lastInspection} onChangeText={(text) => setFormData({ ...formData, lastInspection: text })} placeholderTextColor={colors.textMuted} />
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
            <Text style={styles.bold}>Pest Control:</Text> {duckData.pestsConsumed ?? d.pestsConsumed} activity at {duckData.area ?? d.area}
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
          <Text style={styles.infoText}>Last inspection: {beeData.lastInspection ?? bees.lastInspection}</Text>
          <Text style={styles.infoText}>Pollination boost: +18% greenhouse yield</Text>
        </View>
      </Card>

      {/* Edit Modal */}
      <Modal visible={modalVisible} animationType="fade" transparent onRequestClose={() => setModalVisible(false)}>
        <TouchableWithoutFeedback onPress={() => setModalVisible(false)}>
          <View style={cs.modalOverlay}>
            <TouchableWithoutFeedback>
              <View style={cs.modalContent}>
                <Text style={cs.modalTitle}>{getSectionTitle()}</Text>

                <ScrollView style={cs.formScroll} showsVerticalScrollIndicator={false}>
                  {getFormFields()}
                </ScrollView>

                <View style={cs.modalButtonGroup}>
                  <TouchableOpacity onPress={() => setModalVisible(false)} style={cs.cancelButton}>
                    <Text style={cs.cancelButtonText}>Cancel</Text>
                  </TouchableOpacity>

                  <TouchableOpacity onPress={handleSave} style={cs.saveButton}>
                    <Text style={cs.saveButtonText}>Save</Text>
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
