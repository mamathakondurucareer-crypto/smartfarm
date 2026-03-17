import { useState, useEffect, useCallback } from "react";
import { Alert } from "react-native";
import useAuthStore from "../../store/useAuthStore";
import { api } from "../../services/api";

export const useQAScreen = () => {
  const token = useAuthStore((s) => s.token);

  // Tab state
  const [tab, setTab] = useState("lots");
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Lots state
  const [lots, setLots] = useState([]);
  const [selectedLot, setSelectedLot] = useState(null);
  const [traceDetails, setTraceDetails] = useState(null);

  // Tests state
  const [tests, setTests] = useState([]);

  // Quarantine state
  const [quarantineRecords, setQuarantineRecords] = useState([]);

  // Modal state
  const [modalVisible, setModalVisible] = useState(false);
  const [modalMode, setModalMode] = useState("view"); // view/create/edit/resolve
  const [formData, setFormData] = useState({});
  const [formErrors, setFormErrors] = useState({});

  // Field definitions per tab
  const fieldsByTab = {
    lots: [
      { key: "product_type", label: "Product Type", type: "text" },
      { key: "source_module", label: "Source Module", type: "text" },
      { key: "produced_date", label: "Produced Date", type: "date" },
      { key: "quantity", label: "Quantity", type: "number" },
      { key: "unit", label: "Unit", type: "text" },
      { key: "harvest_team", label: "Harvest Team", type: "text" },
      { key: "notes", label: "Notes", type: "text" },
    ],
    tests: [
      { key: "lot_id", label: "Lot ID", type: "number" },
      { key: "test_type", label: "Test Type", type: "text" },
      { key: "test_date", label: "Test Date", type: "date" },
      { key: "result_value", label: "Result Value", type: "number" },
      { key: "result_text", label: "Result Text", type: "text" },
      { key: "passed", label: "Passed", type: "checkbox" },
      { key: "tester", label: "Tester", type: "text" },
      { key: "lab", label: "Lab", type: "text" },
      { key: "notes", label: "Notes", type: "text" },
    ],
    quarantine: [
      { key: "lot_id", label: "Lot ID", type: "number" },
      { key: "reason", label: "Reason", type: "text" },
      { key: "quarantine_date", label: "Quarantine Date", type: "date" },
    ],
  };

  // Fetch all data
  const fetchAll = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [lotsData, testsData, quarData] = await Promise.all([
        api.qa.lots.list(token),
        api.qa.tests.list(token),
        api.qa.quarantine.list(token),
      ]);
      setLots(lotsData || []);
      setTests(testsData || []);
      setQuarantineRecords(quarData || []);
    } catch (err) {
      console.error("Fetch error:", err);
      Alert.alert("Error", "Failed to load QA data");
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

  // Handler: Create Lot
  const handleCreateLot = async () => {
    try {
      const newLot = await api.qa.lots.create(formData, token);
      setLots([newLot, ...lots]);
      setModalVisible(false);
      setFormData({});
      Alert.alert("Success", "Lot created");
    } catch (err) {
      Alert.alert("Error", err.response?.data?.detail || "Failed to create lot");
    }
  };

  // Handler: Create Test
  const handleCreateTest = async () => {
    try {
      const newTest = await api.qa.tests.create(formData, token);
      setTests([newTest, ...tests]);
      setModalVisible(false);
      setFormData({});
      Alert.alert("Success", "Test created");
    } catch (err) {
      Alert.alert("Error", err.response?.data?.detail || "Failed to create test");
    }
  };

  // Handler: Create Quarantine
  const handleCreateQuarantine = async () => {
    try {
      const newQr = await api.qa.quarantine.create(formData, token);
      setQuarantineRecords([newQr, ...quarantineRecords]);
      setModalVisible(false);
      setFormData({});
      Alert.alert("Success", "Quarantine record created");
    } catch (err) {
      Alert.alert("Error", err.response?.data?.detail || "Failed to create quarantine");
    }
  };

  // Handler: Resolve Quarantine
  const handleResolveQuarantine = async (qrId) => {
    try {
      const resolved = await api.qa.quarantine.resolve(qrId, formData, token);
      setQuarantineRecords(
        quarantineRecords.map((q) => (q.id === qrId ? resolved : q))
      );
      setModalVisible(false);
      setFormData({});
      Alert.alert("Success", "Quarantine resolved");
    } catch (err) {
      Alert.alert("Error", err.response?.data?.detail || "Failed to resolve");
    }
  };

  // Handler: Trace Lot
  const handleTraceLot = async (lotCode) => {
    try {
      setLoading(true);
      const trace = await api.qa.lots.trace(lotCode, token);
      setTraceDetails(trace);
      setModalVisible(true);
      setModalMode("view");
    } catch (err) {
      Alert.alert("Error", "Failed to trace lot");
    } finally {
      setLoading(false);
    }
  };

  // Status color mapping
  const getStatusColor = (status) => {
    switch (status) {
      case "active":
        return "#4CAF50";
      case "quarantine":
        return "#FF5722";
      case "released":
        return "#2196F3";
      case "rejected":
        return "#9C27B0";
      default:
        return "#757575";
    }
  };

  return {
    // State
    tab,
    setTab,
    loading,
    refreshing,
    lots,
    selectedLot,
    setSelectedLot,
    traceDetails,
    tests,
    quarantineRecords,
    modalVisible,
    setModalVisible,
    modalMode,
    setModalMode,
    formData,
    setFormData,
    formErrors,
    setFormErrors,
    fieldsByTab,

    // Handlers
    fetchAll,
    onRefresh,
    handleCreateLot,
    handleCreateTest,
    handleCreateQuarantine,
    handleResolveQuarantine,
    handleTraceLot,
    getStatusColor,
  };
};
