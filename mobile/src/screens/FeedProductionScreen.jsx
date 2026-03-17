import React, { useState, useCallback, useEffect } from "react";
import {
  View, Text, ScrollView, TouchableOpacity,
  Modal, TextInput, ActivityIndicator, RefreshControl,
} from "react-native";
import { Bug, Leaf, Droplets, Package, BarChart2, Plus, Edit2, Trash2, X, ChevronDown } from "lucide-react-native";
import useAuthStore from "../store/useAuthStore";
import { api } from "../services/api";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import { colors } from "../config/theme";
import { styles } from "./FeedProductionScreen.styles";
import { commonStyles as cs } from "../styles/common";

const TABS = ["BSF", "Azolla", "Duckweed", "Feed Mill", "Inventory"];

export default function FeedProductionScreen() {
  const token = useAuthStore((s) => s.token);
  const user = useAuthStore((s) => s.user);
  const canEdit = user?.role && ["ADMIN", "MANAGER", "SUPERVISOR"].includes(user.role);

  const [activeTab, setActiveTab] = useState("BSF");
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState({ bsf: [], azolla: [], duckweed: [], batches: [], inventory: [], sufficiency: null });
  const [modal, setModal] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [form, setForm] = useState({});
  const [saving, setSaving] = useState(false);

  const fetchAll = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const [bsf, azolla, duckweed, batches, inventory, sufficiency] = await Promise.all([
        api.feedProduction.bsf.list(token),
        api.feedProduction.azolla.list(token),
        api.feedProduction.duckweed.list(token),
        api.feedProduction.batches.list(token),
        api.feedProduction.inventory.list(token),
        api.feedProduction.selfSufficiency(token),
      ]);
      setData({ bsf, azolla, duckweed, batches, inventory, sufficiency });
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
      BSF: { batch_code: "", colony_stage: "egg", substrate_type: "kitchen_waste", daily_yield_kg: "0", moisture_pct: "60", larvae_age_days: "0", colony_health: "good" },
      Azolla: { bed_id: "", log_date: new Date().toISOString().split("T")[0], harvest_kg: "0", moisture_pct: "90", protein_pct: "25", area_sqm: "0" },
      Duckweed: { pond_id: "", log_date: new Date().toISOString().split("T")[0], yield_kg: "0", water_tds: "0", ph: "7", allocated_to: "fish" },
      "Feed Mill": { batch_code: "", formulation: "", date_produced: new Date().toISOString().split("T")[0], quantity_kg: "0", moisture_pct: "12", protein_pct: "28", aflatoxin_ppb: "0", pellet_durability_pct: "98", target_species: "fish", passed_qa: "true" },
      Inventory: { feed_type: "", quantity_kg: "0", unit_cost_per_kg: "0", source: "on-farm", received_date: new Date().toISOString().split("T")[0] },
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
      const numKeys = ["daily_yield_kg", "moisture_pct", "larvae_age_days", "harvest_kg", "protein_pct", "area_sqm", "yield_kg", "water_tds", "ph", "quantity_kg", "unit_cost_per_kg", "aflatoxin_ppb", "pellet_durability_pct"];
      const payload = { ...form };
      numKeys.forEach((k) => {
        if (payload[k] !== undefined) payload[k] = Number(payload[k]);
      });
      if (payload.passed_qa !== undefined) payload.passed_qa = payload.passed_qa === "true" || payload.passed_qa === true;

      if (activeTab === "BSF") {
        if (editItem) await api.feedProduction.bsf.update(editItem.id, payload, token);
        else await api.feedProduction.bsf.create(payload, token);
      } else if (activeTab === "Azolla") {
        await api.feedProduction.azolla.create(payload, token);
      } else if (activeTab === "Duckweed") {
        await api.feedProduction.duckweed.create(payload, token);
      } else if (activeTab === "Feed Mill") {
        await api.feedProduction.batches.create(payload, token);
      } else if (activeTab === "Inventory") {
        await api.feedProduction.inventory.create(payload, token);
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
      if (activeTab === "BSF") await api.feedProduction.bsf.delete(item.id, token);
      else if (activeTab === "Feed Mill") await api.feedProduction.batches.delete(item.id, token);
      else if (activeTab === "Inventory") await api.feedProduction.inventory.delete(item.id, token);
      fetchAll();
    } catch (e) {
      setError(e.message);
    }
  };

  const renderContent = () => {
    if (loading) return <ActivityIndicator color={colors.primary} style={{ marginTop: 40 }} />;
    switch (activeTab) {
      case "BSF":
        return (
          <Card>
            <SectionHeader Icon={Bug} title={`BSF Colonies (${data.bsf.length})`} action={canEdit && <TouchableOpacity onPress={openCreate}><Plus size={18} color={colors.primary} /></TouchableOpacity>} />
            {data.bsf.length === 0 && <Text style={styles.empty}>No BSF colonies recorded</Text>}
            {data.bsf.map((c) => (
              <View key={c.id} style={cs.row}>
                <View style={styles.rowLeft}>
                  <Text style={styles.rowTitle}>{c.batch_code}</Text>
                  <Text style={styles.rowSub}>Stage: {c.colony_stage} • Health: {c.colony_health}</Text>
                  <Text style={styles.rowSub}>Yield: {c.daily_yield_kg} kg/day • Age: {c.larvae_age_days} days</Text>
                </View>
                {canEdit && (
                  <View style={styles.rowActions}>
                    <TouchableOpacity onPress={() => openEdit(c)}><Edit2 size={16} color={colors.textDim} /></TouchableOpacity>
                    <TouchableOpacity onPress={() => handleDelete(c)} style={{ marginLeft: 8 }}><Trash2 size={16} color={colors.danger} /></TouchableOpacity>
                  </View>
                )}
              </View>
            ))}
          </Card>
        );
      case "Azolla":
        return (
          <Card>
            <SectionHeader Icon={Leaf} title={`Azolla Logs (${data.azolla.length})`} action={canEdit && <TouchableOpacity onPress={openCreate}><Plus size={18} color={colors.primary} /></TouchableOpacity>} />
            {data.azolla.length === 0 && <Text style={styles.empty}>No Azolla logs</Text>}
            {data.azolla.map((l) => (
              <View key={l.id} style={cs.row}>
                <View style={styles.rowLeft}>
                  <Text style={styles.rowTitle}>{l.log_date} — Bed {l.bed_id}</Text>
                  <Text style={styles.rowSub}>Harvest: {l.harvest_kg} kg • Protein: {l.protein_pct}% • Area: {l.area_sqm} m²</Text>
                </View>
              </View>
            ))}
          </Card>
        );
      case "Duckweed":
        return (
          <Card>
            <SectionHeader Icon={Droplets} title={`Duckweed Logs (${data.duckweed.length})`} action={canEdit && <TouchableOpacity onPress={openCreate}><Plus size={18} color={colors.primary} /></TouchableOpacity>} />
            {data.duckweed.length === 0 && <Text style={styles.empty}>No Duckweed logs</Text>}
            {data.duckweed.map((l) => (
              <View key={l.id} style={cs.row}>
                <View style={styles.rowLeft}>
                  <Text style={styles.rowTitle}>{l.log_date} — Pond {l.pond_id}</Text>
                  <Text style={styles.rowSub}>Yield: {l.yield_kg} kg • pH: {l.ph} • TDS: {l.water_tds} ppm • For: {l.allocated_to}</Text>
                </View>
              </View>
            ))}
          </Card>
        );
      case "Feed Mill":
        return (
          <Card>
            <SectionHeader Icon={Package} title={`Feed Mill Batches (${data.batches.length})`} action={canEdit && <TouchableOpacity onPress={openCreate}><Plus size={18} color={colors.primary} /></TouchableOpacity>} />
            {data.batches.length === 0 && <Text style={styles.empty}>No feed mill batches</Text>}
            {data.batches.map((b) => (
              <View key={b.id} style={cs.row}>
                <View style={styles.rowLeft}>
                  <Text style={styles.rowTitle}>{b.batch_code} — {b.date_produced}</Text>
                  <Text style={styles.rowSub}>{b.formulation}</Text>
                  <Text style={styles.rowSub}>{b.quantity_kg} kg • Protein: {b.protein_pct}% • QA: {b.passed_qa ? "✓ Pass" : "✗ Fail"}</Text>
                </View>
                {canEdit && (
                  <TouchableOpacity onPress={() => handleDelete(b)} style={{ marginLeft: 8 }}><Trash2 size={16} color={colors.danger} /></TouchableOpacity>
                )}
              </View>
            ))}
          </Card>
        );
      case "Inventory":
        return (
          <>
            {data.sufficiency && (
              <Card>
                <SectionHeader Icon={BarChart2} title="Feed Self-Sufficiency" />
                <View style={styles.suffRow}>
                  <View style={[styles.suffBox, { backgroundColor: colors.primaryDim }]}>
                    <Text style={styles.suffPct}>{data.sufficiency.on_farm_pct}%</Text>
                    <Text style={styles.suffLabel}>On-Farm</Text>
                  </View>
                  <View style={[styles.suffBox, { backgroundColor: colors.dangerDim }]}>
                    <Text style={styles.suffPct}>{data.sufficiency.purchased_pct}%</Text>
                    <Text style={styles.suffLabel}>Purchased</Text>
                  </View>
                </View>
              </Card>
            )}
            <Card>
              <SectionHeader Icon={Package} title={`Feed Inventory (${data.inventory.length})`} action={canEdit && <TouchableOpacity onPress={openCreate}><Plus size={18} color={colors.primary} /></TouchableOpacity>} />
              {data.inventory.length === 0 && <Text style={styles.empty}>No inventory records</Text>}
              {data.inventory.map((i) => (
                <View key={i.id} style={cs.row}>
                  <View style={styles.rowLeft}>
                    <Text style={styles.rowTitle}>{i.feed_type}</Text>
                    <Text style={styles.rowSub}>{i.quantity_kg} kg • ₹{i.unit_cost_per_kg}/kg • {i.source}</Text>
                    <Text style={styles.rowSub}>Received: {i.received_date}{i.expiry_date ? ` • Expires: ${i.expiry_date}` : ""}</Text>
                  </View>
                  {canEdit && (
                    <TouchableOpacity onPress={() => handleDelete(i)}><Trash2 size={16} color={colors.danger} /></TouchableOpacity>
                  )}
                </View>
              ))}
            </Card>
          </>
        );
      default:
        return null;
    }
  };

  const formFields = {
    BSF: [
      { key: "batch_code", label: "Batch Code", edit: false },
      { key: "colony_stage", label: "Stage (egg/larvae/prepupae/pupae)" },
      { key: "substrate_type", label: "Substrate Type" },
      { key: "daily_yield_kg", label: "Daily Yield (kg)", numeric: true },
      { key: "moisture_pct", label: "Moisture %", numeric: true },
      { key: "larvae_age_days", label: "Larvae Age (days)", numeric: true },
      { key: "colony_health", label: "Health (good/fair/poor)" },
      { key: "notes", label: "Notes", multiline: true },
    ],
    Azolla: [
      { key: "bed_id", label: "Bed ID" },
      { key: "log_date", label: "Date (YYYY-MM-DD)" },
      { key: "harvest_kg", label: "Harvest (kg)", numeric: true },
      { key: "moisture_pct", label: "Moisture %", numeric: true },
      { key: "protein_pct", label: "Protein %", numeric: true },
      { key: "area_sqm", label: "Area (m²)", numeric: true },
      { key: "notes", label: "Notes", multiline: true },
    ],
    Duckweed: [
      { key: "pond_id", label: "Pond ID" },
      { key: "log_date", label: "Date (YYYY-MM-DD)" },
      { key: "yield_kg", label: "Yield (kg)", numeric: true },
      { key: "water_tds", label: "Water TDS (ppm)", numeric: true },
      { key: "ph", label: "pH", numeric: true },
      { key: "allocated_to", label: "Allocated To (fish/poultry)" },
      { key: "notes", label: "Notes", multiline: true },
    ],
    "Feed Mill": [
      { key: "batch_code", label: "Batch Code" },
      { key: "formulation", label: "Formulation (e.g. BSF30-Soya70)" },
      { key: "date_produced", label: "Date Produced (YYYY-MM-DD)" },
      { key: "quantity_kg", label: "Quantity (kg)", numeric: true },
      { key: "moisture_pct", label: "Moisture %", numeric: true },
      { key: "protein_pct", label: "Protein %", numeric: true },
      { key: "aflatoxin_ppb", label: "Aflatoxin (ppb)", numeric: true },
      { key: "pellet_durability_pct", label: "Pellet Durability %", numeric: true },
      { key: "target_species", label: "Target Species (fish/poultry)" },
      { key: "passed_qa", label: "Passed QA (true/false)" },
      { key: "notes", label: "Notes", multiline: true },
    ],
    Inventory: [
      { key: "feed_type", label: "Feed Type (e.g. bsf_larvae, azolla, purchased_pellet)" },
      { key: "quantity_kg", label: "Quantity (kg)", numeric: true },
      { key: "unit_cost_per_kg", label: "Cost per kg (₹)", numeric: true },
      { key: "source", label: "Source (on-farm / supplier name)" },
      { key: "received_date", label: "Received Date (YYYY-MM-DD)" },
      { key: "expiry_date", label: "Expiry Date (YYYY-MM-DD, optional)" },
      { key: "batch_code", label: "Batch Code (optional)" },
      { key: "notes", label: "Notes", multiline: true },
    ],
  };

  return (
    <ScreenWrapper title="Feed Production">
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={cs.tabBar} contentContainerStyle={styles.tabBarContent}>
        {TABS.map((t) => (
          <TouchableOpacity key={t} style={[cs.tab, activeTab === t && cs.tabActive]} onPress={() => setActiveTab(t)}>
            <Text style={[cs.tabText, activeTab === t && cs.tabActiveText]}>{t}</Text>
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
                      style={[cs.input, f.multiline && styles.inputMulti]}
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
