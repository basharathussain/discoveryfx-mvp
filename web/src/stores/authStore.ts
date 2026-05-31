import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  setTokens: (a: string, r: string) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      setTokens: (a, r) => set({ accessToken: a, refreshToken: r }),
      clear: () => set({ accessToken: null, refreshToken: null }),
    }),
    { name: "discoveryfx-auth" }
  )
);
