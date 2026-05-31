import { Box, Card, CardContent, Grid, Stack, Typography } from "@mui/material";
import { useListings, useProducts } from "../api/hooks";

function StatCard({ label, value, hint }: { label: string; value: string | number; hint?: string }) {
  return (
    <Card>
      <CardContent>
        <Typography variant="caption" color="text.secondary" sx={{ textTransform: "uppercase", letterSpacing: 1 }}>
          {label}
        </Typography>
        <Typography variant="h4" sx={{ fontWeight: 800, mt: 0.5 }}>
          {value}
        </Typography>
        {hint && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>{hint}</Typography>
        )}
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const allProducts = useProducts({ page: 1, page_size: 1 });
  const aliProducts = useProducts({ page: 1, page_size: 1, source: "aliexpress_uk" });
  const amzProducts = useProducts({ page: 1, page_size: 1, source: "amazon_uk" });
  const drafts = useListings("draft");
  const active = useListings("active");

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" sx={{ fontWeight: 800 }}>Dashboard</Typography>
        <Typography variant="body2" color="text.secondary">
          UK-first discovery workspace. Live numbers across the system.
        </Typography>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="Supplier products" value={allProducts.data?.total ?? "…"} hint="across all sources" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="From AliExpress UK" value={aliProducts.data?.total ?? "…"} />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="From Amazon UK" value={amzProducts.data?.total ?? "…"} />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard label="Drafts" value={drafts.data?.length ?? "…"} hint={`${active.data?.length ?? 0} published`} />
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>Get started</Typography>
          <Typography variant="body2" color="text.secondary">
            Open <b>Discovery</b> to browse supplier products, filter by margin / orders / trend, then create a draft
            listing. In Phase 3, publish drafts directly to eBay UK (sandbox).
          </Typography>
        </CardContent>
      </Card>
    </Stack>
  );
}
