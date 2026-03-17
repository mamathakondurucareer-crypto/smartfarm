import { useState, useEffect, useCallback } from "react";
import { Alert } from "react-native";
import useAuthStore from "../../store/useAuthStore";
import { api } from "../../services/api";

export const useNurseryBackendScreen = () => {
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
    const statusColorMap = {
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
    return statusColorMap[status] || "#757575";
  };

  const calculateMonthlyRevenue = () => {
    const now = new Date();
    const currentMonth =
      now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0");
    return orders
      .filter((o) => o.order_date.startsWith(currentMonth))
      .reduce((sum, o) => sum + o.total_amount, 0);
  };

  const handleOpenBatchModal = (mode, item = null) => {
    setModalMode(mode);
    if (mode === "edit" && item) {
      setSelectedItem(item);
      setFormData(item);
    } else {
      setFormData({});
      setSelectedItem(null);
    }
    setModalVisible(true);
  };

  const handleOpenOrderModal = (mode, item = null) => {
    setModalMode(mode);
    if (mode === "edit" && item) {
      setSelectedItem(item);
      setFormData(item);
    } else {
      setFormData({});
      setSelectedItem(null);
    }
    setModalVisible(true);
  };

  const handleModalSubmit = async () => {
    if (tab === "batches") {
      if (modalMode === "create") {
        await handleCreateBatch();
      } else {
        await handleUpdateBatch();
      }
    } else if (tab === "orders") {
      if (modalMode === "create") {
        await handleCreateOrder();
      } else {
        await handleUpdateOrder();
      }
    }
  };

  return {
    // State
    tab,
    setTab,
    loading,
    refreshing,
    batches,
    batchesSummary,
    orders,
    modalVisible,
    setModalVisible,
    modalMode,
    formData,
    setFormData,
    selectedItem,
    fieldsByTab,
    // Handlers
    onRefresh,
    handleCreateBatch,
    handleUpdateBatch,
    handleDeleteBatch,
    handleCreateOrder,
    handleUpdateOrder,
    handleDeleteOrder,
    getStatusColor,
    calculateMonthlyRevenue,
    handleOpenBatchModal,
    handleOpenOrderModal,
    handleModalSubmit,
  };
};
