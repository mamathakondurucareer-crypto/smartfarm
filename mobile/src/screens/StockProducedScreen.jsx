/**
 * Stock Produced — farm production output report.
 */
import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, TextInput, TouchableOpacity, ActivityIndicator,
} from "react-native";
import { Layers, RefreshCw, Filter } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import StatGrid      from "../components/ui/StatGrid";
import DataTable     from "../components/ui/DataTable";
import Badge         from "../components/ui/Badge";
import { colors } from "../config/theme";
import { api }       from "../services/api";
import useAuthStore  from "../store/useAuthStore";
import { styles } from "./StockProducedScreen.styles";
import { commonStyles as cs } from "../styles/common";

export default function StockProducedScreen() {
  const token = useAuthStore((s) => s.token);

  const [data,       setData]       = useState(null);
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState("");
  const [startDate,  setStartDate]  = useState("");
  const [endDate,    setEndDate]    = useState("");

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      let params = "";
      const parts = [];
      if (startDate) parts.push(`start_date=${startDate}`);
      if (endDate)   parts.push(`end_date=${endDate}`);
      if (parts.length) params = "?" + parts.join("&");
      const result = await api.reports.production(token, params);
      setData(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [token, startDate, endDate]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const totalBatches = data?.total_batches ?? 0;
  const totalVal     = data?.total_value ?? 0;
  const byCategory   = data?.by_category ?? {};
  const bySource     = data?.by_source ?? {};
  const topCat       = Object.keys(byCategory).length > 0
    ? Object.entries(byCategory).sort((a, b) => b[1] - a[1])[0][0]
    : "—";

  const stats = [
    { label: "Total Batches",  value: String(totalBatches),                      color: colors.primary,  icon: Layers },
    { label: "Total Value",    value: `₹${Number(totalVal).toLocaleString()}`,   color: colors.store,    icon: Layers },
    { label: "Top Category",   value: topCat,                                    color: colors.packing,  icon: Layers },
  ];

  const headers = ["Category", "Quantity"];
  const rows    = Object.entries(byCategory).map(([cat, qty]) => [
    cat,
    String(qty),
  ]);

  return (
    <ScreenWrapper title="Stock Produced">
      {!!error && (
        <View style={cs.errorBox}>
          <Text style={cs.errorText}>{error}</Text>
        </View>
      )}

      {/* Filter row */}
      <Card style={cs.cardGap}>
        <SectionHeader Icon={Filter} title="Date Filter" color={colors.packing} />
        <View style={styles.filterRow}>
          <View style={styles.filterField}>
            <Text style={cs.label}>Start Date</Text>
            <TextInput
              style={cs.input}
              value={startDate}
              onChangeText={setStartDate}
              placeholder="YYYY-MM-DD"
              placeholderTextColor={colors.textMuted}
            />
          </View>
          <View style={styles.filterField}>
            <Text style={cs.label}>End Date</Text>
            <TextInput
              style={cs.input}
              value={endDate}
              onChangeText={setEndDate}
              placeholder="YYYY-MM-DD"
              placeholderTextColor={colors.textMuted}
            />
          </View>
          <TouchableOpacity style={styles.refreshBtn} onPress={fetchData} activeOpacity={0.8}>
            <RefreshCw size={14} color={colors.bg} />
            <Text style={styles.refreshBtnText}>Refresh</Text>
          </TouchableOpacity>
        </View>
      </Card>

      {loading ? (
        <ActivityIndicator size="large" color={colors.packing} style={{ marginTop: 40 }} />
      ) : (
        <>
          <Card style={cs.cardGap}>
            <SectionHeader Icon={Layers} title="Production Summary" color={colors.packing} />
            <StatGrid stats={stats} />
          </Card>

          <Card style={cs.cardGap}>
            <SectionHeader Icon={Layers} title="By Category" color={colors.primary} />
            {rows.length === 0
              ? <Text style={cs.empty}>No production records found</Text>
              : <DataTable headers={headers} rows={rows} />
            }
          </Card>

          {Object.keys(bySource).length > 0 && (
            <Card>
              <SectionHeader Icon={Layers} title="By Source" color={colors.store} />
              <DataTable headers={["Source", "Quantity"]} rows={Object.entries(bySource).map(([src, qty]) => [src, String(qty)])} />
            </Card>
          )}
        </>
      )}
    </ScreenWrapper>
  );
}

