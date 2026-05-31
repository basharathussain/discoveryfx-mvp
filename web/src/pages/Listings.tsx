import { useState } from "react";
import { Alert, Box, Button, Card, CardContent, Chip, Snackbar, Stack, Typography } from "@mui/material";
import { useListings, usePublishListing } from "../api/hooks";

const STATUS_COLOR: Record<string, "default" | "primary" | "success" | "warning" | "error"> = {
  draft: "default", active: "success", paused: "warning", ended: "default", failed: "error",
};

export default function Listings() {
  const drafts = useListings("draft");
  const active = useListings("active");
  const failed = useListings("failed");
  const publish = usePublishListing();
  const [msg, setMsg] = useState<string | null>(null);

  const onPublish = async (id: number) => {
    try {
      await publish.mutateAsync(id);
      setMsg("Published to eBay UK.");
    } catch (e: any) {
      setMsg(e?.response?.data?.detail ?? "Publish failed.");
    }
  };

  const sections = [
    { title: "Drafts",           data: drafts.data ?? [],  hint: "Edit details, then publish to eBay." },
    { title: "Active on eBay UK", data: active.data ?? [], hint: "Currently published listings." },
    { title: "Failed",           data: failed.data ?? [], hint: "Publish errors — fix and retry." },
  ];

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" sx={{ fontWeight: 800 }}>Listings</Typography>
        <Typography variant="body2" color="text.secondary">
          Drafts you’re preparing, what’s live on eBay UK, and what failed to publish.
        </Typography>
      </Box>

      <Snackbar
        open={msg != null}
        autoHideDuration={5000}
        onClose={() => setMsg(null)}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          severity={msg?.includes("Published") ? "success" : "warning"}
          onClose={() => setMsg(null)}
        >
          {msg}
        </Alert>
      </Snackbar>

      {sections.map((s) => (
        <Card key={s.title}>
          <CardContent>
            <Stack direction="row" alignItems="baseline" justifyContent="space-between" sx={{ mb: 1.5 }}>
              <Typography variant="h6" sx={{ fontWeight: 700 }}>{s.title}</Typography>
              <Typography variant="caption" color="text.secondary">{s.hint}</Typography>
            </Stack>

            {s.data.length === 0 ? (
              <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
                Nothing here yet.
              </Typography>
            ) : (
              <Stack divider={<Box sx={{ borderBottom: "1px solid #eef0f5" }} />} spacing={0}>
                {s.data.map((l) => (
                  <Box key={l.id} sx={{ display: "flex", py: 1.5, gap: 2, alignItems: "center" }}>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="body1" sx={{ fontWeight: 600 }}>{l.title}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        £{l.selling_price} sell · £{l.profit_margin} margin · created {new Date(l.created_at).toLocaleDateString()}
                      </Typography>
                    </Box>
                    <Chip size="small" label={l.status} color={STATUS_COLOR[l.status] ?? "default"} />
                    {l.ebay_item_id && (
                      <Chip size="small" variant="outlined" label={`eBay #${l.ebay_item_id}`} />
                    )}
                    {l.status === "draft" && (
                      <Button size="small" variant="contained"
                              onClick={() => onPublish(l.id)} disabled={publish.isPending}>
                        Publish
                      </Button>
                    )}
                  </Box>
                ))}
              </Stack>
            )}
          </CardContent>
        </Card>
      ))}
    </Stack>
  );
}
