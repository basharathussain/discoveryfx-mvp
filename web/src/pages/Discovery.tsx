import { useMemo, useState } from "react";
import {
  Alert, Box, Button, Card, CardContent, Checkbox, Chip, Drawer, FormControl, FormControlLabel, FormGroup,
  Grid, IconButton, InputLabel, LinearProgress, MenuItem, Select, Stack, TextField, Typography,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import SearchIcon from "@mui/icons-material/Search";
import { AgGridReact } from "ag-grid-react";
import type { ColDef, ICellRendererParams } from "ag-grid-community";
import { useNavigate } from "react-router-dom";

import { useCategories, useCreateListing, useProduct, useProducts, useSearchSuppliers } from "../api/hooks";
import type { ProductFilters, SupplierProduct } from "../types";

const SOURCES = [
  { value: "",              label: "All sources" },
  { value: "aliexpress_uk", label: "AliExpress UK" },
  { value: "amazon_uk",     label: "Amazon UK" },
];

function ScoreChip({ value }: { value: number }) {
  let color: "default" | "success" | "warning" | "error" = "default";
  if (value >= 80) color = "success";
  else if (value >= 60) color = "warning";
  else if (value > 0) color = "error";
  return <Chip label={value.toFixed(0)} color={color} size="small" sx={{ minWidth: 44, fontWeight: 700 }} />;
}

export default function Discovery() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<ProductFilters>({
    page: 1, page_size: 100, sort: "overall_score", order: "desc",
  });
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const products = useProducts(filters);
  const categories = useCategories();
  const detail = useProduct(selectedId);
  const createListing = useCreateListing();
  const searchSuppliers = useSearchSuppliers();

  // Live-search panel state
  const [supplierQuery, setSupplierQuery] = useState("");
  const [searchAli, setSearchAli] = useState(true);
  const [searchAmz, setSearchAmz] = useState(true);
  const [lastSearchMsg, setLastSearchMsg] = useState<string | null>(null);
  const [lastSearchErr, setLastSearchErr] = useState<string | null>(null);

  const runSupplierSearch = async () => {
    const q = supplierQuery.trim();
    if (!q) return;
    const sources: ("aliexpress_uk" | "amazon_uk")[] = [];
    if (searchAli) sources.push("aliexpress_uk");
    if (searchAmz) sources.push("amazon_uk");
    if (sources.length === 0) {
      setLastSearchErr("Pick at least one source.");
      return;
    }
    setLastSearchErr(null); setLastSearchMsg(null);
    try {
      const r = await searchSuppliers.mutateAsync({ query: q, sources, limit_per_source: 30 });
      const errParts = Object.entries(r.errors).map(([s, e]) => `${s}: ${e.slice(0, 80)}`);
      setLastSearchMsg(
        `Scraped "${r.query}" — ${r.inserted} new, ${r.skipped} already known.` +
        (errParts.length ? `  Errors: ${errParts.join(" · ")}` : "")
      );
      // Re-apply the local filter to the just-scraped query so the grid focuses on it
      setFilters((f) => ({ ...f, q, page: 1 }));
    } catch (e: any) {
      const detail = e?.response?.data?.detail;
      setLastSearchErr(
        typeof detail === "string"
          ? detail
          : detail?.message
            ? `${detail.message}: ${JSON.stringify(detail.errors ?? {})}`
            : "Search failed"
      );
    }
  };

  const cols = useMemo<ColDef<SupplierProduct>[]>(() => [
    {
      headerName: "", field: "image", maxWidth: 80, sortable: false,
      cellRenderer: (p: ICellRendererParams<SupplierProduct>) =>
        p.value
          ? <img src={p.value} alt="" style={{ width: 40, height: 40, objectFit: "cover", borderRadius: 6 }} />
          : null,
    },
    { headerName: "Title", field: "title", flex: 2, minWidth: 240, tooltipField: "title" },
    {
      headerName: "Source", field: "source", maxWidth: 140,
      cellRenderer: (p: ICellRendererParams<SupplierProduct>) =>
        <Chip label={p.value === "aliexpress_uk" ? "AliExpress UK" : "Amazon UK"} size="small" variant="outlined" />,
    },
    { headerName: "Supplier",  field: "supplier_name", flex: 1, minWidth: 140 },
    { headerName: "Cost",      field: "cost_price",    maxWidth: 90,
      valueFormatter: (p) => `£${p.value}` },
    { headerName: "Shipping",  field: "shipping_cost", maxWidth: 100,
      valueFormatter: (p) => `£${p.value}` },
    { headerName: "Orders",    field: "orders_count",  maxWidth: 100 },
    { headerName: "Rating",    field: "supplier_rating", maxWidth: 100,
      valueFormatter: (p) => p.value != null ? p.value.toFixed(1) : "—" },
    { headerName: "Trend",     field: "trend_score",     maxWidth: 100,
      cellRenderer: (p: ICellRendererParams<SupplierProduct>) => <ScoreChip value={p.value} /> },
    { headerName: "Margin",    field: "margin_score",    maxWidth: 110,
      cellRenderer: (p: ICellRendererParams<SupplierProduct>) => <ScoreChip value={p.value} /> },
    { headerName: "Overall",   field: "overall_score",   maxWidth: 110, sort: "desc",
      cellRenderer: (p: ICellRendererParams<SupplierProduct>) => <ScoreChip value={p.value} /> },
  ], []);

  const update = (patch: Partial<ProductFilters>) =>
    setFilters((f) => ({ ...f, ...patch, page: 1 }));

  const handleCreate = async () => {
    if (selectedId == null) return;
    const listing = await createListing.mutateAsync({ supplier_product_id: selectedId });
    setSelectedId(null);
    navigate("/listings", { state: { highlight: listing.id } });
  };

  return (
    <Stack spacing={2}>
      <Box>
        <Typography variant="h4" sx={{ fontWeight: 800 }}>Discovery</Typography>
        <Typography variant="body2" color="text.secondary">
          Search live UK suppliers, filter for the ones worth listing, drill in, then create a draft.
        </Typography>
      </Box>

      {/* Live supplier search */}
      <Card sx={{ borderColor: "primary.light" }}>
        <CardContent>
          <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems={{ md: "center" }}>
            <TextField
              size="small" fullWidth label="Search live suppliers (e.g. wireless earbuds)"
              value={supplierQuery}
              onChange={(e) => setSupplierQuery(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") runSupplierSearch(); }}
              sx={{ flex: 1 }}
            />
            <FormGroup row sx={{ flexShrink: 0 }}>
              <FormControlLabel
                control={<Checkbox size="small" checked={searchAli} onChange={(e) => setSearchAli(e.target.checked)} />}
                label="AliExpress UK"
              />
              <FormControlLabel
                control={<Checkbox size="small" checked={searchAmz} onChange={(e) => setSearchAmz(e.target.checked)} />}
                label="Amazon UK"
              />
            </FormGroup>
            <Button
              variant="contained"
              startIcon={<SearchIcon />}
              onClick={runSupplierSearch}
              disabled={searchSuppliers.isPending || !supplierQuery.trim()}
              sx={{ flexShrink: 0 }}
            >
              {searchSuppliers.isPending ? "Scraping…" : "Scrape suppliers"}
            </Button>
          </Stack>
          {searchSuppliers.isPending && <LinearProgress sx={{ mt: 1.5 }} />}
          {lastSearchMsg && <Alert severity="success" sx={{ mt: 1.5 }}>{lastSearchMsg}</Alert>}
          {lastSearchErr && <Alert severity="error" sx={{ mt: 1.5 }}>{lastSearchErr}</Alert>}
        </CardContent>
      </Card>

      {/* Filter bar */}
      <Card>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <TextField fullWidth size="small" label="Search title"
                value={filters.q ?? ""} onChange={(e) => update({ q: e.target.value || undefined })} />
            </Grid>
            <Grid item xs={6} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Source</InputLabel>
                <Select label="Source" value={filters.source ?? ""}
                        onChange={(e) => update({ source: e.target.value || undefined })}>
                  {SOURCES.map((s) => <MenuItem key={s.value} value={s.value}>{s.label}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Category</InputLabel>
                <Select label="Category" value={filters.category ?? ""}
                        onChange={(e) => update({ category: e.target.value || undefined })}>
                  <MenuItem value="">All</MenuItem>
                  {(categories.data ?? []).map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6} md={2}>
              <TextField fullWidth size="small" label="Min orders" type="number"
                value={filters.min_orders ?? ""}
                onChange={(e) => update({ min_orders: e.target.value ? Number(e.target.value) : undefined })} />
            </Grid>
            <Grid item xs={6} md={2}>
              <TextField fullWidth size="small" label="Min overall score" type="number"
                value={filters.min_overall ?? ""}
                onChange={(e) => update({ min_overall: e.target.value ? Number(e.target.value) : undefined })} />
            </Grid>
            <Grid item xs={12} md={1}>
              <Button fullWidth variant="text" onClick={() => setFilters({ page: 1, page_size: 100, sort: "overall_score", order: "desc" })}>
                Reset
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Grid */}
      <div className="ag-theme-quartz" style={{ height: 640, width: "100%" }}>
        <AgGridReact
          rowData={products.data?.items ?? []}
          columnDefs={cols}
          loading={products.isLoading}
          onRowClicked={(e) => e.data && setSelectedId(e.data.id)}
          rowHeight={48}
          headerHeight={42}
          suppressCellFocus
          animateRows
          tooltipShowDelay={300}
        />
      </div>
      <Typography variant="caption" color="text.secondary">
        {products.data ? `${products.data.total} products` : "Loading…"}
      </Typography>

      {/* Detail drawer */}
      <Drawer anchor="right" open={selectedId != null} onClose={() => setSelectedId(null)}
              PaperProps={{ sx: { width: { xs: "100%", md: 480 } } }}>
        <Box sx={{ p: 3 }}>
          <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>Product detail</Typography>
            <IconButton onClick={() => setSelectedId(null)}><CloseIcon /></IconButton>
          </Stack>

          {detail.isLoading && <Typography>Loading…</Typography>}

          {detail.data && (
            <Stack spacing={2}>
              {detail.data.image && (
                <img src={detail.data.image} alt=""
                     style={{ width: "100%", height: 220, objectFit: "cover", borderRadius: 8 }} />
              )}
              <Typography variant="h6" sx={{ lineHeight: 1.3 }}>{detail.data.title}</Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                <Chip label={detail.data.source === "aliexpress_uk" ? "AliExpress UK" : "Amazon UK"} size="small" />
                {detail.data.category && <Chip label={detail.data.category} size="small" variant="outlined" />}
                <Chip label={detail.data.supplier_name} size="small" variant="outlined" />
              </Stack>

              <Grid container spacing={2}>
                <Grid item xs={6}><Stat label="Cost"     value={`£${detail.data.cost_price}`} /></Grid>
                <Grid item xs={6}><Stat label="Shipping" value={`£${detail.data.shipping_cost}`} /></Grid>
                <Grid item xs={6}><Stat label="Orders"   value={detail.data.orders_count.toLocaleString()} /></Grid>
                <Grid item xs={6}><Stat label="Reviews"  value={detail.data.reviews_count.toLocaleString()} /></Grid>
              </Grid>

              <Box>
                <Typography variant="overline" color="text.secondary">Scores (0–100)</Typography>
                <Grid container spacing={1} sx={{ mt: 0.5 }}>
                  <Grid item xs={6}><ScoreRow label="Trend"       value={detail.data.trend_score} /></Grid>
                  <Grid item xs={6}><ScoreRow label="Margin"      value={detail.data.margin_score} /></Grid>
                  <Grid item xs={6}><ScoreRow label="Supplier"    value={detail.data.supplier_score} /></Grid>
                  <Grid item xs={6}><ScoreRow label="Competition" value={detail.data.competition_score} /></Grid>
                  <Grid item xs={12}><ScoreRow label="Overall"    value={detail.data.overall_score} bold /></Grid>
                </Grid>
              </Box>

              <Box>
                <Typography variant="overline" color="text.secondary">Margin inputs</Typography>
                <Card variant="outlined" sx={{ p: 1.5, mt: 0.5, fontSize: 12, bgcolor: "background.default" }}>
                  <pre style={{ margin: 0, fontFamily: "monospace", whiteSpace: "pre-wrap" }}>
                    {JSON.stringify(detail.data.margin_inputs, null, 2)}
                  </pre>
                </Card>
              </Box>

              {createListing.isError && (
                <Alert severity="error">
                  {(createListing.error as any)?.response?.data?.detail ?? "Could not create listing"}
                </Alert>
              )}

              <Button variant="contained" size="large" onClick={handleCreate} disabled={createListing.isPending}>
                {createListing.isPending ? "Creating draft…" : "Create draft listing"}
              </Button>
              <Button variant="text" href={detail.data.product_url} target="_blank" rel="noreferrer">
                Open supplier page →
              </Button>
            </Stack>
          )}
        </Box>
      </Drawer>
    </Stack>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <Box>
      <Typography variant="caption" color="text.secondary" sx={{ textTransform: "uppercase", letterSpacing: 1 }}>{label}</Typography>
      <Typography variant="h6" sx={{ fontWeight: 700 }}>{value}</Typography>
    </Box>
  );
}

function ScoreRow({ label, value, bold = false }: { label: string; value: number; bold?: boolean }) {
  return (
    <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", py: 0.5 }}>
      <Typography variant="body2" sx={{ fontWeight: bold ? 700 : 500 }}>{label}</Typography>
      <ScoreChip value={value} />
    </Box>
  );
}
