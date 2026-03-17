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
import { CheckCircle, AlertTriangle, Package } from "lucide-react-native";

const QAScreen = () => {
  const token = useAuthStore((s) => s.token);
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

  const renderLotsTab = () => (
    <View style={styles.tabContent}>
      <TouchableOpacity
        style={styles.addButton}
        onPress={() => {
          setModalMode("create");
          setFormData({});
          setSelectedLot(null);
          setModalVisible(true);
        }}
      >
        <Text style={styles.addButtonText}>+ Add Lot</Text>
      </TouchableOpacity>

      <FlatList
        data={lots}
        keyExtractor={(item) => item.id.toString()}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Package size={48} color="#bdbdbd" />
            <Text style={styles.emptyTitle}>No production lots yet</Text>
            <Text style={styles.emptyText}>Tap "+ Add Lot" to create a traceable production lot.</Text>
          </View>
        }
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.listItem}
            onPress={() => handleTraceLot(item.lot_code)}
          >
            <View style={styles.listItemContent}>
              <View style={styles.listItemHeader}>
                <Package size={20} color="#666" />
                <Text style={styles.listItemTitle}>{item.lot_code}</Text>
              </View>
              <Text style={styles.listItemSubtitle}>{item.product_type}</Text>
              <View style={styles.listItemRow}>
                <Text style={styles.listItemText}>
                  {item.quantity} {item.unit}
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
              <Text style={styles.listItemMeta}>{item.produced_date}</Text>
            </View>
          </TouchableOpacity>
        )}
        scrollEnabled={false}
        refreshing={refreshing}
        onRefresh={onRefresh}
      />
    </View>
  );

  const renderTestsTab = () => (
    <View style={styles.tabContent}>
      <TouchableOpacity
        style={styles.addButton}
        onPress={() => {
          setModalMode("create");
          setFormData({});
          setModalVisible(true);
        }}
      >
        <Text style={styles.addButtonText}>+ Add Test</Text>
      </TouchableOpacity>

      <FlatList
        data={tests}
        keyExtractor={(item) => item.id.toString()}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <CheckCircle size={48} color="#bdbdbd" />
            <Text style={styles.emptyTitle}>No quality tests recorded</Text>
            <Text style={styles.emptyText}>Tap "+ Add Test" to log a quality test against a lot.</Text>
          </View>
        }
        renderItem={({ item }) => (
          <View style={styles.listItem}>
            <View style={styles.listItemContent}>
              <View style={styles.listItemHeader}>
                <CheckCircle
                  size={20}
                  color={item.passed ? "#4CAF50" : "#FF5722"}
                />
                <Text style={styles.listItemTitle}>{item.test_type}</Text>
              </View>
              <Text style={styles.listItemSubtitle}>Lot ID: {item.lot_id}</Text>
              <View style={styles.listItemRow}>
                <Text style={styles.listItemText}>{item.test_date}</Text>
                {item.result_value && (
                  <Text style={styles.listItemMeta}>
                    Result: {item.result_value}
                  </Text>
                )}
              </View>
              <Text style={styles.listItemMeta}>Tester: {item.tester}</Text>
            </View>
          </View>
        )}
        scrollEnabled={false}
        refreshing={refreshing}
        onRefresh={onRefresh}
      />
    </View>
  );

  const renderQuarantineTab = () => (
    <View style={styles.tabContent}>
      <TouchableOpacity
        style={styles.addButton}
        onPress={() => {
          setModalMode("create");
          setFormData({});
          setModalVisible(true);
        }}
      >
        <Text style={styles.addButtonText}>+ Add Quarantine</Text>
      </TouchableOpacity>

      <FlatList
        data={quarantineRecords}
        keyExtractor={(item) => item.id.toString()}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <AlertTriangle size={48} color="#bdbdbd" />
            <Text style={styles.emptyTitle}>No quarantine records</Text>
            <Text style={styles.emptyText}>Quarantine records appear here when lots are flagged for review.</Text>
          </View>
        }
        renderItem={({ item }) => {
          const lotInfo = lots.find((l) => l.id === item.lot_id);
          return (
            <View style={styles.listItem}>
              <View style={styles.listItemContent}>
                <View style={styles.listItemHeader}>
                  <AlertTriangle size={20} color="#FF5722" />
                  <Text style={styles.listItemTitle}>
                    {lotInfo?.lot_code || `Lot ${item.lot_id}`}
                  </Text>
                </View>
                <Text style={styles.listItemSubtitle}>{item.reason}</Text>
                <View style={styles.listItemRow}>
                  <Text style={styles.listItemText}>{item.quarantine_date}</Text>
                  <View
                    style={[
                      styles.statusBadge,
                      {
                        backgroundColor: item.is_resolved ? "#4CAF50" : "#FF5722",
                      },
                    ]}
                  >
                    <Text style={styles.statusText}>
                      {item.is_resolved ? "Resolved" : "Active"}
                    </Text>
                  </View>
                </View>
                {!item.is_resolved && (
                  <TouchableOpacity
                    style={styles.resolveButton}
                    onPress={() => {
                      setFormData({});
                      setModalMode("resolve");
                      setSelectedLot(item.id);
                      setModalVisible(true);
                    }}
                  >
                    <Text style={styles.resolveButtonText}>Resolve</Text>
                  </TouchableOpacity>
                )}
              </View>
            </View>
          );
        }}
        scrollEnabled={false}
        refreshing={refreshing}
        onRefresh={onRefresh}
      />
    </View>
  );

  const renderModal = () => {
    if (modalMode === "view" && traceDetails) {
      return (
        <Modal
          visible={modalVisible}
          transparent
          animationType="slide"
          onRequestClose={() => setModalVisible(false)}
        >
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              <Text style={styles.modalTitle}>Lot Trace</Text>
              <ScrollView style={styles.modalScroll}>
                <Text style={styles.modalSubtitle}>Lot Information</Text>
                <View style={styles.traceCard}>
                  <Text style={styles.traceText}>
                    Code: {traceDetails.lot.lot_code}
                  </Text>
                  <Text style={styles.traceText}>
                    Type: {traceDetails.lot.product_type}
                  </Text>
                  <Text style={styles.traceText}>
                    Quantity: {traceDetails.lot.quantity} {traceDetails.lot.unit}
                  </Text>
                  <Text style={styles.traceText}>
                    Status: {traceDetails.lot.status}
                  </Text>
                </View>

                {traceDetails.quality_tests.length > 0 && (
                  <>
                    <Text style={styles.modalSubtitle}>Quality Tests</Text>
                    {traceDetails.quality_tests.map((test) => (
                      <View key={test.id} style={styles.traceCard}>
                        <Text style={styles.traceText}>
                          {test.test_type} - {test.test_date}
                        </Text>
                        <Text style={styles.traceText}>
                          Passed: {test.passed ? "Yes" : "No"}
                        </Text>
                        {test.result_value && (
                          <Text style={styles.traceText}>
                            Result: {test.result_value}
                          </Text>
                        )}
                      </View>
                    ))}
                  </>
                )}

                {traceDetails.quarantine.length > 0 && (
                  <>
                    <Text style={styles.modalSubtitle}>Quarantine Records</Text>
                    {traceDetails.quarantine.map((qr) => (
                      <View key={qr.id} style={styles.traceCard}>
                        <Text style={styles.traceText}>
                          Reason: {qr.reason}
                        </Text>
                        <Text style={styles.traceText}>
                          Status: {qr.is_resolved ? "Resolved" : "Active"}
                        </Text>
                      </View>
                    ))}
                  </>
                )}

                <Text style={styles.modalSubtitle}>Summary</Text>
                <Text
                  style={[
                    styles.traceText,
                    {
                      color: traceDetails.all_passed ? "#4CAF50" : "#FF5722",
                    },
                  ]}
                >
                  {traceDetails.all_passed
                    ? "All tests passed"
                    : "Some tests failed"}
                </Text>
              </ScrollView>
              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setModalVisible(false)}
              >
                <Text style={styles.closeButtonText}>Close</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Modal>
      );
    }

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
              {modalMode === "create" && `New ${tab}`}
              {modalMode === "resolve" && "Resolve Quarantine"}
            </Text>
            <ScrollView style={styles.modalScroll}>
              {modalMode === "resolve" ? (
                <>
                  <Text style={styles.fieldLabel}>Resolved By</Text>
                  <TextInput
                    style={styles.fieldInput}
                    placeholder="Your name"
                    value={formData.resolved_by || ""}
                    onChangeText={(val) =>
                      setFormData({ ...formData, resolved_by: val })
                    }
                  />
                  <Text style={styles.fieldLabel}>Resolution</Text>
                  <TextInput
                    style={[styles.fieldInput, { minHeight: 80 }]}
                    placeholder="Describe resolution"
                    multiline
                    value={formData.resolution || ""}
                    onChangeText={(val) =>
                      setFormData({ ...formData, resolution: val })
                    }
                  />
                </>
              ) : (
                fields.map((field) => (
                  <View key={field.key}>
                    <Text style={styles.fieldLabel}>{field.label}</Text>
                    {field.type === "checkbox" ? (
                      <TouchableOpacity
                        style={styles.checkboxContainer}
                        onPress={() =>
                          setFormData({
                            ...formData,
                            [field.key]: !formData[field.key],
                          })
                        }
                      >
                        <View
                          style={[
                            styles.checkbox,
                            formData[field.key] && styles.checkboxChecked,
                          ]}
                        />
                        <Text style={styles.checkboxLabel}>
                          {formData[field.key] ? "Yes" : "No"}
                        </Text>
                      </TouchableOpacity>
                    ) : (
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
                    )}
                  </View>
                ))
              )}
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
                  if (modalMode === "resolve") {
                    handleResolveQuarantine(selectedLot);
                  } else if (tab === "lots") {
                    handleCreateLot();
                  } else if (tab === "tests") {
                    handleCreateTest();
                  } else if (tab === "quarantine") {
                    handleCreateQuarantine();
                  }
                }}
              >
                <Text style={styles.buttonText}>
                  {modalMode === "resolve" ? "Resolve" : "Create"}
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
        <Text style={styles.headerTitle}>QA & Traceability</Text>
      </View>

      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tabButton, tab === "lots" && styles.tabActive]}
          onPress={() => setTab("lots")}
        >
          <Text
            style={[
              styles.tabButtonText,
              tab === "lots" && styles.tabActiveText,
            ]}
          >
            Lots
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tabButton, tab === "tests" && styles.tabActive]}
          onPress={() => setTab("tests")}
        >
          <Text
            style={[
              styles.tabButtonText,
              tab === "tests" && styles.tabActiveText,
            ]}
          >
            Tests
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[
            styles.tabButton,
            tab === "quarantine" && styles.tabActive,
          ]}
          onPress={() => setTab("quarantine")}
        >
          <Text
            style={[
              styles.tabButtonText,
              tab === "quarantine" && styles.tabActiveText,
            ]}
          >
            Quarantine
          </Text>
        </TouchableOpacity>
      </View>

      {loading && !refreshing ? (
        <View style={styles.centerContent}>
          <ActivityIndicator size="large" color="#2196F3" />
        </View>
      ) : (
        <ScrollView style={styles.scrollView} scrollEventThrottle={16}>
          {tab === "lots" && renderLotsTab()}
          {tab === "tests" && renderTestsTab()}
          {tab === "quarantine" && renderQuarantineTab()}
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
    borderLeftColor: "#2196F3",
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
  resolveButton: {
    backgroundColor: "#FF9800",
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 4,
    marginTop: 8,
    alignItems: "center",
  },
  resolveButtonText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 12,
  },
  centerContent: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  emptyState: {
    alignItems: "center",
    paddingVertical: 48,
    paddingHorizontal: 24,
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#999",
    marginTop: 16,
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 13,
    color: "#bdbdbd",
    textAlign: "center",
    lineHeight: 20,
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
  modalSubtitle: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#2196F3",
    marginTop: 12,
    marginBottom: 8,
  },
  modalScroll: {
    paddingHorizontal: 16,
    maxHeight: 400,
  },
  traceCard: {
    backgroundColor: "#f9f9f9",
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
    borderLeftWidth: 3,
    borderLeftColor: "#2196F3",
  },
  traceText: {
    fontSize: 13,
    color: "#333",
    marginBottom: 4,
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
  checkboxContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginVertical: 8,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderWidth: 2,
    borderColor: "#ddd",
    borderRadius: 4,
    marginRight: 8,
  },
  checkboxChecked: {
    backgroundColor: "#4CAF50",
    borderColor: "#4CAF50",
  },
  checkboxLabel: {
    fontSize: 14,
    color: "#333",
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
  closeButton: {
    backgroundColor: "#2196F3",
    marginHorizontal: 16,
    marginBottom: 16,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: "center",
  },
  closeButtonText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 14,
  },
});

export default QAScreen;
