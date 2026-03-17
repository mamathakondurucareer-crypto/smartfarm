/**
 * Point of Sale screen — product search, cart management, checkout.
 */
import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, TextInput, TouchableOpacity, ScrollView,
  ActivityIndicator, Modal, FlatList,
} from "react-native";
import {
  ShoppingCart, Search, X, Plus, Minus, CreditCard,
  CheckCircle, Package, Terminal,
} from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import Badge         from "../components/ui/Badge";
import { colors, spacing, fontSize } from "../config/theme";
import { api }       from "../services/api";
import useAuthStore  from "../store/useAuthStore";
import usePOSStore   from "../store/usePOSStore";
import { styles } from "./POSScreen.styles";
import { commonStyles as cs } from "../styles/common";

const PAYMENT_MODES = ["Cash", "UPI", "Card"];

export default function POSScreen() {
  const token = useAuthStore((s) => s.token);
  const {
    cart, activeSession,
    addToCart, removeFromCart, updateQty, clearCart, setSession,
  } = usePOSStore();

  const [products,     setProducts]     = useState([]);
  const [search,       setSearch]       = useState("");
  const [barcode,      setBarcode]      = useState("");
  const [loading,      setLoading]      = useState(true);
  const [error,        setError]        = useState("");
  const [paymentMode,  setPaymentMode]  = useState("Cash");
  const [tendered,     setTendered]     = useState("");
  const [discount,     setDiscount]     = useState("0");
  const [processing,   setProcessing]   = useState(false);
  const [receiptModal, setReceiptModal] = useState(false);
  const [receipt,      setReceipt]      = useState(null);
  const [sessionModal, setSessionModal] = useState(false);
  const [openingCash,  setOpeningCash]  = useState("");
  const [sessionMsg,   setSessionMsg]   = useState("");

  // Computed totals
  const subtotal   = cart.reduce((s, i) => s + i.unit_price * i.quantity, 0);
  const discountAmt = subtotal * (parseFloat(discount) || 0) / 100;
  const taxTotal   = cart.reduce((s, i) => s + (i.unit_price * i.quantity * (i.tax_rate / 100)), 0);
  const total      = subtotal - discountAmt + taxTotal;

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [prods, sess] = await Promise.all([
        api.store.products.list(token, "?is_active=true"),
        api.pos.activeSession(token).catch(() => null),
      ]);
      setProducts(Array.isArray(prods) ? prods : prods?.products ?? []);
      if (sess) setSession(sess);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [token, setSession]);

  useEffect(() => { fetchProducts(); }, [fetchProducts]);

  const filteredProducts = products.filter((p) =>
    p.name?.toLowerCase().includes(search.toLowerCase()) ||
    p.barcode?.toLowerCase().includes(search.toLowerCase())
  );

  const handleBarcodeSearch = async () => {
    if (!barcode.trim()) return;
    try {
      const result = await api.pos.lookup(barcode.trim(), token);
      if (result?.found && result?.result) {
        // Normalize barcode result to match product shape for cart
        const r = result.result;
        addToCart({
          id:            r.product_id,
          name:          r.name,
          unit:          r.unit,
          selling_price: r.selling_price ?? 0,
          gst_rate:      r.gst_rate ?? 0,
        }, 1);
      } else {
        setError("Barcode not found in product catalog");
      }
      setBarcode("");
    } catch (e) {
      setError(e.message);
    }
  };

  const handleOpenSession = async () => {
    try {
      const sess = await api.pos.openSession({ opening_cash: parseFloat(openingCash) || 0 }, token);
      setSession(sess);
      setSessionModal(false);
      setOpeningCash("");
      setSessionMsg("");
    } catch (e) {
      setSessionMsg(e.message);
    }
  };

  const handleCloseSession = async () => {
    if (!activeSession) return;
    try {
      await api.pos.closeSession(activeSession.id, {}, token);
      setSession(null);
    } catch (e) {
      setError(e.message);
    }
  };

  const handleCheckout = async () => {
    if (!activeSession) { setError("Open a session first before processing payment."); return; }
    if (cart.length === 0) { setError("Cart is empty."); return; }
    setProcessing(true);
    setError("");
    try {
      const payload = {
        session_id:   activeSession.id,
        payment_mode: paymentMode.toLowerCase(),
        discount_pct: parseFloat(discount) || 0,
        amount_tendered: paymentMode === "Cash" ? (parseFloat(tendered) || total) : total,
        items: cart.map((i) => ({
          product_id:   i.product.id,
          quantity:     i.quantity,
          unit_price:   i.unit_price,
          discount_pct: i.discount_pct,
          tax_rate:     i.tax_rate,
        })),
      };
      const result = await api.pos.checkout(payload, token);
      setReceipt(result);
      clearCart();
      setTendered("");
      setDiscount("0");
      setReceiptModal(true);
    } catch (e) {
      setError(e.message);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <ScreenWrapper title="Point of Sale">
      {/* Session bar */}
      <Card style={styles.sessionBar}>
        <View style={styles.sessionRow}>
          <View style={styles.sessionLeft}>
            <Terminal size={16} color={activeSession ? colors.primary : colors.textMuted} />
            <Text style={[styles.sessionText, { color: activeSession ? colors.primary : colors.textMuted }]}>
              {activeSession ? `Session #${activeSession.id} — Open` : "No Active Session"}
            </Text>
          </View>
          {activeSession
            ? <TouchableOpacity style={[styles.sessionBtn, { borderColor: colors.danger }]} onPress={handleCloseSession} activeOpacity={0.8}>
                <Text style={{ color: colors.danger, fontSize: fontSize.md, fontWeight: "600" }}>Close Session</Text>
              </TouchableOpacity>
            : <TouchableOpacity style={[styles.sessionBtn, { borderColor: colors.primary }]} onPress={() => setSessionModal(true)} activeOpacity={0.8}>
                <Text style={{ color: colors.primary, fontSize: fontSize.md, fontWeight: "600" }}>Open Session</Text>
              </TouchableOpacity>
          }
        </View>
      </Card>

      {!!error && (
        <View style={cs.errorBox}>
          <Text style={cs.errorText}>{error}</Text>
        </View>
      )}

      <View style={styles.layout}>
        {/* ── Left panel: products ── */}
        <View style={styles.leftPanel}>
          <Card style={cs.cardGap}>
            <SectionHeader Icon={Package} title="Products" color={colors.pos} />
            {/* Search */}
            <View style={styles.searchRow}>
              <View style={styles.searchBox}>
                <Search size={14} color={colors.textMuted} />
                <TextInput
                  style={styles.searchInput}
                  value={search}
                  onChangeText={setSearch}
                  placeholder="Search products..."
                  placeholderTextColor={colors.textMuted}
                />
              </View>
            </View>
            {/* Barcode input */}
            <View style={styles.searchRow}>
              <TextInput
                style={[cs.input, { flex: 1 }]}
                value={barcode}
                onChangeText={setBarcode}
                placeholder="Scan / enter barcode"
                placeholderTextColor={colors.textMuted}
                onSubmitEditing={handleBarcodeSearch}
              />
              <TouchableOpacity style={styles.barcodeBtn} onPress={handleBarcodeSearch} activeOpacity={0.8}>
                <Text style={styles.barcodeBtnText}>Lookup</Text>
              </TouchableOpacity>
            </View>

            {loading
              ? <ActivityIndicator size="large" color={colors.pos} style={{ marginTop: 20 }} />
              : (
                <View style={styles.productGrid}>
                  {filteredProducts.length === 0
                    ? <Text style={cs.empty}>No products found</Text>
                    : filteredProducts.map((p) => (
                      <TouchableOpacity
                        key={p.id}
                        style={styles.productCard}
                        onPress={() => addToCart(p, 1)}
                        activeOpacity={0.75}
                      >
                        <Text style={styles.productName} numberOfLines={2}>{p.name}</Text>
                        <Text style={styles.productPrice}>₹{Number(p.selling_price ?? p.price ?? 0).toLocaleString()}</Text>
                        <Text style={styles.productUnit}>{p.unit ?? ""}</Text>
                      </TouchableOpacity>
                    ))
                  }
                </View>
              )
            }
          </Card>
        </View>

        {/* ── Right panel: cart ── */}
        <View style={styles.rightPanel}>
          <Card>
            <SectionHeader Icon={ShoppingCart} title="Cart" color={colors.store} />
            {cart.length === 0
              ? <Text style={cs.empty}>Cart is empty — tap a product to add</Text>
              : (
                <ScrollView style={{ maxHeight: 320 }} showsVerticalScrollIndicator={false}>
                  {cart.map((item) => (
                    <View key={item.product.id} style={styles.cartItem}>
                      <View style={{ flex: 1 }}>
                        <Text style={styles.cartName} numberOfLines={1}>{item.product.name}</Text>
                        <Text style={styles.cartPrice}>₹{item.unit_price.toLocaleString()} × {item.quantity}</Text>
                      </View>
                      <View style={styles.qtyRow}>
                        <TouchableOpacity onPress={() => updateQty(item.product.id, item.quantity - 1)} style={styles.qtyBtn}>
                          <Minus size={12} color={colors.text} />
                        </TouchableOpacity>
                        <Text style={styles.qtyText}>{item.quantity}</Text>
                        <TouchableOpacity onPress={() => updateQty(item.product.id, item.quantity + 1)} style={styles.qtyBtn}>
                          <Plus size={12} color={colors.text} />
                        </TouchableOpacity>
                        <TouchableOpacity onPress={() => removeFromCart(item.product.id)} style={styles.removeBtn}>
                          <X size={12} color={colors.danger} />
                        </TouchableOpacity>
                      </View>
                    </View>
                  ))}
                </ScrollView>
              )
            }

            {/* Totals */}
            <View style={styles.totalsBox}>
              <View style={styles.totalRow}>
                <Text style={styles.totalLabel}>Subtotal</Text>
                <Text style={styles.totalVal}>₹{subtotal.toFixed(2)}</Text>
              </View>
              <View style={styles.totalRow}>
                <Text style={styles.totalLabel}>Discount (%)</Text>
                <TextInput
                  style={styles.inlineInput}
                  value={discount}
                  onChangeText={setDiscount}
                  keyboardType="numeric"
                  placeholderTextColor={colors.textMuted}
                />
              </View>
              <View style={styles.totalRow}>
                <Text style={styles.totalLabel}>Tax</Text>
                <Text style={styles.totalVal}>₹{taxTotal.toFixed(2)}</Text>
              </View>
              <View style={[styles.totalRow, styles.totalFinal]}>
                <Text style={styles.totalFinalLabel}>Total</Text>
                <Text style={styles.totalFinalVal}>₹{total.toFixed(2)}</Text>
              </View>
            </View>

            {/* Payment mode */}
            <Text style={cs.label}>Payment Mode</Text>
            <View style={styles.modeRow}>
              {PAYMENT_MODES.map((m) => (
                <TouchableOpacity
                  key={m}
                  style={[styles.modeBtn, paymentMode === m && styles.modeBtnActive]}
                  onPress={() => setPaymentMode(m)}
                  activeOpacity={0.8}
                >
                  <Text style={[styles.modeBtnText, paymentMode === m && { color: colors.bg }]}>{m}</Text>
                </TouchableOpacity>
              ))}
            </View>

            {paymentMode === "Cash" && (
              <>
                <Text style={cs.label}>Amount Tendered</Text>
                <TextInput
                  style={cs.input}
                  value={tendered}
                  onChangeText={setTendered}
                  keyboardType="numeric"
                  placeholder={`₹${total.toFixed(2)}`}
                  placeholderTextColor={colors.textMuted}
                />
                {tendered !== "" && parseFloat(tendered) >= total && (
                  <Text style={styles.changeText}>Change: ₹{(parseFloat(tendered) - total).toFixed(2)}</Text>
                )}
              </>
            )}

            <TouchableOpacity
              style={[styles.checkoutBtn, (processing || cart.length === 0) && { opacity: 0.5 }]}
              onPress={handleCheckout}
              disabled={processing || cart.length === 0}
              activeOpacity={0.85}
            >
              {processing
                ? <ActivityIndicator size="small" color={colors.bg} />
                : <><CreditCard size={16} color={colors.bg} /><Text style={styles.checkoutBtnText}>Process Payment</Text></>
              }
            </TouchableOpacity>
          </Card>
        </View>
      </View>

      {/* Open Session Modal */}
      <Modal visible={sessionModal} transparent animationType="fade" onRequestClose={() => setSessionModal(false)}>
        <View style={cs.modalOverlayCentered}>
          <View style={cs.modalCard}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitleText}>Open POS Session</Text>
              <TouchableOpacity onPress={() => setSessionModal(false)}>
                <X size={18} color={colors.textDim} />
              </TouchableOpacity>
            </View>
            {!!sessionMsg && (
              <View style={cs.errorBox}>
                <Text style={cs.errorText}>{sessionMsg}</Text>
              </View>
            )}
            <Text style={cs.label}>Opening Cash Amount (₹)</Text>
            <TextInput
              style={cs.input}
              value={openingCash}
              onChangeText={setOpeningCash}
              keyboardType="numeric"
              placeholder="0.00"
              placeholderTextColor={colors.textMuted}
            />
            <TouchableOpacity style={styles.checkoutBtn} onPress={handleOpenSession} activeOpacity={0.85}>
              <Text style={styles.checkoutBtnText}>Open Session</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {/* Receipt Modal */}
      <Modal visible={receiptModal} transparent animationType="slide" onRequestClose={() => setReceiptModal(false)}>
        <View style={cs.modalOverlayCentered}>
          <View style={cs.modalCard}>
            <View style={styles.modalHeader}>
              <View style={styles.receiptHeader}>
                <CheckCircle size={20} color={colors.primary} />
                <Text style={styles.modalTitleText}>Payment Successful</Text>
              </View>
              <TouchableOpacity onPress={() => setReceiptModal(false)}>
                <X size={18} color={colors.textDim} />
              </TouchableOpacity>
            </View>
            {receipt && (
              <ScrollView showsVerticalScrollIndicator={false}>
                <Text style={styles.receiptCode}>Txn: {receipt.transaction_code ?? receipt.id}</Text>
                <Text style={styles.receiptTotal}>Total Paid: ₹{Number(receipt.total_amount ?? 0).toFixed(2)}</Text>
                <Text style={styles.receiptMode}>Mode: {receipt.payment_mode ?? "—"}</Text>
                {Array.isArray(receipt.items) && receipt.items.length > 0 && (
                  <>
                    <Text style={[cs.label, { marginTop: spacing.md }]}>Items</Text>
                    {receipt.items.map((it, idx) => (
                      <View key={idx} style={styles.receiptItem}>
                        <Text style={styles.receiptItemName}>{it.product_name ?? `Product ${it.product_id}`}</Text>
                        <Text style={styles.receiptItemVal}>×{it.quantity} — ₹{(it.total ?? 0).toFixed(2)}</Text>
                      </View>
                    ))}
                  </>
                )}
                <TouchableOpacity style={[styles.checkoutBtn, { marginTop: spacing.xl }]} onPress={() => setReceiptModal(false)} activeOpacity={0.85}>
                  <Text style={styles.checkoutBtnText}>Done</Text>
                </TouchableOpacity>
              </ScrollView>
            )}
          </View>
        </View>
      </Modal>
    </ScreenWrapper>
  );
}

