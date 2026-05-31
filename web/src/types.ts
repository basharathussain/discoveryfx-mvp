export interface SupplierProduct {
  id: number;
  source: string;
  supplier_name: string;
  supplier_rating: number | null;
  product_url: string;
  external_id: string | null;
  title: string;
  image: string | null;
  category: string | null;
  currency: string;
  cost_price: string;       // Decimal serialised as string
  shipping_cost: string;
  orders_count: number;
  reviews_count: number;
  trend_score: number;
  supplier_score: number;
  margin_score: number;
  competition_score: number;
  overall_score: number;
  created_at: string;
}

export interface SupplierProductDetail extends SupplierProduct {
  trend_inputs: Record<string, unknown>;
  supplier_inputs: Record<string, unknown>;
  margin_inputs: Record<string, unknown>;
  competition_inputs: Record<string, unknown>;
  overall_inputs: Record<string, unknown>;
}

export interface ProductListResponse {
  items: SupplierProduct[];
  total: number;
  page: number;
  page_size: number;
}

export interface Listing {
  id: number;
  user_id: number;
  supplier_product_id: number;
  store_id: number | null;
  title: string;
  description: string;
  currency: string;
  selling_price: string;
  profit_margin: string;
  status: string;
  ebay_item_id: string | null;
  ebay_offer_id: string | null;
  ebay_sku: string | null;
  publish_error: string | null;
  created_at: string;
  updated_at: string;
}

export interface Store {
  id: number;
  platform: string;
  store_name: string;
  region: string;
  status: string;
  created_at: string;
}

export interface Order {
  id: number;
  store_id: number;
  listing_id: number | null;
  ebay_order_id: string;
  buyer_name: string | null;
  currency: string;
  total: string;
  order_status: string;
  supplier_product_url: string | null;
  created_at: string;
}

export interface MarkupRule {
  id: number;
  default_markup_pct: string;
  currency: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserOut {
  id: number;
  email: string;
  created_at: string;
}

export interface ProductFilters {
  q?: string;
  source?: string;
  category?: string;
  min_price?: number;
  max_price?: number;
  min_orders?: number;
  min_rating?: number;
  min_trend?: number;
  min_margin?: number;
  min_overall?: number;
  sort?: string;
  order?: "asc" | "desc";
  page?: number;
  page_size?: number;
}
