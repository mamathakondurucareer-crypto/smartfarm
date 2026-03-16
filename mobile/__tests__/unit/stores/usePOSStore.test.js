/**
 * Unit tests for usePOSStore — cart state and computed values.
 */

import usePOSStore from "../../../src/store/usePOSStore";

// Reset store before each test
beforeEach(() => {
  usePOSStore.setState({ cart: [], activeSession: null });
});

const sampleProduct = {
  id: 1,
  name: "Murrel Fish",
  unit: "kg",
  selling_price: 350,
  gst_rate: 5,
};

const sampleProduct2 = {
  id: 2,
  name: "Eggs Tray",
  unit: "tray",
  selling_price: 180,
  gst_rate: 5,
};

// ── addToCart ───────────────────────────────────────────────────────────────
describe("addToCart", () => {
  it("adds a new product to an empty cart", () => {
    usePOSStore.getState().addToCart(sampleProduct, 1);
    const cart = usePOSStore.getState().cart;
    expect(cart).toHaveLength(1);
    expect(cart[0].product.id).toBe(1);
    expect(cart[0].quantity).toBe(1);
  });

  it("increments quantity when same product is added again", () => {
    usePOSStore.getState().addToCart(sampleProduct, 1);
    usePOSStore.getState().addToCart(sampleProduct, 2);
    const cart = usePOSStore.getState().cart;
    expect(cart).toHaveLength(1);
    expect(cart[0].quantity).toBe(3);
  });

  it("adds multiple different products", () => {
    usePOSStore.getState().addToCart(sampleProduct, 1);
    usePOSStore.getState().addToCart(sampleProduct2, 2);
    const cart = usePOSStore.getState().cart;
    expect(cart).toHaveLength(2);
  });

  it("stores correct unit_price from selling_price", () => {
    usePOSStore.getState().addToCart(sampleProduct, 1);
    const item = usePOSStore.getState().cart[0];
    expect(item.unit_price).toBe(350);
  });

  it("stores correct tax_rate from gst_rate", () => {
    usePOSStore.getState().addToCart(sampleProduct, 1);
    const item = usePOSStore.getState().cart[0];
    expect(item.tax_rate).toBe(5);
  });

  it("calculates correct total with tax", () => {
    usePOSStore.getState().addToCart(sampleProduct, 2);
    const item = usePOSStore.getState().cart[0];
    // 2 * 350 * (1 + 5/100) = 735
    expect(item.total).toBeCloseTo(735, 2);
  });

  it("handles product with price field fallback", () => {
    const productWithPrice = { id: 3, name: "Test", unit: "kg", price: 100, gst_rate: 0 };
    usePOSStore.getState().addToCart(productWithPrice, 1);
    const item = usePOSStore.getState().cart[0];
    expect(item.unit_price).toBe(100);
  });

  it("handles product with zero price", () => {
    const freeProduct = { id: 4, name: "Free", unit: "pc", selling_price: 0, gst_rate: 0 };
    usePOSStore.getState().addToCart(freeProduct, 1);
    const item = usePOSStore.getState().cart[0];
    expect(item.total).toBe(0);
  });
});

// ── removeFromCart ──────────────────────────────────────────────────────────
describe("removeFromCart", () => {
  it("removes a product by id", () => {
    usePOSStore.getState().addToCart(sampleProduct, 1);
    usePOSStore.getState().removeFromCart(1);
    expect(usePOSStore.getState().cart).toHaveLength(0);
  });

  it("removes only the specified product", () => {
    usePOSStore.getState().addToCart(sampleProduct, 1);
    usePOSStore.getState().addToCart(sampleProduct2, 1);
    usePOSStore.getState().removeFromCart(1);
    const cart = usePOSStore.getState().cart;
    expect(cart).toHaveLength(1);
    expect(cart[0].product.id).toBe(2);
  });

  it("removing nonexistent product leaves cart unchanged", () => {
    usePOSStore.getState().addToCart(sampleProduct, 1);
    usePOSStore.getState().removeFromCart(999);
    expect(usePOSStore.getState().cart).toHaveLength(1);
  });

  it("removing from empty cart does nothing", () => {
    usePOSStore.getState().removeFromCart(1);
    expect(usePOSStore.getState().cart).toHaveLength(0);
  });
});

