import { useState } from "react";
import { Box, Button, Card, CardContent, Stack, TextField, Typography, Alert } from "@mui/material";
import { Link, useNavigate } from "react-router-dom";

import { useSignup } from "../api/hooks";
import { useAuthStore } from "../stores/authStore";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const signup = useSignup();
  const setTokens = useAuthStore((s) => s.setTokens);
  const navigate = useNavigate();

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null);
    try {
      const tok = await signup.mutateAsync({ email, password });
      setTokens(tok.access_token, tok.refresh_token);
      navigate("/discovery");
    } catch (e: any) {
      setErr(e?.response?.data?.detail ?? "Signup failed");
    }
  };

  return (
    <Box sx={{ minHeight: "100vh", display: "grid", placeItems: "center", bgcolor: "background.default" }}>
      <Card sx={{ width: 400, p: 1 }}>
        <CardContent>
          <Typography variant="h5" sx={{ fontWeight: 800, mb: 0.5 }}>Create an account</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Start finding UK supplier opportunities in under a minute.
          </Typography>
          <form onSubmit={submit}>
            <Stack spacing={2}>
              {err && <Alert severity="error">{err}</Alert>}
              <TextField label="Email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} autoFocus />
              <TextField label="Password (min 8 chars)" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
              <Button type="submit" variant="contained" disabled={signup.isPending} size="large">
                {signup.isPending ? "Creating…" : "Create account"}
              </Button>
              <Typography variant="body2" color="text.secondary">
                Already have an account? <Link to="/login">Sign in</Link>.
              </Typography>
            </Stack>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
}
