/**
 * Zustand store for POS cart state.
 * Manages cart items, session, and computed totals.
 */
import { create } from "zustand";

const usePOSStore = create((set, get) => ({
  cart:          [],
  activeSession: null,

  // ─── Cart actions ──────────────────────────────────────────────
  addToCart: (product, qty = 1) => {
    const { cart } = get();
    const existing = cart.find((i) => i.product.id === product.id);
    if (existing) {
      set({
        cart: cart.map((i) =>
          i.product.id === product.id
            ? { ...i, quantity: i.quantity + qty, total: (i.quantity + qty) * i.unit_price * (1 - i.discount_pct / 100) * (1 + i.tax_rate / 100) }
            : i
        ),
      });
    } else {
      const unit_price   = product.selling_price ?? product.price ?? 0;
      const discount_pct = 0;
      const tax_rate     = product.tax_rate ?? 0;
      const total        = qty * unit_price * (1 - discount_pct / 100) * (1 + tax_rate / 100);
      set({ cart: [...cart, { product, quantity: qty, unit_price, discount_pct, tax_rate, total }] });
    }
  },

  removeFromCart: (productId) => {
    set({ cart: get().cart.filter((i) => i.product.id !== productId) });
  },

  updateQty: (productId, qty) => {
    if (qty <= 0) {
      set({ cart: get().cart.filter((i) => i.product.id !== productId) });
      return;
    }
    set({
      cart: get().cart.map((i) =>
        i.product.id === productId
          ? { ...i, quantity: qty, total: qty * i.unit_price * (1 - i.discount_pct / 100) * (1 + i.tax_rate / 100) }
          : i
      ),
    });
  },

  clearCart: () => set({ cart: [] }),

  setSession: (session) => set({ activeSession: session }),

  // ─── Computed getters ─────────────────────────────────────────
  get cartSubtotal() {
    return get().cart.reduce((sum, i) => sum + i.unit_price * i.quantity * (1 - i.discount_pct / 100), 0);
  },

  get cartTax() {
    return get().cart.reduce(
      (sum, i) => sum + i.unit_price * i.quantity * (1 - i.discount_pct / 100) * (i.tax_rate / 100),
      0
    );
  },

  get cartTotal() {
    return get().cart.reduce((sum, i) => sum + i.total, 0);
  },
}));

export default usePOSStore;
