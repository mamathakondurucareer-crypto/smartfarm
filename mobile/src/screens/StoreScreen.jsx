/**
 * Store dashboard — daily KPIs, recent transactions, low stock alerts.
 */
import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, TouchableOpacity, ActivityIndicator,
} from "react-native";
import { ShoppingBag, AlertTriangle, TrendingUp, Terminal } from "lucide-react-native";
import ScreenWrapper  from "../components/layout/ScreenWrapper";
import Card           from "../components/ui/Card";
import SectionHeader  from "../components/ui/SectionHeader";
import StatGrid       from "../components/ui/StatGrid";
import Badge          from "../components/ui/Badge";
import DataTable      from "../components/ui/DataTable";
import { colors } from "../config/theme";
import { api }        from "../services/api";
import useAuthStore   from "../store/useAuthStore";
import { useNavigation } from "../context/NavigationContext";
import { styles } from "./StoreScreen.styles";
import { commonStyles as cs } from "../styles/common";

export default function StoreScreen() {
  const token      = useAuthStore((s) => s.token);
  const { navigate } = useNavigation();

  const [daily,    setDaily]    = useState(null);
  const [txns,     setTxns]     = useState([]);
  const [lowStock, setLowStock] = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState("");

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [d, t, l] = await Promise.all([
        api.reports.storeDaily(token),
        api.pos.transactions(token, "?limit=10"),
        api.stock.low(token),
      ]);
      setDaily(d);
      setTxns(Array.isArray(t) ? t : t?.transactions ?? []);
      setLowStock(Array.isArray(l) ? l : l?.items ?? []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const stats = daily ? [
    { label: "Today's Sales",  value: `₹${Number(daily.total_sales ?? 0).toLocaleString()}`, color: colors.store,   icon: TrendingUp },
    { label: "Transactions",   value: String(daily.total_transactions ?? 0),                  color: colors.pos,     icon: ShoppingBag },
    { label: "Low Stock",      value: String(lowStock.length),                                color: colors.warn,    icon: AlertTriangle },
  ] : [];

  const txnHeaders = ["Time", "Code", "Amount", "Payment", "Status"];
  const txnRows    = txns.map((t) => {
    const ts = t.transaction_time ?? t.created_at;
    return [
      ts ? new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "—",
      t.transaction_code ?? t.id ?? "—",
      `₹${Number(t.total_amount ?? 0).toLocaleString()}`,
      <Badge key={t.id} label={t.payment_mode ?? "—"} color={colors.info} />,
      <Badge key={`s${t.id}`} label={t.status ?? "—"} color={t.status === "completed" ? colors.primary : colors.textMuted} />,
    ];
  });

  return (
    <ScreenWrapper title="Store">
      {!!error && (
        <View style={cs.errorBox}>
          <Text style={cs.errorText}>{error}</Text>
        </View>
      )}

      {loading ? (
        <ActivityIndicator size="large" color={colors.store} style={{ marginTop: 40 }} />
      ) : (
        <>
          {/* KPI stats */}
          <Card style={cs.cardGap}>
            <SectionHeader Icon={ShoppingBag} title="Today's Overview" color={colors.store} />
            <StatGrid stats={stats} />
          </Card>

          {/* Quick actions */}
          <View style={styles.actionRow}>
            <TouchableOpacity style={[styles.actionBtn, { borderColor: colors.pos }]} onPress={() => navigate("POS")} activeOpacity={0.8}>
              <Text style={[styles.actionBtnText, { color: colors.pos }]}>Open POS Session</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.actionBtn, { borderColor: colors.store }]} onPress={() => navigate("StockSales")} activeOpacity={0.8}>
              <Text style={[styles.actionBtnText, { color: colors.store }]}>View All Stock</Text>
            </TouchableOpacity>
          </View>

          {/* Recent transactions */}
          <Card style={cs.cardGap}>
            <SectionHeader Icon={TrendingUp} title="Recent Transactions" color={colors.pos} />
            {txnRows.length === 0
              ? <Text style={cs.empty}>No transactions today</Text>
              : <DataTable headers={txnHeaders} rows={txnRows} />}
          </Card>

          {/* Low stock */}
          <Card>
            <SectionHeader Icon={AlertTriangle} title="Low Stock Alerts" color={colors.warn} />
            {lowStock.length === 0
              ? <Text style={cs.empty}>All stock levels are healthy</Text>
              : lowStock.map((item) => (
                <View key={item.product_id ?? item.id} style={styles.stockRow}>
                  <Text style={styles.stockName}>{item.product_name ?? item.name ?? "Unknown"}</Text>
                  <View style={styles.stockRight}>
                    <Text style={styles.stockQty}>{item.current_qty ?? item.quantity ?? 0} {item.unit ?? ""}</Text>
                    <Badge label="Low" color={colors.warn} />
                  </View>
                </View>
              ))}
          </Card>
        </>
      )}
    </ScreenWrapper>
  );
}

