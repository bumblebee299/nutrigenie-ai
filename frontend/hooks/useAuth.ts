"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import type { UserPublic, LoginCredentials, RegisterCredentials } from "@/services/types/auth";
import {
  login as loginService,
  register as registerService,
  logout as logoutService,
  getMe,
  isAuthenticated,
} from "@/services/authService";

interface UseAuthReturn {
  user: UserPublic | null;
  isLoading: boolean;
  isLoggedIn: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => Promise<void>;
}

export function useAuth(): UseAuthReturn {
  const router = useRouter();
  const [user, setUser] = useState<UserPublic | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch the current user on mount if a token is present
  useEffect(() => {
    if (!isAuthenticated()) {
      setIsLoading(false);
      return;
    }

    getMe()
      .then(setUser)
      .catch(() => {
        // Token may be expired — clear it silently
        setUser(null);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const login = useCallback(
    async (credentials: LoginCredentials): Promise<void> => {
      setIsLoading(true);
      try {
        await loginService(credentials);
        const me = await getMe();
        setUser(me);
        toast.success(`Welcome back, ${me.name}!`);
        router.push("/dashboard");
      } catch (err) {
        toast.error(err instanceof Error ? err.message : "Login failed.");
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [router]
  );

  const register = useCallback(
    async (credentials: RegisterCredentials): Promise<void> => {
      setIsLoading(true);
      try {
        await registerService(credentials);
        // Immediately log in after registration
        await loginService({ email: credentials.email, password: credentials.password });
        const me = await getMe();
        setUser(me);
        toast.success(`Welcome to NutriGenie AI, ${me.name}!`);
        router.push("/dashboard");
      } catch (err) {
        toast.error(err instanceof Error ? err.message : "Registration failed.");
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [router]
  );

  const logout = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    try {
      await logoutService();
      setUser(null);
      toast.success("You have been logged out.");
      router.push("/auth/login");
    } catch {
      // Still clear local state even if the server call fails
      setUser(null);
      router.push("/auth/login");
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  return {
    user,
    isLoading,
    isLoggedIn: Boolean(user),
    login,
    register,
    logout,
  };
}
