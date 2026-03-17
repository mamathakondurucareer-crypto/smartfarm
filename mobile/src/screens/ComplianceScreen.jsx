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
import { Shield, AlertCircle, CheckSquare } from "lucide-react-native";

const ComplianceScreen = () => {
  const token = useAuthStore((state) => state.token);
  const [tab, setTab] = useState("licences");
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Licences state
  const [licences, setLicences] = useState([]);
  const [expiringSoon, setExpiringSoon] = useState([]);

  // Tasks state
  const [tasks, setTasks] = useState([]);
  const [taskFilter, setTaskFilter] = useState("all"); // all/pending/completed

  // Modal state
  const [modalVisible, setModalVisible] = useState(false);
  const [modalMode, setModalMode] = useState("create"); // create/edit
  const [formData, setFormData] = useState({});
  const [selectedItem, setSelectedItem] = useState(null);

  // Field definitions per tab
  const fieldsByTab = {
    licences: [
      { key: "name", label: "Licence Name", type: "text" },
      { key: "category", label: "Category", type: "text" },
      { key: "issuing_authority", label: "Issuing Authority", type: "text" },
      { key: "licence_number", label: "Licence Number", type: "text" },
      { key: "cost_inr", label: "Cost (INR)", type: "number" },
      { key: "issue_date", label: "Issue Date", type: "date" },
      { key: "expiry_date", label: "Expiry Date", type: "date" },
      { key: "responsible_person", label: "Responsible Person", type: "text" },
      { key: "notes", label: "Notes", type: "text" },
    ],
    tasks: [
      { key: "title", label: "Task Title", type: "text" },
      { key: "task_type", label: "Task Type", type: "text" },
      { key: "frequency", label: "Frequency", type: "text" },
      { key: "due_date", label: "Due Date", type: "date" },
      { key: "assigned_to", label: "Assigned To", type: "text" },
      { key: "notes", label: "Notes", type: "text" },
    ],
  };

  const fetchAll = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [licsData, tasksData, expData] = await Promise.all([
        api.compliance.licences.list(token),
        api.compliance.tasks.list(token),
        api.compliance.licences.expiringSoon(token),
      ]);
      setLicences(licsData || []);
      setTasks(tasksData || []);
      setExpiringSoon(expData || []);
    } catch (err) {
      console.error("Fetch error:", err);
      Alert.alert("Error", "Failed to load compliance data");
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

  const handleCreateLicence = async () => {
    try {
      const newLic = await api.compliance.licences.create(formData, token);
      setLicences([newLic, ...licences]);
      setModalVisible(false);
      setFormData({});
      Alert.alert("Success", "Licence created");
    } catch (err) {
      Alert.alert("Error", err.response?.data?.detail || "Failed to create licence");
    }
  };

  const handleUpdateLicence = async () => {
    try {
      const updated = await api.compliance.licences.update(
        selectedItem.id,
        formData,
        token
      );
      setLicences(licences.map((l) => (l.id === selectedItem.id ? updated : l)));
      setModalVisible(false);
      setFormData({});
      setSelectedItem(null);
      Alert.alert("Success", "Licence updated");
    } catch (err) {
      Alert.alert("Error", err.response?.data?.detail || "Failed to update licence");
    }
  };

  const handleDeleteLicence = async (licId) => {
    Alert.alert("Confirm", "Delete this licence?", [
      { text: "Cancel" },
      {
        text: "Delete",
        onPress: async () => {
          try {
            await api.compliance.licences.delete(licId, token);
            setLicences(licences.filter((l) => l.id !== licId));
            Alert.alert("Success", "Licence deleted");
          } catch (err) {
            Alert.alert(
              "Error",
              err.response?.data?.detail || "Failed to delete licence"
            );
          }
        },
      },
    ]);
  };

  const handleCreateTask = async () => {
    try {
      const newTask = await api.compliance.tasks.create(formData, token);
      setTasks([newTask, ...tasks]);
      setModalVisible(false);
      setFormData({});
      Alert.alert("Success", "Task created");
    } catch (err) {
      Alert.alert("Error", err.response?.data?.detail || "Failed to create task");
    }
  };

  const handleUpdateTask = async () => {
    try {
      const updated = await api.compliance.tasks.update(
        selectedItem.id,
        formData,
        token
      );
      setTasks(tasks.map((t) => (t.id === selectedItem.id ? updated : t)));
      setModalVisible(false);
      setFormData({});
      setSelectedItem(null);
      Alert.alert("Success", "Task updated");
    } catch (err) {
      Alert.alert("Error", err.response?.data?.detail || "Failed to update task");
    }
  };

  const handleMarkTaskComplete = async (taskId, currentStatus) => {
    try {
      const updated = await api.compliance.tasks.update(
        taskId,
        {
          completed: !currentStatus,
          completed_date: !currentStatus ? new Date().toISOString().split("T")[0] : null,
        },
        token
      );
      setTasks(tasks.map((t) => (t.id === taskId ? updated : t)));
    } catch (err) {
      Alert.alert("Error", "Failed to update task");
    }
  };

  const handleDeleteTask = async (taskId) => {
    Alert.alert("Confirm", "Delete this task?", [
      { text: "Cancel" },
      {
        text: "Delete",
        onPress: async () => {
          try {
            await api.compliance.tasks.delete(taskId, token);
            setTasks(tasks.filter((t) => t.id !== taskId));
            Alert.alert("Success", "Task deleted");
          } catch (err) {
            Alert.alert(
              "Error",
              err.response?.data?.detail || "Failed to delete task"
            );
          }
        },
      },
    ]);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "active":
        return "#4CAF50";
      case "expiring":
        return "#FF9800";
      case "expired":
        return "#FF5722";
      case "pending":
        return "#9C27B0";
      default:
        return "#757575";
    }
  };

  const getExpireSoonCount = () => {
    return expiringSoon.length;
  };

  const renderLicencesTab = () => (
    <View style={styles.tabContent}>
      {getExpirySoonCount() > 0 && (
        <View style={styles.alertBanner}>
          <AlertCircle size={24} color="#FF5722" />
          <View style={styles.alertContent}>
            <Text style={styles.alertTitle}>Action Required</Text>
            <Text style={styles.alertText}>
              {getExpirySoonCount()} licence(s) expiring soon
            </Text>
          </View>
        </View>
      )}

      <TouchableOpacity
        style={styles.addButton}
        onPress={() => {
          setModalMode("create");
          setFormData({});
          setSelectedItem(null);
          setModalVisible(true);
        }}
      >
        <Text style={styles.addButtonText}>+ Add Licence</Text>
      </TouchableOpacity>

      <FlatList
        data={licences}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => {
          const days_left = item.expiry_date
            ? Math.ceil(
                (new Date(item.expiry_date) - new Date()) / (1000 * 60 * 60 * 24)
              )
            : null;
          return (
            <View
              style={[
                styles.listItem,
                { borderLeftColor: getStatusColor(item.status) },
              ]}
            >
              <View style={styles.listItemContent}>
                <View style={styles.listItemHeader}>
                  <Shield size={20} color={getStatusColor(item.status)} />
                  <Text style={styles.listItemTitle}>{item.name}</Text>
                </View>
                <Text style={styles.listItemSubtitle}>
                  {item.issuing_authority}
                </Text>
                <View style={styles.listItemRow}>
                  <Text style={styles.listItemText}>
                    {item.licence_number || "N/A"}
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
                {item.expiry_date && (
                  <Text style={styles.listItemMeta}>
                    Expires: {item.expiry_date}
                    {days_left !== null &&
                      days_left >= 0 &&
                      ` (${days_left} days)`}
                  </Text>
                )}
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
                    onPress={() => handleDeleteLicence(item.id)}
                  >
                    <Text style={styles.smallButtonText}>Delete</Text>
                  </TouchableOpacity>
                </View>
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

  const renderTasksTab = () => (
    <View style={styles.tabContent}>
      <View style={styles.filterButtons}>
        <TouchableOpacity
          style={[
            styles.filterButton,
            taskFilter === "all" && styles.filterButtonActive,
          ]}
          onPress={() => setTaskFilter("all")}
        >
          <Text
            style={[
              styles.filterButtonText,
              taskFilter === "all" && styles.filterButtonActiveText,
            ]}
          >
            All
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[
            styles.filterButton,
            taskFilter === "pending" && styles.filterButtonActive,
          ]}
          onPress={() => setTaskFilter("pending")}
        >
          <Text
            style={[
              styles.filterButtonText,
              taskFilter === "pending" && styles.filterButtonActiveText,
            ]}
          >
            Pending
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[
            styles.filterButton,
            taskFilter === "completed" && styles.filterButtonActive,
          ]}
          onPress={() => setTaskFilter("completed")}
        >
          <Text
            style={[
              styles.filterButtonText,
              taskFilter === "completed" && styles.filterButtonActiveText,
            ]}
          >
            Completed
          </Text>
        </TouchableOpacity>
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
        <Text style={styles.addButtonText}>+ Add Task</Text>
      </TouchableOpacity>

      <FlatList
        data={tasks.filter((t) => {
          if (taskFilter === "all") return true;
          if (taskFilter === "pending") return !t.completed;
          if (taskFilter === "completed") return t.completed;
          return true;
        })}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View
            style={[
              styles.listItem,
              {
                borderLeftColor: item.completed ? "#4CAF50" : "#2196F3",
              },
            ]}
          >
            <View style={styles.listItemContent}>
              <View style={styles.listItemHeader}>
                <CheckSquare
                  size={20}
                  color={item.completed ? "#4CAF50" : "#999"}
                />
                <Text
                  style={[
                    styles.listItemTitle,
                    item.completed && styles.completedText,
                  ]}
                >
                  {item.title}
                </Text>
              </View>
              <Text style={styles.listItemSubtitle}>{item.task_type}</Text>
              <View style={styles.listItemRow}>
                <Text style={styles.listItemText}>{item.due_date}</Text>
                <View
                  style={[
                    styles.statusBadge,
                    {
                      backgroundColor: item.completed ? "#4CAF50" : "#FF9800",
                    },
                  ]}
                >
                  <Text style={styles.statusText}>
                    {item.completed ? "Done" : "Pending"}
                  </Text>
                </View>
              </View>
              {item.assigned_to && (
                <Text style={styles.listItemMeta}>
                  Assigned to: {item.assigned_to}
                </Text>
              )}
              <View style={styles.actionButtons}>
                <TouchableOpacity
                  style={[
                    styles.smallButton,
                    item.completed
                      ? styles.uncompleteButton
                      : styles.completeButton,
                  ]}
                  onPress={() =>
                    handleMarkTaskComplete(item.id, item.completed)
                  }
                >
                  <Text style={styles.smallButtonText}>
                    {item.completed ? "Undo" : "Complete"}
                  </Text>
                </TouchableOpacity>
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
                  onPress={() => handleDeleteTask(item.id)}
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
                ? `New ${tab === "licences" ? "Licence" : "Task"}`
                : `Edit ${tab === "licences" ? "Licence" : "Task"}`}
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
                  if (tab === "licences") {
                    if (modalMode === "create") {
                      handleCreateLicence();
                    } else {
                      handleUpdateLicence();
                    }
                  } else if (tab === "tasks") {
                    if (modalMode === "create") {
                      handleCreateTask();
                    } else {
                      handleUpdateTask();
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

  const getExpirySoonCount = () => {
    return expiringSoon.length;
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Compliance & Licences</Text>
      </View>

      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tabButton, tab === "licences" && styles.tabActive]}
          onPress={() => setTab("licences")}
        >
          <Text
            style={[
              styles.tabButtonText,
              tab === "licences" && styles.tabActiveText,
            ]}
          >
            Licences
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tabButton, tab === "tasks" && styles.tabActive]}
          onPress={() => setTab("tasks")}
        >
          <Text
            style={[
              styles.tabButtonText,
              tab === "tasks" && styles.tabActiveText,
            ]}
          >
            Tasks
          </Text>
        </TouchableOpacity>
      </View>

      {loading && !refreshing ? (
        <View style={styles.centerContent}>
          <ActivityIndicator size="large" color="#2196F3" />
        </View>
      ) : (
        <ScrollView style={styles.scrollView} scrollEventThrottle={16}>
          {tab === "licences" && renderLicencesTab()}
          {tab === "tasks" && renderTasksTab()}
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
  alertBanner: {
    backgroundColor: "#FFF3E0",
    borderLeftWidth: 4,
    borderLeftColor: "#FF5722",
    flexDirection: "row",
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
    alignItems: "center",
  },
  alertContent: {
    marginLeft: 12,
    flex: 1,
  },
  alertTitle: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#FF5722",
  },
  alertText: {
    fontSize: 12,
    color: "#E65100",
  },
  filterButtons: {
    flexDirection: "row",
    marginBottom: 16,
  },
  filterButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    backgroundColor: "#e0e0e0",
    borderRadius: 6,
    marginHorizontal: 4,
    alignItems: "center",
  },
  filterButtonActive: {
    backgroundColor: "#2196F3",
  },
  filterButtonText: {
    fontSize: 13,
    color: "#666",
    fontWeight: "500",
  },
  filterButtonActiveText: {
    color: "#fff",
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
  completedText: {
    textDecorationLine: "line-through",
    color: "#999",
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
    marginBottom: 8,
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
  completeButton: {
    backgroundColor: "#4CAF50",
  },
  uncompleteButton: {
    backgroundColor: "#999",
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

export default ComplianceScreen;
