"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuth } from "@/hooks/useAuth";
import { useProfile, useUpdateProfile } from "@/hooks/useProfile";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import type { ProfileUpdate } from "@/services/types/profile";

const profileSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters.").optional(),
  age: z.coerce.number().int().min(1).max(120).optional(),
  height_cm: z.coerce.number().min(50).max(300).optional(),
  weight_kg: z.coerce.number().min(10).max(500).optional(),
  gender: z.enum(["male", "female", "other"]).optional(),
  goal: z
    .enum(["weight_loss", "weight_gain", "maintenance", "muscle_gain"])
    .optional(),
  lifestyle: z
    .enum([
      "sedentary",
      "lightly_active",
      "moderately_active",
      "very_active",
      "extra_active",
    ])
    .optional(),
});

type ProfileFormValues = z.infer<typeof profileSchema>;

function ProfilePageContent() {
  const { user, logout } = useAuth();
  const { data: profile, isLoading } = useProfile(user?.id ?? "");
  const { mutate: updateProfile, isPending } = useUpdateProfile(user?.id ?? "");

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    values: {
      name: profile?.name,
      age: profile?.age ?? undefined,
      height_cm: profile?.height_cm ?? undefined,
      weight_kg: profile?.weight_kg ?? undefined,
      gender: profile?.gender ?? undefined,
      goal: profile?.goal ?? undefined,
      lifestyle: profile?.lifestyle ?? undefined,
    },
  });

  function onSubmit(values: ProfileFormValues) {
    updateProfile(values as ProfileUpdate);
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-gray-400 animate-pulse">Loading profile…</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">My Profile</h1>
          <p className="text-gray-400 text-sm mt-1">{user?.email}</p>
        </div>
        <button onClick={logout} className="btn-secondary text-sm">
          Sign out
        </button>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="card space-y-5">
        <h2 className="text-lg font-semibold text-white border-b border-gray-800 pb-3">
          Personal Information
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          {/* Name */}
          <div className="sm:col-span-2">
            <label htmlFor="name" className="label">
              Full name
            </label>
            <input id="name" type="text" className="input-field" {...register("name")} />
            {errors.name && <p className="mt-1 text-sm text-red-400">{errors.name.message}</p>}
          </div>

          {/* Age */}
          <div>
            <label htmlFor="age" className="label">
              Age
            </label>
            <input id="age" type="number" className="input-field" {...register("age")} />
          </div>

          {/* Gender */}
          <div>
            <label htmlFor="gender" className="label">
              Gender
            </label>
            <select id="gender" className="input-field" {...register("gender")}>
              <option value="">Select…</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>

          {/* Height */}
          <div>
            <label htmlFor="height_cm" className="label">
              Height (cm)
            </label>
            <input
              id="height_cm"
              type="number"
              step="0.1"
              className="input-field"
              {...register("height_cm")}
            />
          </div>

          {/* Weight */}
          <div>
            <label htmlFor="weight_kg" className="label">
              Weight (kg)
            </label>
            <input
              id="weight_kg"
              type="number"
              step="0.1"
              className="input-field"
              {...register("weight_kg")}
            />
          </div>

          {/* Goal */}
          <div>
            <label htmlFor="goal" className="label">
              Goal
            </label>
            <select id="goal" className="input-field" {...register("goal")}>
              <option value="">Select…</option>
              <option value="weight_loss">Weight Loss</option>
              <option value="weight_gain">Weight Gain</option>
              <option value="maintenance">Maintenance</option>
              <option value="muscle_gain">Muscle Gain</option>
            </select>
          </div>

          {/* Lifestyle */}
          <div>
            <label htmlFor="lifestyle" className="label">
              Lifestyle
            </label>
            <select id="lifestyle" className="input-field" {...register("lifestyle")}>
              <option value="">Select…</option>
              <option value="sedentary">Sedentary</option>
              <option value="lightly_active">Lightly Active</option>
              <option value="moderately_active">Moderately Active</option>
              <option value="very_active">Very Active</option>
              <option value="extra_active">Extra Active</option>
            </select>
          </div>
        </div>

        <div className="pt-2 border-t border-gray-800">
          <button type="submit" disabled={isPending} className="btn-primary">
            {isPending ? "Saving…" : "Save changes"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <ProfilePageContent />
    </ProtectedRoute>
  );
}
