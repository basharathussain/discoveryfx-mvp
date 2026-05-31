import { Box, Card, CardContent, Chip, Stack, Typography } from "@mui/material";
import { useOrders } from "../api/hooks";

export default function Orders() {
  const orders = useOrders();

  return (
    <Stack spacing={2}>
      <Box>
        <Typography variant="h4" sx={{ fontWeight: 800 }}>Orders</Typography>
        <Typography variant="body2" color="text.secondary">
          eBay UK orders that came in on your published listings. Phase 3 wires the live pull.
        </Typography>
      </Box>

      <Card>
        <CardContent>
          {orders.data && orders.data.length === 0 && (
            <Typography variant="body2" color="text.secondary" sx={{ py: 4, textAlign: "center" }}>
              No orders yet. Once a listing is published and a buyer purchases on eBay UK sandbox,
              the order appears here.
            </Typography>
          )}

          {orders.data?.map((o) => (
            <Box key={o.id} sx={{ display: "flex", py: 1.5, gap: 2, alignItems: "center", borderBottom: "1px solid #eef0f5" }}>
              <Box sx={{ flex: 1 }}>
                <Typography variant="body1" sx={{ fontWeight: 600 }}>eBay #{o.ebay_order_id}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {o.buyer_name ?? "—"} · {new Date(o.created_at).toLocaleString()}
                </Typography>
              </Box>
              <Typography variant="body1" sx={{ fontWeight: 700 }}>£{o.total}</Typography>
              <Chip size="small" label={o.order_status} />
            </Box>
          ))}
        </CardContent>
      </Card>
    </Stack>
  );
}
