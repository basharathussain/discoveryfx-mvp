import {
  AppBar, Avatar, Box, Drawer, IconButton, List, ListItemButton, ListItemIcon, ListItemText, Toolbar, Typography,
} from "@mui/material";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

import DashboardIcon from "@mui/icons-material/Dashboard";
import SearchIcon from "@mui/icons-material/Search";
import InventoryIcon from "@mui/icons-material/Inventory2";
import ReceiptIcon from "@mui/icons-material/Receipt";
import StoreIcon from "@mui/icons-material/Store";
import SettingsIcon from "@mui/icons-material/Settings";
import LogoutIcon from "@mui/icons-material/Logout";

import { useAuthStore } from "../stores/authStore";
import { useMe } from "../api/hooks";

const DRAWER_WIDTH = 240;

const NAV = [
  { label: "Dashboard",          to: "/dashboard", icon: <DashboardIcon /> },
  { label: "Discovery",          to: "/discovery", icon: <SearchIcon /> },
  { label: "Listings",           to: "/listings",  icon: <InventoryIcon /> },
  { label: "Orders",             to: "/orders",    icon: <ReceiptIcon /> },
  { label: "Store integrations", to: "/stores",    icon: <StoreIcon /> },
  { label: "Settings",           to: "/settings",  icon: <SettingsIcon /> },
];

export default function AppShell() {
  const navigate = useNavigate();
  const loc = useLocation();
  const clear = useAuthStore((s) => s.clear);
  const me = useMe();

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <Drawer
        variant="permanent"
        sx={{
          width: DRAWER_WIDTH, flexShrink: 0,
          "& .MuiDrawer-paper": { width: DRAWER_WIDTH, boxSizing: "border-box", borderRight: "1px solid #e8ecf3" },
        }}
      >
        <Box sx={{ p: 2.5, display: "flex", alignItems: "center", gap: 1.5 }}>
          <Avatar sx={{ bgcolor: "primary.main", fontWeight: 800 }}>D</Avatar>
          <Typography variant="h6" sx={{ fontWeight: 800, letterSpacing: -0.3 }}>
            DiscoveryFX
          </Typography>
        </Box>
        <List sx={{ px: 1 }}>
          {NAV.map((n) => {
            const selected = loc.pathname.startsWith(n.to);
            return (
              <ListItemButton
                key={n.to}
                selected={selected}
                onClick={() => navigate(n.to)}
                sx={{ borderRadius: 1.5, mb: 0.5 }}
              >
                <ListItemIcon sx={{ minWidth: 36, color: selected ? "primary.main" : "inherit" }}>{n.icon}</ListItemIcon>
                <ListItemText primary={n.label} primaryTypographyProps={{ fontWeight: selected ? 700 : 500 }} />
              </ListItemButton>
            );
          })}
        </List>
      </Drawer>

      <Box sx={{ flex: 1, display: "flex", flexDirection: "column" }}>
        <AppBar
          position="sticky"
          elevation={0}
          color="inherit"
          sx={{ borderBottom: "1px solid #e8ecf3", bgcolor: "#fff" }}
        >
          <Toolbar sx={{ justifyContent: "space-between" }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, color: "text.secondary" }}>
              UK · GBP · Sandbox
            </Typography>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <Typography variant="body2" sx={{ color: "text.secondary" }}>
                {me.data?.email ?? "…"}
              </Typography>
              <IconButton
                onClick={() => { clear(); navigate("/login"); }}
                aria-label="Sign out"
                size="small"
              >
                <LogoutIcon />
              </IconButton>
            </Box>
          </Toolbar>
        </AppBar>

        <Box component="main" sx={{ p: { xs: 2, md: 3 } }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
