import { useState } from "react";
import { Box, Button, Card, CardContent, Stack, TextField, Typography, Alert } from "@mui/material";
import { Link, useNavigate } from "react-router-dom";

import { useLogin } from "../api/hooks";
import { useAuthStore } from "../stores/authStore";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const login = useLogin();
  const setTokens = useAuthStore((s) => s.setTokens);
  const navigate = useNavigate();

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null);
    try {
      const tok = await login.mutateAsync({ email, password });
      setTokens(tok.access_token, tok.refresh_token);
      navigate("/discovery");
    } catch (e: any) {
      setErr(e?.response?.data?.detail ?? "Login failed");
    }
  };

  return (
    <Box sx={{ minHeight: "100vh", display: "grid", placeItems: "center", bgcolor: "background.default" }}>
      <Card sx={{ width: 400, p: 1 }}>
        <CardContent>
          <Typography variant="h5" sx={{ fontWeight: 800, mb: 0.5 }}>DiscoveryFX</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Sign in to your UK product-discovery workspace.
          </Typography>
          <form onSubmit={submit}>
            <Stack spacing={2}>
              {err && <Alert severity="error">{err}</Alert>}
              <TextField label="Email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} autoFocus />
              <TextField label="Password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
              <Button type="submit" variant="contained" disabled={login.isPending} size="large">
                {login.isPending ? "Signing in…" : "Sign in"}
              </Button>
              <Typography variant="body2" color="text.secondary">
                No account? <Link to="/signup">Create one</Link>.
              </Typography>
            </Stack>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
}
