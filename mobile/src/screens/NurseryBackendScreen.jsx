import React from "react";
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
import { Sprout, ShoppingCart } from "lucide-react-native";
import { useNurseryBackendScreen } from "../hooks/screens/useNurseryBackendScreen";
import { styles } from "./NurseryBackendScreen.styles";
import { commonStyles as cs } from "../styles/common";
import { colors } from "../config/theme";

const NurseryBackendScreen = () => {
  const {
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
    onRefresh,
    handleDeleteBatch,
    handleDeleteOrder,
    getStatusColor,
    calculateMonthlyRevenue,
    handleOpenBatchModal,
    handleOpenOrderModal,
    handleModalSubmit,
  } = useNurseryBackendScreen();

  const renderBatchesSummary = () => {
    if (!batchesSummary) return null;
    const capacityUsed = batchesSummary.total_capacity
      ? ((batchesSummary.total_ready / batchesSummary.total_capacity) * 100).toFixed(1)
      : 0;
    const isEmpty = batchesSummary.total_batches === 0;
    const valueColor = isEmpty ? colors.textMuted : colors.primary;
    return (
      <View style={[styles.summaryCard, isEmpty && { borderLeftColor: colors.textMuted }]}>
        <View style={styles.summaryItem}>
          <Text style={styles.summaryLabel}>Total Batches</Text>
          <Text style={[styles.summaryValue, { color: valueColor }]}>
            {batchesSummary.total_batches}
          </Text>
        </View>
        <View style={styles.summaryItem}>
          <Text style={styles.summaryLabel}>Seedlings Ready</Text>
          <Text style={[styles.summaryValue, { color: valueColor }]}>
            {batchesSummary.total_ready}
          </Text>
        </View>
        <View style={styles.summaryItem}>
          <Text style={styles.summaryLabel}>Capacity Used</Text>
          <Text style={[styles.summaryValue, { color: valueColor }]}>
            {capacityUsed}%
          </Text>
        </View>
      </View>
    );
  };

  const renderBatchesTab = () => (
    <View style={styles.tabContent}>
      {renderBatchesSummary()}

      <TouchableOpacity
        style={cs.addButton}
        onPress={() => handleOpenBatchModal("create")}
      >
        <Text style={cs.addButtonText}>+ Add Batch</Text>
      </TouchableOpacity>

      <FlatList
        data={batches}
        keyExtractor={(item) => item.id.toString()}
        ListEmptyComponent={
          <View style={cs.emptyState}>
            <Sprout size={48} color={colors.textMuted} />
            <Text style={cs.emptyTitle}>No batches yet</Text>
            <Text style={cs.emptyText}>Tap "+ Add Batch" to record your first nursery batch.</Text>
          </View>
        }
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
                  onPress={() => handleOpenBatchModal("edit", item)}
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
        style={cs.addButton}
        onPress={() => handleOpenOrderModal("create")}
      >
        <Text style={cs.addButtonText}>+ Add Order</Text>
      </TouchableOpacity>

      <FlatList
        data={orders}
        keyExtractor={(item) => item.id.toString()}
        ListEmptyComponent={
          <View style={cs.emptyState}>
            <ShoppingCart size={48} color={colors.textMuted} />
            <Text style={cs.emptyTitle}>No orders yet</Text>
            <Text style={cs.emptyText}>Tap "+ Add Order" to record your first seedling sale.</Text>
          </View>
        }
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
                  onPress={() => handleOpenOrderModal("edit", item)}
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
            <Text style={cs.modalTitle}>
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
                style={[styles.button, cs.cancelButton]}
                onPress={() => setModalVisible(false)}
              >
                <Text style={cs.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.button, styles.submitButton]}
                onPress={handleModalSubmit}
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

      {loading ? (
        <View style={styles.centerContent}>
          <ActivityIndicator size="large" color={colors.info} />
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

export default NurseryBackendScreen;
