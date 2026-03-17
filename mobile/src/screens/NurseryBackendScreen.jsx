import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Modal,
  FlatList,
  ActivityIndicator,
  Alert,
  TextInput,
} from "react-native";
import useAuthStore from "../store/useAuthStore";
import { api } from "../services/api";
import { Sprout, ShoppingCart } from "lucide-react-native";

const NurseryBackendScreen = () => {
  const token = useAuthStore((state) => state.token);
  const [tab, setTab] = useState("batches");
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Batches state
  const [batches, setBatches] = useState([]);
  const [batchesSummary, setBatchesSummary] = useState(null);

  // Orders state
  const [orders, setOrders] = useState([]);

  // Modal state
  const [modalVisible, setModalVisible] = useState(false);
  const [modalMode, setModalMode] = useState("create"); // create/edit
  const [formData, setFormData] = useState({});
  const [selectedItem, setSelectedItem] = useState(null);

  // Field definitions per tab
  const fieldsByTab = {
    batches: [
      { key: "batch_code", label: "Batch Code", type: "text" },
      { key: "species", label: "Species", type: "text" },
      { key: "category", label: "Category", type: "text" },
      { key: "sowing_date", label: "Sowing Date", type: "date" },
      { key: "expected_ready_date", label: "Expected Ready Date", type: "date" },
      { key: "tray_count", label: "Tray Count", type: "number" },
      { key: "cells_per_tray", label: "Cells Per Tray", type: "number" },
      { key: "germination_pct", label: "Germination %", type: "number" },
      { key: "seedlings_ready", label: "Seedlings Ready", type: "number" },
      { key: "status", label: "Status", type: "text" },
      { key: "notes", label: "Notes", type: "text" },
    ],
    orders: [
      { key: "batch_id", label: "Batch ID", type: "number" },
      { key: "buyer_name", label: "Buyer Name", type: "text" },
      { key: "buyer_contact", label: "Buyer Contact", type: "text" },
      { key: "species", label: "Species", type: "text" },
      { key: "quantity", label: "Quantity", type: "number" },
      { key: "price_per_seedling", label: "Price per Seedling", type: "number" },
      { key: "order_date", label: "Order Date", type: "date" },
      { key: "dispatch_date", label: "Dispatch Date", type: "date" },
      { key: "status", label: "Status", type: "text" },
      { key: "notes", label: "Notes", type: "text" },
    ],
  };

  const fetchAll = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [batchesData, summaryData, ordersData] = await Promise.all([
        api.nursery.batches.list(token),
        api.nursery.batches.summary(token),
        api.nursery.orders.list(token),
      ]);
      setBatches(batchesData || []);
      setBatchesSummary(summaryData || null);
      setOrders(ordersData || []);
    } catch (err) {
      console.error("Fetch error:", err);
      Alert.alert("Error", "Failed to load nursery data");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchAll();
    setRefreshing(false);
  };

  const handleCreateBatch = async () => {
    try {
      const newBatch = await api.nursery.batches.create(formData, token);
      setBatches([newBatch, ...batches]);
      setModalVisible(false);
      setFormData({});
      Alert.alert("Success", "Batch created");
      await fetchAll();
    } catch (err) {
      Alert.alert("Error", err.response?.data?.detail || "Failed to create batch");
    }
  };

  const handleUpdateBatch = async () => {
    try {
      const updated = await api.nursery.batches.update(
        selectedItem.id,
        formData,
        token
      );
      setBatches(batches.map((b) => (b.id === selectedItem.id ? updated : b)));
      setModalVisible(false);
      setFormData({});
      setSelectedItem(null);
      Alert.alert("Success", "Batch updated");
      await fetchAll();
    } catch (err) {
      Alert.alert("Error", err.response?.data?.detail || "Failed to update batch");
    }
  };

  const handleDeleteBatch = async (batchId) => {
    Alert.alert("Confirm", "Delete this batch?", [
      { text: "Cancel" },
      {
        text: "Delete",
        onPress: async () => {
          try {
            await api.nursery.batches.delete(batchId, token);
            setBatches(batches.filter((b) => b.id !== batchId));
            Alert.alert("Success", "Batch deleted");
            await fetchAll();
          } catch (err) {
            Alert.alert(
              "Error",
              err.response?.data?.detail || "Failed to delete batch"
            );
          }
        },
      },
    ]);
  };

  const handleCreateOrder = async () => {
    try {
      const newOrder = await api.nursery.orders.create(formData, token);
      setOrders([newOrder, ...orders]);
      setModalVisible(false);
      setFormData({});
      Alert.alert("Success", "Order created");
    } catch (err) {
      Alert.alert("Error", err.response?.data?.detail || "Failed to create order");
    }
  };

  const handleUpdateOrder = async () => {
    try {
      const updated = await api.nursery.orders.update(
        selectedItem.id,
        formData,
        token
      );
      setOrders(orders.map((o) => (o.id === selectedItem.id ? updated : o)));
      setModalVisible(false);
      setFormData({});
      setSelectedItem(null);
      Alert.alert("Success", "Order updated");
    } catch (err) {
      Alert.alert("Error", err.response?.data?.detail || "Failed to update order");
    }
  };

  const handleDeleteOrder = async (orderId) => {
    Alert.alert("Confirm", "Delete this order?", [
      { text: "Cancel" },
      {
        text: "Delete",
        onPress: async () => {
          try {
            await api.nursery.orders.delete(orderId, token);
            setOrders(orders.filter((o) => o.id !== orderId));
            Alert.alert("Success", "Order deleted");
          } catch (err) {
            Alert.alert(
              "Error",
              err.response?.data?.detail || "Failed to delete order"
            );
          }
        },
      },
    ]);
  };

  const getStatusColor = (status) => {
    const colors = {
      sown: "#FFC107",
      germinated: "#FF9800",
      hardening: "#2196F3",
      ready: "#4CAF50",
      dispatched: "#9C27B0",
      pending: "#FFC107",
      confirmed: "#2196F3",
      delivered: "#4CAF50",
      cancelled: "#FF5722",
    };
    return colors[status] || "#757575";
  };

  const calculateMonthlyRevenue = () => {
    const now = new Date();
    const currentMonth = now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0");
    return orders
      .filter((o) => o.order_date.startsWith(currentMonth))
      .reduce((sum, o) => sum + o.total_amount, 0);
  };

  const renderBatchesSummary = () => {
    if (!batchesSummary) return null;
    const capacityUsed = batchesSummary.total_capacity
      ? ((batchesSummary.total_ready / batchesSummary.total_capacity) * 100).toFixed(1)
      : 0;
    return (
      <View style={styles.summaryCard}>
        <View style={styles.summaryItem}>
          <Text style={styles.summaryLabel}>Total Batches</Text>
          <Text style={styles.summaryValue}>{batchesSummary.total_batches}</Text>
        </View>
        <View style={styles.summaryItem}>
          <Text style={styles.summaryLabel}>Seedlings Ready</Text>
          <Text style={styles.summaryValue}>
            {batchesSummary.total_ready}
          </Text>
        </View>
        <View style={styles.summaryItem}>
          <Text style={styles.summaryLabel}>Capacity Used</Text>
          <Text style={styles.summaryValue}>{capacityUsed}%</Text>
        </View>
      </View>
    );
  };

  const renderBatchesTab = () => (
    <View style={styles.tabContent}>
      {renderBatchesSummary()}

      <TouchableOpacity
        style={styles.addButton}
        onPress={() => {
          setModalMode("create");
          setFormData({});
          setSelectedItem(null);
          setModalVisible(true);
        }}
      >
        <Text style={styles.addButtonText}>+ Add Batch</Text>
      </TouchableOpacity>

      <FlatList
        data={batches}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View
            style={[
              styles.listItem,
              { borderLeftColor: getStatusColor(item.status) },
            ]}
          >
            <View style={styles.listItemContent}>
              <View style={styles.listItemHeader}>
                <Sprout size={20} color={getStatusColor(item.status)} />
                <Text style={styles.listItemTitle}>{item.batch_code}</Text>
              </View>
              <Text style={styles.listItemSubtitle}>{item.species}</Text>
              <View style={styles.listItemRow}>
                <Text style={styles.listItemText}>
                  Ready: {item.seedlings_ready}
                </Text>
                <View
                  style={[
                    styles.statusBadge,
                    { backgroundColor: getStatusColor(item.status) },
                  ]}
                >
                  <Text style={styles.statusText}>{item.status}</Text>
                </View>
              </View>
              <Text style={styles.listItemMeta}>
                Germination: {item.germination_pct}%
              </Text>
              <Text style={styles.listItemMeta}>
                Sown: {item.sowing_date}
              </Text>
              <View style={styles.actionButtons}>
                <TouchableOpacity
                  style={[styles.smallButton, styles.editButton]}
                  onPress={() => {
                    setSelectedItem(item);
                    setFormData(item);
                    setModalMode("edit");
                    setModalVisible(true);
                  }}
                >
                  <Text style={styles.smallButtonText}>Edit</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.smallButton, styles.deleteButton]}
                  onPress={() => handleDeleteBatch(item.id)}
                >
                  <Text style={styles.smallButtonText}>Delete</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        )}
        scrollEnabled={false}
        refreshing={refreshing}
        onRefresh={onRefresh}
      />
    </View>
  );

  const renderOrdersTab = () => (
    <View style={styles.tabContent}>
      <View style={styles.revenueCard}>
        <Text style={styles.revenueLabel}>Monthly Revenue (Current)</Text>
        <Text style={styles.revenueValue}>
          ₹{calculateMonthlyRevenue().toFixed(2)}
        </Text>
      </View>

      <TouchableOpacity
        style={styles.addButton}
        onPress={() => {
          setModalMode("create");
          setFormData({});
          setSelectedItem(null);
          setModalVisible(true);
        }}
      >
        <Text style={styles.addButtonText}>+ Add Order</Text>
      </TouchableOpacity>

      <FlatList
        data={orders}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View
            style={[
              styles.listItem,
              { borderLeftColor: getStatusColor(item.status) },
            ]}
          >
            <View style={styles.listItemContent}>
              <View style={styles.listItemHeader}>
                <ShoppingCart size={20} color={getStatusColor(item.status)} />
                <Text style={styles.listItemTitle}>{item.buyer_name}</Text>
              </View>
              <Text style={styles.listItemSubtitle}>{item.species}</Text>
              <View style={styles.listItemRow}>
                <Text style={styles.listItemText}>
                  Qty: {item.quantity}
                </Text>
                <Text style={styles.listItemText}>
                  ₹{item.total_amount.toFixed(2)}
                </Text>
              </View>
              <View style={styles.listItemRow}>
                <Text style={styles.listItemMeta}>{item.order_date}</Text>
                <View
                  style={[
                    styles.statusBadge,
                    { backgroundColor: getStatusColor(item.status) },
                  ]}
                >
                  <Text style={styles.statusText}>{item.status}</Text>
                </View>
              </View>
              <View style={styles.actionButtons}>
                <TouchableOpacity
                  style={[styles.smallButton, styles.editButton]}
                  onPress={() => {
                    setSelectedItem(item);
                    setFormData(item);
                    setModalMode("edit");
                    setModalVisible(true);
                  }}
                >
                  <Text style={styles.smallButtonText}>Edit</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.smallButton, styles.deleteButton]}
                  onPress={() => handleDeleteOrder(item.id)}
                >
                  <Text style={styles.smallButtonText}>Delete</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        )}
        scrollEnabled={false}
        refreshing={refreshing}
        onRefresh={onRefresh}
      />
    </View>
  );

  const renderModal = () => {
    const fields = fieldsByTab[tab];
    return (
      <Modal
        visible={modalVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>
              {modalMode === "create"
                ? `New ${tab === "batches" ? "Batch" : "Order"}`
                : `Edit ${tab === "batches" ? "Batch" : "Order"}`}
            </Text>
            <ScrollView style={styles.modalScroll}>
              {fields.map((field) => (
                <View key={field.key}>
                  <Text style={styles.fieldLabel}>{field.label}</Text>
                  <TextInput
                    style={styles.fieldInput}
                    placeholder={field.label}
                    keyboardType={
                      field.type === "number" ? "decimal-pad" : "default"
                    }
                    value={String(formData[field.key] || "")}
                    onChangeText={(val) =>
                      setFormData({ ...formData, [field.key]: val })
                    }
                  />
                </View>
              ))}
            </ScrollView>
            <View style={styles.modalActions}>
              <TouchableOpacity
                style={[styles.button, styles.cancelButton]}
                onPress={() => setModalVisible(false)}
              >
                <Text style={styles.buttonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.button, styles.submitButton]}
                onPress={() => {
                  if (tab === "batches") {
                    if (modalMode === "create") {
                      handleCreateBatch();
                    } else {
                      handleUpdateBatch();
                    }
                  } else if (tab === "orders") {
                    if (modalMode === "create") {
                      handleCreateOrder();
                    } else {
                      handleUpdateOrder();
                    }
                  }
                }}
              >
                <Text style={styles.buttonText}>
                  {modalMode === "create" ? "Create" : "Update"}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Nursery Management</Text>
      </View>

      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tabButton, tab === "batches" && styles.tabActive]}
          onPress={() => setTab("batches")}
        >
          <Text
            style={[
              styles.tabButtonText,
              tab === "batches" && styles.tabActiveText,
            ]}
          >
            Batches
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tabButton, tab === "orders" && styles.tabActive]}
          onPress={() => setTab("orders")}
        >
          <Text
            style={[
              styles.tabButtonText,
              tab === "orders" && styles.tabActiveText,
            ]}
          >
            Orders
          </Text>
        </TouchableOpacity>
      </View>

      {loading && !refreshing ? (
        <View style={styles.centerContent}>
          <ActivityIndicator size="large" color="#2196F3" />
        </View>
      ) : (
        <ScrollView style={styles.scrollView} scrollEventThrottle={16}>
          {tab === "batches" && renderBatchesTab()}
          {tab === "orders" && renderOrdersTab()}
        </ScrollView>
      )}

      {renderModal()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
  },
  header: {
    backgroundColor: "#2196F3",
    paddingHorizontal: 16,
    paddingVertical: 16,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#fff",
  },
  tabBar: {
    flexDirection: "row",
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0",
  },
  tabButton: {
    flex: 1,
    paddingVertical: 12,
    alignItems: "center",
  },
  tabActive: {
    borderBottomWidth: 3,
    borderBottomColor: "#2196F3",
  },
  tabButtonText: {
    fontSize: 14,
    color: "#666",
    fontWeight: "500",
  },
  tabActiveText: {
    color: "#2196F3",
  },
  scrollView: {
    flex: 1,
  },
  tabContent: {
    padding: 16,
  },
  summaryCard: {
    backgroundColor: "#fff",
    borderRadius: 8,
    flexDirection: "row",
    marginBottom: 16,
    padding: 12,
    borderLeftWidth: 4,
    borderLeftColor: "#4CAF50",
  },
  summaryItem: {
    flex: 1,
    alignItems: "center",
  },
  summaryLabel: {
    fontSize: 12,
    color: "#666",
    marginBottom: 4,
  },
  summaryValue: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#4CAF50",
  },
  revenueCard: {
    backgroundColor: "#fff",
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: "#2196F3",
    alignItems: "center",
  },
  revenueLabel: {
    fontSize: 12,
    color: "#666",
    marginBottom: 8,
  },
  revenueValue: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#2196F3",
  },
  addButton: {
    backgroundColor: "#4CAF50",
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginBottom: 16,
    alignItems: "center",
  },
  addButtonText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 14,
  },
  listItem: {
    backgroundColor: "#fff",
    padding: 12,
    marginBottom: 12,
    borderRadius: 8,
    borderLeftWidth: 4,
  },
  listItemContent: {
    flex: 1,
  },
  listItemHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },
  listItemTitle: {
    fontSize: 16,
    fontWeight: "bold",
    marginLeft: 8,
    flex: 1,
  },
  listItemSubtitle: {
    fontSize: 13,
    color: "#666",
    marginBottom: 8,
  },
  listItemRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 8,
  },
  listItemText: {
    fontSize: 13,
    color: "#555",
  },
  listItemMeta: {
    fontSize: 12,
    color: "#999",
    marginBottom: 4,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  statusText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "bold",
  },
  actionButtons: {
    flexDirection: "row",
    marginTop: 12,
  },
  smallButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 6,
    alignItems: "center",
    marginHorizontal: 4,
  },
  editButton: {
    backgroundColor: "#FF9800",
  },
  deleteButton: {
    backgroundColor: "#FF5722",
  },
  smallButtonText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 12,
  },
  centerContent: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    justifyContent: "flex-end",
  },
  modalContent: {
    backgroundColor: "#fff",
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
    maxHeight: "85%",
    paddingTop: 16,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: "bold",
    marginHorizontal: 16,
    marginBottom: 12,
    color: "#333",
  },
  modalScroll: {
    paddingHorizontal: 16,
    maxHeight: 400,
  },
  fieldLabel: {
    fontSize: 13,
    fontWeight: "bold",
    color: "#333",
    marginTop: 12,
    marginBottom: 6,
  },
  fieldInput: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 6,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
    backgroundColor: "#fafafa",
  },
  modalActions: {
    flexDirection: "row",
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: "#e0e0e0",
  },
  button: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: "center",
    marginHorizontal: 8,
  },
  cancelButton: {
    backgroundColor: "#e0e0e0",
  },
  submitButton: {
    backgroundColor: "#2196F3",
  },
  buttonText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 14,
  },
});

export default NurseryBackendScreen;
