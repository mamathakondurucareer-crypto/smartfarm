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
import { CheckCircle, AlertTriangle, Package } from "lucide-react-native";
import { useQAScreen } from "../hooks/screens/useQAScreen";
import { styles } from "./QAScreen.styles";
import { commonStyles as cs } from "../styles/common";
import { colors } from "../config/theme";

const QAScreen = () => {
  const {
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
    fieldsByTab,
    onRefresh,
    handleCreateLot,
    handleCreateTest,
    handleCreateQuarantine,
    handleResolveQuarantine,
    handleTraceLot,
    getStatusColor,
  } = useQAScreen();

  const renderLotsTab = () => (
    <View style={styles.tabContent}>
      <TouchableOpacity
        style={cs.addButton}
        onPress={() => {
          setModalMode("create");
          setFormData({});
          setSelectedLot(null);
          setModalVisible(true);
        }}
      >
        <Text style={cs.addButtonText}>+ Add Lot</Text>
      </TouchableOpacity>

      <FlatList
        data={lots}
        keyExtractor={(item) => item.id.toString()}
        ListEmptyComponent={
          <View style={cs.emptyState}>
            <Package size={48} color={colors.textMuted} />
            <Text style={cs.emptyTitle}>No production lots yet</Text>
            <Text style={cs.emptyText}>Tap "+ Add Lot" to create a traceable production lot.</Text>
          </View>
        }
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.listItem}
            onPress={() => handleTraceLot(item.lot_code)}
          >
            <View style={styles.listItemContent}>
              <View style={styles.listItemHeader}>
                <Package size={20} color={colors.textDim} />
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
        style={cs.addButton}
        onPress={() => {
          setModalMode("create");
          setFormData({});
          setModalVisible(true);
        }}
      >
        <Text style={cs.addButtonText}>+ Add Test</Text>
      </TouchableOpacity>

      <FlatList
        data={tests}
        keyExtractor={(item) => item.id.toString()}
        ListEmptyComponent={
          <View style={cs.emptyState}>
            <CheckCircle size={48} color={colors.textMuted} />
            <Text style={cs.emptyTitle}>No quality tests recorded</Text>
            <Text style={cs.emptyText}>Tap "+ Add Test" to log a quality test against a lot.</Text>
          </View>
        }
        renderItem={({ item }) => (
          <View style={styles.listItem}>
            <View style={styles.listItemContent}>
              <View style={styles.listItemHeader}>
                <CheckCircle
                  size={20}
                  color={item.passed ? colors.primary : colors.danger}
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
        style={cs.addButton}
        onPress={() => {
          setModalMode("create");
          setFormData({});
          setModalVisible(true);
        }}
      >
        <Text style={cs.addButtonText}>+ Add Quarantine</Text>
      </TouchableOpacity>

      <FlatList
        data={quarantineRecords}
        keyExtractor={(item) => item.id.toString()}
        ListEmptyComponent={
          <View style={cs.emptyState}>
            <AlertTriangle size={48} color={colors.textMuted} />
            <Text style={cs.emptyTitle}>No quarantine records</Text>
            <Text style={cs.emptyText}>Quarantine records appear here when lots are flagged for review.</Text>
          </View>
        }
        renderItem={({ item }) => {
          const lotInfo = lots.find((l) => l.id === item.lot_id);
          return (
            <View style={styles.listItem}>
              <View style={styles.listItemContent}>
                <View style={styles.listItemHeader}>
                  <AlertTriangle size={20} color={colors.danger} />
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
                        backgroundColor: item.is_resolved ? colors.primary : colors.danger,
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
          <View style={cs.modalOverlay}>
            <View style={cs.modalContent}>
              <Text style={cs.modalTitle}>Lot Trace</Text>
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
                      color: traceDetails.all_passed ? colors.primary : colors.danger,
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
        <View style={cs.modalOverlay}>
          <View style={cs.modalContent}>
            <Text style={cs.modalTitle}>
              {modalMode === "create" && `New ${tab}`}
              {modalMode === "resolve" && "Resolve Quarantine"}
            </Text>
            <ScrollView style={cs.formScroll}>
              {modalMode === "resolve" ? (
                <>
                  <Text style={cs.label}>Resolved By</Text>
                  <TextInput
                    style={cs.input}
                    placeholder="Your name"
                    placeholderTextColor={colors.textMuted}
                    value={formData.resolved_by || ""}
                    onChangeText={(val) =>
                      setFormData({ ...formData, resolved_by: val })
                    }
                  />
                  <Text style={cs.label}>Resolution</Text>
                  <TextInput
                    style={[cs.input, { minHeight: 80 }]}
                    placeholder="Describe resolution"
                    placeholderTextColor={colors.textMuted}
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
                    <Text style={cs.label}>{field.label}</Text>
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
                        style={cs.input}
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
                    )}
                  </View>
                ))
              )}
            </ScrollView>
            <View style={cs.modalButtonGroup}>
              <TouchableOpacity
                style={cs.cancelButton}
                onPress={() => setModalVisible(false)}
              >
                <Text style={cs.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={cs.saveButton}
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
                <Text style={cs.saveButtonText}>
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
          <ActivityIndicator size="large" color={colors.info} />
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

export default QAScreen;
