import axios, { AxiosError, AxiosInstance } from "axios";
import { useAuthStore } from "../stores/authStore";

// In dev (vite), API is proxied via Vite/nginx — relative paths work.
// We use a relative base so dev (port 5173 → nginx?) and prod both work.
export const apiClient: AxiosInstance = axios.create({
  baseURL: "/api",
  timeout: 30_000,
});

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (r) => r,
  (err: AxiosError) => {
    if (err.response?.status === 401) {
      useAuthStore.getState().clear();
      if (typeof window !== "undefined" && window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);
