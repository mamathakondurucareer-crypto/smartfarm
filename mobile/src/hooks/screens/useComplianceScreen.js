import { useState, useEffect, useCallback } from "react";
import { Alert } from "react-native";
import useAuthStore from "../../store/useAuthStore";
import { api } from "../../services/api";

export const useComplianceScreen = () => {
  const token = useAuthStore((state) => state.token);

  // Tab state
  const [tab, setTab] = useState("licences");

  // Licences state
  const [licences, setLicences] = useState([]);
  const [expiringSoon, setExpiringSoon] = useState([]);

  // Tasks state
  const [tasks, setTasks] = useState([]);
  const [taskFilter, setTaskFilter] = useState("all"); // all/pending/completed

  // Loading state
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

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

  // Fetch all data
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

  // Licence handlers
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

  // Task handlers
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

  // Utility functions
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

  const getExpiringSoonCount = () => {
    return expiringSoon.length;
  };

  // Modal handlers
  const openCreateModal = (type) => {
    setModalMode("create");
    setFormData({});
    setSelectedItem(null);
    setTab(type);
    setModalVisible(true);
  };

  const openEditModal = (item, type) => {
    setSelectedItem(item);
    setFormData(item);
    setModalMode("edit");
    setTab(type);
    setModalVisible(true);
  };

  const closeModal = () => {
    setModalVisible(false);
    setFormData({});
    setSelectedItem(null);
  };

  const handleModalSubmit = () => {
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
  };

  return {
    // Tab state
    tab,
    setTab,

    // Licences
    licences,
    expiringSoon,

    // Tasks
    tasks,
    taskFilter,
    setTaskFilter,

    // Loading
    loading,
    refreshing,
    onRefresh,

    // Modal
    modalVisible,
    setModalVisible,
    modalMode,
    formData,
    setFormData,
    selectedItem,
    closeModal,

    // Field definitions
    fieldsByTab,

    // Licence handlers
    handleCreateLicence,
    handleUpdateLicence,
    handleDeleteLicence,

    // Task handlers
    handleCreateTask,
    handleUpdateTask,
    handleMarkTaskComplete,
    handleDeleteTask,

    // Utility
    getStatusColor,
    getExpiringSoonCount,

    // Modal helpers
    openCreateModal,
    openEditModal,
    handleModalSubmit,
  };
};
