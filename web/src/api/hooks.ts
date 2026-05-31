import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "./client";
import type {
  Listing,
  MarkupRule,
  Order,
  ProductFilters,
  ProductListResponse,
  Store,
  SupplierProductDetail,
  TokenResponse,
  UserOut,
} from "../types";

// ---- Auth ----
export const useSignup = () =>
  useMutation({
    mutationFn: (p: { email: string; password: string }) =>
      apiClient.post<TokenResponse>("/auth/signup", p).then((r) => r.data),
  });

export const useLogin = () =>
  useMutation({
    mutationFn: (p: { email: string; password: string }) =>
      apiClient.post<TokenResponse>("/auth/login", p).then((r) => r.data),
  });

export const useMe = (enabled = true) =>
  useQuery({
    queryKey: ["me"],
    queryFn: () => apiClient.get<UserOut>("/auth/me").then((r) => r.data),
    enabled,
    retry: false,
  });

// ---- Products ----
export const useProducts = (filters: ProductFilters) =>
  useQuery({
    queryKey: ["products", filters],
    queryFn: () =>
      apiClient
        .get<ProductListResponse>("/products", { params: filters })
        .then((r) => r.data),
  });

export const useProduct = (id: number | null) =>
  useQuery({
    queryKey: ["product", id],
    queryFn: () =>
      apiClient.get<SupplierProductDetail>(`/products/${id}`).then((r) => r.data),
    enabled: id != null,
  });

export const useCategories = () =>
  useQuery({
    queryKey: ["categories"],
    queryFn: () => apiClient.get<string[]>("/products/categories").then((r) => r.data),
  });

// ---- Listings ----
export const useListings = (status?: string) =>
  useQuery({
    queryKey: ["listings", status],
    queryFn: () =>
      apiClient
        .get<Listing[]>("/listings", { params: status ? { status } : {} })
        .then((r) => r.data),
  });

export const useCreateListing = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (p: {
      supplier_product_id: number;
      title?: string;
      description?: string;
      selling_price?: string;
    }) => apiClient.post<Listing>("/listings", p).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["listings"] }),
  });
};

export const usePublishListing = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      apiClient.post<Listing>(`/listings/${id}/publish`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["listings"] }),
  });
};

export const useUpdateListing = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: Partial<Listing> }) =>
      apiClient.patch<Listing>(`/listings/${id}`, body).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["listings"] }),
  });
};

// ---- Stores ----
export const useStores = () =>
  useQuery({
    queryKey: ["stores"],
    queryFn: () => apiClient.get<Store[]>("/stores").then((r) => r.data),
  });

export const useCreateStubStore = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (p: { store_name: string; region: string }) =>
      apiClient.post<Store>("/stores/stub", p).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["stores"] }),
  });
};

// ---- Orders ----
export const useOrders = () =>
  useQuery({
    queryKey: ["orders"],
    queryFn: () => apiClient.get<Order[]>("/orders").then((r) => r.data),
  });

// ---- Settings ----
export const useMarkup = () =>
  useQuery({
    queryKey: ["markup"],
    queryFn: () => apiClient.get<MarkupRule>("/settings/markup").then((r) => r.data),
  });

export const useUpdateMarkup = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (p: { default_markup_pct: number }) =>
      apiClient.put<MarkupRule>("/settings/markup", p).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["markup"] }),
  });
};
