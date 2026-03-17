import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  Modal,
  FlatList,
  ActivityIndicator,
  TextInput,
} from "react-native";
import { Shield, AlertCircle, CheckSquare } from "lucide-react-native";
import { useComplianceScreen } from "../hooks/screens/useComplianceScreen";
import { styles } from "./ComplianceScreen.styles";
import { commonStyles as cs } from "../styles/common";
import { colors } from "../config/theme";

const ComplianceScreen = () => {
  const {
    tab,
    setTab,
    licences,
    tasks,
    taskFilter,
    setTaskFilter,
    loading,
    refreshing,
    onRefresh,
    modalVisible,
    setModalVisible,
    modalMode,
    formData,
    setFormData,
    fieldsByTab,
    handleDeleteLicence,
    handleMarkTaskComplete,
    handleDeleteTask,
    getStatusColor,
    getExpiringSoonCount,
    openCreateModal,
    openEditModal,
    handleModalSubmit,
  } = useComplianceScreen();

  const renderLicencesTab = () => (
    <View style={styles.tabContent}>
      {getExpiringSoonCount() > 0 && (
        <View style={styles.alertBanner}>
          <AlertCircle size={24} color={colors.danger} />
          <View style={styles.alertContent}>
            <Text style={styles.alertTitle}>Action Required</Text>
            <Text style={styles.alertText}>
              {getExpiringSoonCount()} licence(s) expiring soon
            </Text>
          </View>
        </View>
      )}

      <TouchableOpacity
        style={cs.addButton}
        onPress={() => openCreateModal("licences")}
      >
        <Text style={cs.addButtonText}>+ Add Licence</Text>
      </TouchableOpacity>

      <FlatList
        data={licences}
        keyExtractor={(item) => item.id.toString()}
        ListEmptyComponent={
          <View style={cs.emptyState}>
            <Shield size={48} color={colors.textMuted} />
            <Text style={cs.emptyTitle}>No licences added</Text>
            <Text style={cs.emptyText}>Tap "+ Add Licence" to track your farm permits and certificates.</Text>
          </View>
        }
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
                    onPress={() => openEditModal(item, "licences")}
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
        style={cs.addButton}
        onPress={() => openCreateModal("tasks")}
      >
        <Text style={cs.addButtonText}>+ Add Task</Text>
      </TouchableOpacity>

      <FlatList
        data={tasks.filter((t) => {
          if (taskFilter === "all") return true;
          if (taskFilter === "pending") return !t.completed;
          if (taskFilter === "completed") return t.completed;
          return true;
        })}
        keyExtractor={(item) => item.id.toString()}
        ListEmptyComponent={
          <View style={cs.emptyState}>
            <CheckSquare size={48} color={colors.textMuted} />
            <Text style={cs.emptyTitle}>
              {taskFilter === "completed" ? "No completed tasks" : taskFilter === "pending" ? "No pending tasks" : "No tasks yet"}
            </Text>
            <Text style={cs.emptyText}>
              {taskFilter === "all" ? "Tap \"+ Add Task\" to schedule your first compliance task." : "Switch to \"All\" to see all tasks."}
            </Text>
          </View>
        }
        renderItem={({ item }) => (
          <View
            style={[
              styles.listItem,
              {
                borderLeftColor: item.completed ? colors.success : colors.info,
              },
            ]}
          >
            <View style={styles.listItemContent}>
              <View style={styles.listItemHeader}>
                <CheckSquare
                  size={20}
                  color={item.completed ? colors.success : colors.textMuted}
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
                      backgroundColor: item.completed ? colors.success : colors.warn,
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
                  onPress={() => openEditModal(item, "tasks")}
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
        <View style={cs.modalOverlay}>
          <View style={cs.modalContent}>
            <Text style={cs.modalTitle}>
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
                    placeholderTextColor={colors.textMuted}
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
                style={[styles.button, cs.cancelButton]}
                onPress={() => setModalVisible(false)}
              >
                <Text style={cs.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.button, cs.saveButton]}
                onPress={handleModalSubmit}
              >
                <Text style={cs.saveButtonText}>
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

      {loading ? (
        <View style={styles.centerContent}>
          <ActivityIndicator size="large" color={colors.info} />
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

export default ComplianceScreen;
