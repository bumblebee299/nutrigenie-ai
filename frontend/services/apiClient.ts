/**
 * Axios instance pre-configured with the backend base URL,
 * auth token injection, and automatic silent token refresh.
 *
 * The refresh call uses a raw axios instance (not this client) to
 * avoid a circular dependency with authService.
 */
import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from "axios";

const _BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

// ── Token helpers (kept local to avoid circular deps) ─────────────────────
function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("refresh_token");
}

function persistTokens(access: string, refresh: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
}

function clearTokens(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

// ── Core axios instance ───────────────────────────────────────────────────
const apiClient: AxiosInstance = axios.create({
  baseURL: _BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 1_20_000,
});

// Track in-flight refresh to prevent duplicate simultaneous refresh calls
let _refreshPromise: Promise<void> | null = null;

// ── Request interceptor — attach access token ─────────────────────────────
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Response interceptor — silent token refresh on 401 ───────────────────
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Attempt one silent refresh on a 401 that has not already been retried
    if (error?.response?.status === 401 && !original._retry && getRefreshToken()) {
      original._retry = true;

      if (!_refreshPromise) {
        _refreshPromise = axios
          .post<{ access_token: string; refresh_token: string }>(
            `${_BASE_URL}/auth/refresh`,
            { refresh_token: getRefreshToken() }
          )
          .then(({ data }) => {
            persistTokens(data.access_token, data.refresh_token);
            _refreshPromise = null;
          })
          .catch(() => {
            _refreshPromise = null;
            clearTokens();
            if (typeof window !== "undefined") {
              window.location.href = "/auth/login";
            }
          });
      }

      await _refreshPromise;
      return apiClient(original);
    }

    const message: string =
      error?.response?.data?.detail ?? error?.message ?? "An unexpected error occurred.";
    return Promise.reject(new Error(message));
  }
);

export default apiClient;
