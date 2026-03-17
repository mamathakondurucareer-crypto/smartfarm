/**
 * Barcode/QR scanner — web-based text input with scan history and result display.
 */
import React, { useState, useRef } from "react";
import {
  View, Text, TextInput, TouchableOpacity, ScrollView,
  ActivityIndicator,
} from "react-native";
import { Scan, Search, X, Package, ShoppingBag } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import Badge         from "../components/ui/Badge";
import { colors } from "../config/theme";
import { api }       from "../services/api";
import useAuthStore  from "../store/useAuthStore";
import { styles } from "./ScannerScreen.styles";
import { commonStyles as cs } from "../styles/common";

const MODES = [
  { key: "stock", label: "Stock Lookup",  color: colors.scanner, icon: Package },
  { key: "pos",   label: "POS Lookup",    color: colors.pos,     icon: ShoppingBag },
];

export default function ScannerScreen() {
  const token    = useAuthStore((s) => s.token);
  const inputRef = useRef(null);

  const [barcode,   setBarcode]   = useState("");
  const [mode,      setMode]      = useState("stock");
  const [loading,   setLoading]   = useState(false);
  const [error,     setError]     = useState("");
  const [result,    setResult]    = useState(null);
  const [history,   setHistory]   = useState([]);

  const handleScan = async () => {
    const code = barcode.trim();
    if (!code) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      let data;
      if (mode === "stock") {
        data = await api.packing.scanBarcode(code, token);
      } else {
        data = await api.pos.lookup(code, token);
      }
      setResult(data);
      setHistory((prev) => [{ code, mode, data, ts: new Date().toLocaleTimeString() }, ...prev].slice(0, 10));
      setBarcode("");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setBarcode("");
    setResult(null);
    setError("");
    inputRef.current?.focus();
  };

  const activeMode = MODES.find((m) => m.key === mode);

  return (
    <ScreenWrapper title="Scanner">
      {/* Mode toggle */}
      <Card style={cs.cardGap}>
        <SectionHeader Icon={Scan} title="Scan Mode" color={colors.scanner} />
        <View style={styles.modeRow}>
          {MODES.map((m) => (
            <TouchableOpacity
              key={m.key}
              style={[styles.modeBtn, mode === m.key && { backgroundColor: m.color, borderColor: m.color }]}
              onPress={() => { setMode(m.key); setResult(null); setError(""); }}
              activeOpacity={0.8}
            >
              <m.icon size={14} color={mode === m.key ? colors.bg : m.color} />
              <Text style={[styles.modeBtnText, mode === m.key && { color: colors.bg }]}>{m.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </Card>

      {/* Input */}
      <Card style={cs.cardGap}>
        <SectionHeader Icon={Search} title="Barcode / QR Input" color={activeMode?.color ?? colors.scanner} />
        <View style={styles.inputRow}>
          <TextInput
            ref={inputRef}
            style={[styles.barcodeInput, { borderColor: activeMode?.color ?? colors.scanner }]}
            value={barcode}
            onChangeText={setBarcode}
            placeholder="Enter or paste barcode / QR code here..."
            placeholderTextColor={colors.textMuted}
            onSubmitEditing={handleScan}
            autoFocus
            autoCapitalize="none"
          />
          <TouchableOpacity
            style={[styles.scanBtn, { backgroundColor: activeMode?.color ?? colors.scanner }, loading && { opacity: 0.6 }]}
            onPress={handleScan}
            disabled={loading}
            activeOpacity={0.85}
          >
            {loading
              ? <ActivityIndicator size="small" color={colors.bg} />
              : <><Scan size={14} color={colors.bg} /><Text style={styles.scanBtnText}>Lookup</Text></>
            }
          </TouchableOpacity>
          <TouchableOpacity style={styles.clearBtn} onPress={handleClear} activeOpacity={0.8}>
            <X size={14} color={colors.textDim} />
          </TouchableOpacity>
        </View>

        {!!error && (
          <View style={cs.errorBox}>
            <Text style={cs.errorText}>{error}</Text>
          </View>
        )}
      </Card>

      {/* Result card */}
      {result && (
        <Card style={cs.cardGap}>
          <SectionHeader Icon={activeMode?.icon ?? Package} title="Scan Result" color={activeMode?.color ?? colors.scanner} />
          <View style={styles.resultGrid}>
            {result.entity_type && (
              <View style={styles.resultItem}>
                <Text style={styles.resultLabel}>Type</Text>
                <Badge label={result.entity_type} color={activeMode?.color ?? colors.scanner} />
              </View>
            )}
            {(result.product_name ?? result.name) && (
              <View style={styles.resultItem}>
                <Text style={styles.resultLabel}>Product</Text>
                <Text style={styles.resultVal}>{result.product_name ?? result.name}</Text>
              </View>
            )}
            {(result.price ?? result.selling_price ?? result.product?.selling_price) != null && (
              <View style={styles.resultItem}>
                <Text style={styles.resultLabel}>Price</Text>
                <Text style={styles.resultVal}>₹{(result.price ?? result.selling_price ?? result.product?.selling_price ?? 0).toLocaleString()}</Text>
              </View>
            )}
            {(result.current_stock ?? result.stock ?? result.quantity) != null && (
              <View style={styles.resultItem}>
                <Text style={styles.resultLabel}>Stock</Text>
                <Text style={styles.resultVal}>{result.current_stock ?? result.stock ?? result.quantity} {result.unit ?? ""}</Text>
              </View>
            )}
            {result.barcode && (
              <View style={styles.resultItem}>
                <Text style={styles.resultLabel}>Barcode</Text>
                <Text style={styles.resultVal}>{result.barcode}</Text>
              </View>
            )}
            {result.category && (
              <View style={styles.resultItem}>
                <Text style={styles.resultLabel}>Category</Text>
                <Text style={styles.resultVal}>{result.category}</Text>
              </View>
            )}
          </View>
        </Card>
      )}

      {/* Scan history */}
      {history.length > 0 && (
        <Card>
          <SectionHeader Icon={Scan} title="Scan History" color={colors.textDim} />
          {history.map((h, idx) => (
            <View key={idx} style={styles.historyRow}>
              <View style={styles.historyLeft}>
                <Text style={styles.historyCode}>{h.code}</Text>
                <Text style={styles.historyMeta}>{h.ts} • {h.mode}</Text>
              </View>
              <Text style={styles.historyName} numberOfLines={1}>
                {h.data?.product_name ?? h.data?.name ?? h.data?.product?.name ?? "Found"}
              </Text>
            </View>
          ))}
        </Card>
      )}
    </ScreenWrapper>
  );
}

