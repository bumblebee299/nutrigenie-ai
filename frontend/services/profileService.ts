/**
 * Profile API service — calls to /profile/* endpoints.
 */
import type { ProfileResponse, ProfileUpdate } from "@/services/types/profile";
import apiClient from "@/services/apiClient";

export async function getProfile(userId: string): Promise<ProfileResponse> {
  const { data } = await apiClient.get<ProfileResponse>(`/profile/${userId}`);
  return data;
}

export async function updateProfile(
  userId: string,
  payload: ProfileUpdate
): Promise<ProfileResponse> {
  const { data } = await apiClient.patch<ProfileResponse>(`/profile/${userId}`, payload);
  return data;
}
