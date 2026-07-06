"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import type { ProfileResponse, ProfileUpdate } from "@/services/types/profile";
import { getProfile, updateProfile } from "@/services/profileService";

export function useProfile(userId: string) {
  return useQuery<ProfileResponse, Error>({
    queryKey: ["profile", userId],
    queryFn: () => getProfile(userId),
    enabled: Boolean(userId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useUpdateProfile(userId: string) {
  const queryClient = useQueryClient();

  return useMutation<ProfileResponse, Error, ProfileUpdate>({
    mutationFn: (payload) => updateProfile(userId, payload),
    onSuccess: (updated) => {
      queryClient.setQueryData(["profile", userId], updated);
      toast.success("Profile updated successfully.");
    },
    onError: (err) => {
      toast.error(err.message ?? "Failed to update profile.");
    },
  });
}
