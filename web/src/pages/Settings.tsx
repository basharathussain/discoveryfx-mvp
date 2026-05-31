import { useEffect, useState } from "react";
import { Alert, Box, Button, Card, CardContent, Stack, TextField, Typography } from "@mui/material";
import { useMarkup, useUpdateMarkup } from "../api/hooks";

export default function SettingsPage() {
  const markup = useMarkup();
  const update = useUpdateMarkup();
  const [pct, setPct] = useState<string>("");

  useEffect(() => {
    if (markup.data && pct === "") setPct(String(markup.data.default_markup_pct));
  }, [markup.data]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" sx={{ fontWeight: 800 }}>Settings</Typography>
        <Typography variant="body2" color="text.secondary">
          Default markup used when suggesting selling prices on new drafts.
        </Typography>
      </Box>

      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>Default markup</Typography>
          <Stack direction="row" spacing={2} alignItems="center">
            <TextField label="Markup %" type="number" value={pct} onChange={(e) => setPct(e.target.value)} sx={{ width: 200 }} />
            <Button
              variant="contained"
              onClick={() => update.mutate({ default_markup_pct: Number(pct) })}
              disabled={update.isPending || pct === ""}
            >
              Save
            </Button>
          </Stack>
          {update.isSuccess && <Alert severity="success" sx={{ mt: 2 }}>Saved.</Alert>}
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Suggested sell price = (cost + shipping) × (1 + markup%). Currency fixed to GBP in MVP.
          </Typography>
        </CardContent>
      </Card>
    </Stack>
  );
}
