import { useState } from "react";
import { Alert, Box, Button, Card, CardContent, Chip, Stack, TextField, Typography } from "@mui/material";
import { useCreateStubStore, useStores } from "../api/hooks";

export default function Stores() {
  const stores = useStores();
  const create = useCreateStubStore();
  const [name, setName] = useState("My eBay UK store");

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" sx={{ fontWeight: 800 }}>Store integrations</Typography>
        <Typography variant="body2" color="text.secondary">
          eBay UK only in MVP. OAuth comes in Phase 3 — for now you can create a placeholder
          store so the listing flow works.
        </Typography>
      </Box>

      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>Connected stores</Typography>
          {stores.data && stores.data.length === 0 && (
            <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
              No stores yet.
            </Typography>
          )}
          <Stack spacing={1.5} sx={{ mt: 1 }}>
            {stores.data?.map((s) => (
              <Box key={s.id} sx={{ display: "flex", alignItems: "center", gap: 2, py: 1 }}>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="body1" sx={{ fontWeight: 600 }}>{s.store_name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {s.platform.toUpperCase()} · region {s.region}
                  </Typography>
                </Box>
                <Chip size="small" label={s.status} />
              </Box>
            ))}
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>Quick-add placeholder store (Phase 1)</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Real eBay OAuth is scheduled for Phase 3. Until then, this creates a
            placeholder store so you can attach drafts to a store.
          </Typography>
          <Stack direction="row" spacing={2} alignItems="center">
            <TextField size="small" label="Store name" value={name} onChange={(e) => setName(e.target.value)} sx={{ flex: 1 }} />
            <Button
              variant="contained"
              onClick={() => create.mutate({ store_name: name, region: "GB" })}
              disabled={create.isPending}
            >
              Add placeholder
            </Button>
          </Stack>
          {create.isError && <Alert severity="error" sx={{ mt: 2 }}>Could not create store.</Alert>}
        </CardContent>
      </Card>
    </Stack>
  );
}
