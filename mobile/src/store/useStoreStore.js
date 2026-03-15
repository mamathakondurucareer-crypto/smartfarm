/**
 * Zustand store for product catalog and store stock.
 */
import { create } from "zustand";
import { api } from "../services/api";

const useStoreStore = create((set) => ({
  products: [],
  stock:    [],
  config:   null,
  loading:  false,

  // ─── Load all store data in parallel ──────────────────────────
  loadStore: async (token) => {
    set({ loading: true });
    try {
      const [config, products, stock] = await Promise.all([
        api.store.getConfig(token),
        api.store.products.list(token),
        api.stock.list(token),
      ]);
      set({ config, products, stock });
    } finally {
      set({ loading: false });
    }
  },

  // ─── Setters ──────────────────────────────────────────────────
  setProducts: (products) => set({ products }),
  setStock:    (stock)    => set({ stock }),
  setConfig:   (config)   => set({ config }),
}));

export default useStoreStore;
