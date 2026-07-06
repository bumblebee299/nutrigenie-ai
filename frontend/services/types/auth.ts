/**
 * Shared TypeScript types for Authentication.
 * These mirror the backend Pydantic models exactly.
 */

export interface RegisterCredentials {
  name: string;
  email: string;
  password: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserPublic {
  id: string;
  name: string;
  email: string;
  created_at: string;
  is_active: boolean;
}
