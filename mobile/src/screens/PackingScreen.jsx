/**
 * Packing order management — list, create, start, complete orders.
 */
import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, TextInput, TouchableOpacity, ScrollView,
  ActivityIndicator, Modal,
} from "react-native";
import { Package, Plus, X, ChevronDown, Play, CheckSquare } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import StatGrid      from "../components/ui/StatGrid";
import Badge         from "../components/ui/Badge";
import { colors, spacing, radius, fontSize } from "../config/theme";
import { api }       from "../services/api";
import useAuthStore  from "../store/useAuthStore";
import { styles } from "./PackingScreen.styles";
import { commonStyles as cs } from "../styles/common";

const STATUS_COLORS = {
  pending:     colors.warn,
  in_progress: colors.info,
  completed:   colors.primary,
  cancelled:   colors.danger,
};

const REF_TYPES = ["sales_order", "transfer", "direct", "other"];

const EMPTY_FORM = { order_ref_type: "direct", notes: "", items: [{ product_id: "", quantity: "" }] };

export default function PackingScreen() {
  const token = useAuthStore((s) => s.token);

  const [orders,     setOrders]     = useState([]);
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState("");
  const [modalOpen,  setModalOpen]  = useState(false);
  const [form,       setForm]       = useState(EMPTY_FORM);
  const [saving,     setSaving]     = useState(false);
  const [formError,  setFormError]  = useState("");
  const [refOpen,    setRefOpen]    = useState(false);

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const result = await api.packing.list(token);
      setOrders(Array.isArray(result) ? result : result?.orders ?? []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { fetchOrders(); }, [fetchOrders]);

  const pending     = orders.filter((o) => o.status === "pending").length;
  const inProgress  = orders.filter((o) => o.status === "in_progress").length;
  const today       = new Date().toDateString();
  const completedToday = orders.filter((o) => o.status === "completed" && o.completed_at && new Date(o.completed_at).toDateString() === today).length;

  const stats = [
    { label: "Pending",          value: String(pending),        color: colors.warn,    icon: Package },
    { label: "In Progress",      value: String(inProgress),     color: colors.info,    icon: Package },
    { label: "Completed Today",  value: String(completedToday), color: colors.primary, icon: CheckSquare },
  ];

  const handleStart = async (id) => {
    try {
      await api.packing.start(id, token);
      fetchOrders();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleComplete = async (id) => {
    try {
      await api.packing.complete(id, token);
      fetchOrders();
    } catch (e) {
      setError(e.message);
    }
  };

  const addItem = () => setForm((f) => ({ ...f, items: [...f.items, { product_id: "", quantity: "" }] }));
  const removeItem = (idx) => setForm((f) => ({ ...f, items: f.items.filter((_, i) => i !== idx) }));
  const updateItem = (idx, key, val) =>
    setForm((f) => ({ ...f, items: f.items.map((it, i) => i === idx ? { ...it, [key]: val } : it) }));

  const handleCreate = async () => {
    if (!form.order_ref_type) { setFormError("Select a reference type."); return; }
    const validItems = form.items.filter((it) => {
      const pid = parseInt(it.product_id);
      const qty = parseFloat(it.quantity);
      return !isNaN(pid) && pid > 0 && !isNaN(qty) && qty > 0;
    });
    if (validItems.length === 0) { setFormError("Add at least one item with a valid product ID and quantity."); return; }
    setSaving(true);
    setFormError("");
    try {
      await api.packing.create({
        order_ref_type: form.order_ref_type,
        notes:          form.notes,
        items:          validItems.map((it) => ({
          product_id:        parseInt(it.product_id),
          product_name:      `Product #${it.product_id}`,
          quantity_required: parseFloat(it.quantity),
        })),
      }, token);
      setModalOpen(false);
      setForm(EMPTY_FORM);
      fetchOrders();
    } catch (e) {
      setFormError(e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <ScreenWrapper title="Packing">
      <View style={cs.topRow}>
        <Text style={cs.count}>{orders.length} orders</Text>
        <TouchableOpacity style={styles.addBtn} onPress={() => { setForm(EMPTY_FORM); setFormError(""); setModalOpen(true); }} activeOpacity={0.8}>
          <Plus size={14} color={colors.bg} />
          <Text style={styles.addBtnText}>Create Order</Text>
        </TouchableOpacity>
      </View>

      {!!error && (
        <View style={cs.errorBox}>
          <Text style={cs.errorText}>{error}</Text>
        </View>
      )}

      {loading ? (
        <ActivityIndicator size="large" color={colors.packing} style={{ marginTop: 40 }} />
      ) : (
        <>
          <Card style={cs.cardGap}>
            <SectionHeader Icon={Package} title="Packing Overview" color={colors.packing} />
            <StatGrid stats={stats} />
          </Card>

          <Card>
            <SectionHeader Icon={Package} title="Packing Orders" color={colors.primary} />
            {orders.length === 0
              ? <Text style={cs.empty}>No packing orders found</Text>
              : orders.map((order) => (
                <View key={order.id} style={styles.orderRow}>
                  <View style={styles.orderInfo}>
                    <View style={styles.orderTopRow}>
                      <Text style={styles.orderCode}>#{order.packing_order_code ?? order.id}</Text>
                      <Badge label={order.status ?? "—"} color={STATUS_COLORS[order.status] ?? colors.textMuted} />
                    </View>
                    <Text style={styles.orderMeta}>
                      {order.item_count ?? order.items?.length ?? 0} items
                      {order.scheduled_date ? ` • Due ${order.scheduled_date}` : ""}
                      {order.order_ref_type ? ` • ${order.order_ref_type}` : ""}
                    </Text>
                  </View>
                  <View style={styles.orderActions}>
                    {order.status === "pending" && (
                      <TouchableOpacity style={[styles.actionBtn, { borderColor: colors.info }]} onPress={() => handleStart(order.id)} activeOpacity={0.8}>
                        <Play size={12} color={colors.info} />
                        <Text style={[styles.actionBtnText, { color: colors.info }]}>Start</Text>
                      </TouchableOpacity>
                    )}
                    {order.status === "in_progress" && (
                      <TouchableOpacity style={[styles.actionBtn, { borderColor: colors.primary }]} onPress={() => handleComplete(order.id)} activeOpacity={0.8}>
                        <CheckSquare size={12} color={colors.primary} />
                        <Text style={[styles.actionBtnText, { color: colors.primary }]}>Complete</Text>
                      </TouchableOpacity>
                    )}
                  </View>
                </View>
              ))
            }
          </Card>
        </>
      )}

      {/* Create Modal */}
      <Modal visible={modalOpen} transparent animationType="fade" onRequestClose={() => setModalOpen(false)}>
        <View style={cs.modalOverlayCentered}>
          <View style={cs.modalCard}>
            <View style={styles.modalHeader}>
              <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.sm }}>
                <Package size={16} color={colors.packing} />
                <Text style={styles.modalTitleText}>Create Packing Order</Text>
              </View>
              <TouchableOpacity onPress={() => setModalOpen(false)} hitSlop={{ top: 8, right: 8, bottom: 8, left: 8 }}>
                <X size={18} color={colors.textDim} />
              </TouchableOpacity>
            </View>

            <ScrollView showsVerticalScrollIndicator={false}>
              {!!formError && (
                <View style={cs.errorBox}>
                  <Text style={cs.errorText}>{formError}</Text>
                </View>
              )}

              <Text style={cs.label}>Reference Type</Text>
              <TouchableOpacity style={styles.picker} onPress={() => setRefOpen((v) => !v)} activeOpacity={0.8}>
                <Text style={{ color: colors.text, fontSize: fontSize.base }}>{form.order_ref_type}</Text>
                <ChevronDown size={14} color={colors.textDim} />
              </TouchableOpacity>
              {refOpen && (
                <View style={styles.pickerList}>
                  {REF_TYPES.map((r) => (
                    <TouchableOpacity key={r} style={[styles.pickerItem, r === form.order_ref_type && styles.pickerItemActive]}
                      onPress={() => { setForm((f) => ({ ...f, order_ref_type: r })); setRefOpen(false); }}>
                      <Text style={{ color: r === form.order_ref_type ? colors.primary : colors.textDim, fontSize: fontSize.md }}>{r}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              )}

              <Text style={cs.label}>Notes</Text>
              <TextInput
                style={[cs.input, { height: 60 }]}
                value={form.notes}
                onChangeText={(v) => setForm((f) => ({ ...f, notes: v }))}
                placeholder="Optional notes..."
                placeholderTextColor={colors.textMuted}
                multiline
              />

              <Text style={cs.label}>Items</Text>
              {form.items.map((item, idx) => (
                <View key={idx} style={styles.itemRow}>
                  <TextInput
                    style={[cs.input, { flex: 2 }]}
                    value={item.product_id}
                    onChangeText={(v) => updateItem(idx, "product_id", v)}
                    placeholder="Product ID"
                    placeholderTextColor={colors.textMuted}
                    keyboardType="numeric"
                  />
                  <TextInput
                    style={[cs.input, { flex: 1 }]}
                    value={item.quantity}
                    onChangeText={(v) => updateItem(idx, "quantity", v)}
                    placeholder="Qty"
                    placeholderTextColor={colors.textMuted}
                    keyboardType="numeric"
                  />
                  {form.items.length > 1 && (
                    <TouchableOpacity onPress={() => removeItem(idx)} style={styles.removeBtn}>
                      <X size={14} color={colors.danger} />
                    </TouchableOpacity>
                  )}
                </View>
              ))}
              <TouchableOpacity style={styles.addItemBtn} onPress={addItem} activeOpacity={0.8}>
                <Plus size={12} color={colors.packing} />
                <Text style={{ color: colors.packing, fontSize: fontSize.md }}>Add Item</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.saveBtn, saving && { opacity: 0.6 }]}
                onPress={handleCreate}
                disabled={saving}
                activeOpacity={0.85}
              >
                {saving ? <ActivityIndicator size="small" color={colors.bg} /> : <Text style={styles.saveBtnText}>Create Order</Text>}
              </TouchableOpacity>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </ScreenWrapper>
  );
}