// ── updateQty ───────────────────────────────────────────────────────────────
describe("updateQty", () => {
  it("updates quantity of a cart item", () => {
    usePOSStore.getState().addToCart(sampleProduct, 1);
    usePOSStore.getState().updateQty(1, 5);
    expect(usePOSStore.getState().cart[0].quantity).toBe(5);
  });

  it("removes item when quantity is set to 0", () => {
    usePOSStore.getState().addToCart(sampleProduct, 3);
    usePOSStore.getState().updateQty(1, 0);
    expect(usePOSStore.getState().cart).toHaveLength(0);
  });

  it("removes item when quantity is negative", () => {
    usePOSStore.getState().addToCart(sampleProduct, 2);
    usePOSStore.getState().updateQty(1, -1);
    expect(usePOSStore.getState().cart).toHaveLength(0);
  });

  it("recalculates total after quantity update", () => {
    usePOSStore.getState().addToCart(sampleProduct, 1);
    usePOSStore.getState().updateQty(1, 3);
    const item = usePOSStore.getState().cart[0];
    // 3 * 350 * 1.05 = 1102.5
    expect(item.total).toBeCloseTo(1102.5, 2);
  });
});

// ── clearCart ───────────────────────────────────────────────────────────────
describe("clearCart", () => {
  it("empties the cart", () => {
    usePOSStore.getState().addToCart(sampleProduct, 2);
    usePOSStore.getState().addToCart(sampleProduct2, 1);
    usePOSStore.getState().clearCart();
    expect(usePOSStore.getState().cart).toHaveLength(0);
  });

  it("clearing already empty cart is safe", () => {
    expect(() => usePOSStore.getState().clearCart()).not.toThrow();
    expect(usePOSStore.getState().cart).toHaveLength(0);
  });
});

// ── setSession ──────────────────────────────────────────────────────────────
describe("setSession", () => {
  it("sets the active session", () => {
    const session = { id: 1, session_code: "SES-001", status: "open" };
    usePOSStore.getState().setSession(session);
    expect(usePOSStore.getState().activeSession).toEqual(session);
  });

  it("clears the session with null", () => {
    usePOSStore.getState().setSession({ id: 1 });
    usePOSStore.getState().setSession(null);
    expect(usePOSStore.getState().activeSession).toBeNull();
  });
});

// ── Computed getters ────────────────────────────────────────────────────────
describe("cartSubtotal", () => {
  it("returns 0 for empty cart", () => {
    expect(usePOSStore.getState().cartSubtotal).toBe(0);
  });

  it("sums unit prices * quantities (before tax)", () => {
    usePOSStore.getState().addToCart(sampleProduct, 2); // 2 * 350 = 700
    const subtotal = usePOSStore.getState().cartSubtotal;
    expect(subtotal).toBeCloseTo(700, 2);
  });

  it("adds multiple items correctly", () => {
    usePOSStore.getState().addToCart(sampleProduct, 1);  // 350
    usePOSStore.getState().addToCart(sampleProduct2, 2); // 360
    const subtotal = usePOSStore.getState().cartSubtotal;
    expect(subtotal).toBeCloseTo(710, 2);
  });
});

describe("cartTax", () => {
  it("returns 0 for empty cart", () => {
    expect(usePOSStore.getState().cartTax).toBe(0);
  });

  it("calculates tax from gst_rate", () => {
    usePOSStore.getState().addToCart(sampleProduct, 1); // 350 * 0.05 = 17.5
    const tax = usePOSStore.getState().cartTax;
    expect(tax).toBeCloseTo(17.5, 2);
  });
});

describe("cartTotal", () => {
  it("returns 0 for empty cart", () => {
    expect(usePOSStore.getState().cartTotal).toBe(0);
  });

  it("equals subtotal + tax", () => {
    usePOSStore.getState().addToCart(sampleProduct, 2);
    const total = usePOSStore.getState().cartTotal;
    const subtotal = usePOSStore.getState().cartSubtotal;
    const tax = usePOSStore.getState().cartTax;
    expect(total).toBeCloseTo(subtotal + tax, 2);
  });

  it("sums totals from all items", () => {
    usePOSStore.getState().addToCart(sampleProduct, 1);  // 350 * 1.05 = 367.5
    usePOSStore.getState().addToCart(sampleProduct2, 1); // 180 * 1.05 = 189
    const total = usePOSStore.getState().cartTotal;
    expect(total).toBeCloseTo(556.5, 2);
  });
});
