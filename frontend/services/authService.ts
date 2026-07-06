/**
 * Authentication API service — all calls to /auth/* endpoints.
 *
 * Token storage helpers are kept here so that application code can import
 * them without touching apiClient (which handles token refresh internally).
 */
import type {
  LoginCredentials,
  RegisterCredentials,
  TokenResponse,
  UserPublic,
} from "@/services/types/auth";
import apiClient from "@/services/apiClient";

export async function register(credentials: RegisterCredentials): Promise<UserPublic> {
  const { data } = await apiClient.post<UserPublic>("/auth/register", credentials);
  return data;
}

export async function login(credentials: LoginCredentials): Promise<TokenResponse> {
  // FastAPI OAuth2PasswordRequestForm expects form-encoded data
  const form = new URLSearchParams();
  form.append("username", credentials.email);
  form.append("password", credentials.password);

  const { data } = await apiClient.post<TokenResponse>("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });

  // Persist tokens so apiClient interceptor can read them
  if (typeof window !== "undefined") {
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
  }

  return data;
}

export async function logout(): Promise<void> {
  try {
    await apiClient.post("/auth/logout");
  } finally {
    clearTokens();
  }
}

export async function getMe(): Promise<UserPublic> {
  const { data } = await apiClient.get<UserPublic>("/auth/me");
  return data;
}

// ── Token storage helpers ─────────────────────────────────────────────────

export function clearTokens(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("refresh_token");
}

export function isAuthenticated(): boolean {
  return Boolean(getAccessToken());
}
