/**
 * Activity Log — paginated audit trail viewer (admin/manager only).
 */
import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, TouchableOpacity, TextInput,
  ActivityIndicator, FlatList,
} from "react-native";
import { Activity, Search, RefreshCw } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import Badge         from "../components/ui/Badge";
import { colors, fontSize } from "../config/theme";
import { api }       from "../services/api";
import useAuthStore  from "../store/useAuthStore";
import { styles } from "./ActivityLogScreen.styles";
import { commonStyles as cs } from "../styles/common";

const MODULE_COLORS = {
  store: colors.store, pos: colors.pos, financial: colors.accent,
  auth: colors.info, inventory: colors.crop, packing: colors.packing,
  logistics: colors.logistics, service: colors.service,
};
const MODULES = ["all", "store", "pos", "financial", "auth", "inventory", "packing", "logistics"];

export default function ActivityLogScreen() {
  const token = useAuthStore((s) => s.token);
  const [logs, setLogs]           = useState([]);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState("");
  const [page, setPage]           = useState(1);
  const [hasMore, setHasMore]     = useState(true);
  const [moduleFilter, setModuleFilter] = useState("all");
  const [searchAction, setSearch] = useState("");

  const fetchLogs = useCallback(async (pg = 1, append = false) => {
    if (pg === 1) setLoading(true);
    setError("");
    try {
      let params = `?page=${pg}&page_size=30`;
      if (moduleFilter !== "all") params += `&module=${moduleFilter}`;
      if (searchAction.trim()) params += `&action=${encodeURIComponent(searchAction.trim())}`;
      const result = await api.activityLog.list(token, params);
      const items = Array.isArray(result.items) ? result.items : (Array.isArray(result) ? result : []);
      if (append) { setLogs((prev) => [...prev, ...items]); }
      else { setLogs(items); }
      setHasMore(items.length >= 30);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }, [token, moduleFilter, searchAction]);

  useEffect(() => { setPage(1); fetchLogs(1); }, [fetchLogs]);

  const loadMore = () => {
    if (!hasMore || loading) return;
    const next = page + 1;
    setPage(next);
    fetchLogs(next, true);
  };

  const fmtTime = (ts) => {
    try { return new Date(ts).toLocaleString(); } catch { return ts; }
  };

  return (
    <ScreenWrapper title="Activity Log">
      {/* Filter bar */}
      <View style={styles.filterBar}>
        <View style={styles.searchWrap}>
          <Search size={14} color={colors.textMuted} />
          <TextInput
            style={styles.searchInput}
            value={searchAction}
            onChangeText={setSearch}
            placeholder="Filter by action..."
            placeholderTextColor={colors.textMuted}
            returnKeyType="search"
            onSubmitEditing={() => { setPage(1); fetchLogs(1); }}
          />
        </View>
        <TouchableOpacity style={styles.refreshBtn} onPress={() => { setPage(1); fetchLogs(1); }} activeOpacity={0.7}>
          <RefreshCw size={14} color={colors.textDim} />
        </TouchableOpacity>
      </View>

      {/* Module filter chips */}
      <View style={cs.chipRow}>
        {MODULES.map((m) => (
          <TouchableOpacity
            key={m}
            style={[cs.chip, moduleFilter === m && cs.chipActive]}
            onPress={() => setModuleFilter(m)}
          >
            <Text style={{ color: moduleFilter === m ? (MODULE_COLORS[m] ?? colors.primary) : colors.textDim, fontSize: fontSize.sm }}>
              {m === "all" ? "All" : m}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {!!error && <View style={cs.errorBox}><Text style={cs.errorText}>{error}</Text></View>}

      {loading && logs.length === 0 ? (
        <ActivityIndicator size="large" color={colors.primary} style={{ marginTop: 40 }} />
      ) : (
        <Card>
          <SectionHeader Icon={Activity} title={`Activity Log (${logs.length}${hasMore ? "+" : ""})`} color={colors.textDim} />
          {logs.length === 0 ? (
            <Text style={cs.empty}>No activity logs found.</Text>
          ) : (
            <>
              {logs.map((log, idx) => (
                <View key={log.id ?? idx} style={[styles.logRow, log.status === "failure" && styles.failureRow]}>
                  <View style={styles.logLeft}>
                    <View style={[styles.dot, { backgroundColor: log.status === "success" ? colors.primary : colors.danger }]} />
                  </View>
                  <View style={styles.logBody}>
                    <View style={styles.logTop}>
                      <Badge label={log.module} color={MODULE_COLORS[log.module] ?? colors.textDim} />
                      <Text style={styles.logAction}>{log.action}</Text>
                    </View>
                    <Text style={styles.logDesc} numberOfLines={2}>{log.description || "—"}</Text>
                    <View style={styles.logBottom}>
                      <Text style={styles.logMeta}>{log.username}</Text>
                      <Text style={styles.logMeta}>{fmtTime(log.timestamp)}</Text>
                    </View>
                    {log.entity_type && log.entity_id != null && (
                      <Text style={styles.logEntity}>{log.entity_type} #{log.entity_id}</Text>
                    )}
                  </View>
                </View>
              ))}
              {hasMore && (
                <TouchableOpacity style={styles.loadMore} onPress={loadMore} activeOpacity={0.7}>
                  <Text style={styles.loadMoreText}>Load More</Text>
                </TouchableOpacity>
              )}
            </>
          )}
        </Card>
      )}
    </ScreenWrapper>
  );
}

