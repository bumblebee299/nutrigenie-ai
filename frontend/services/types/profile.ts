/**
 * Shared TypeScript types for User Profile.
 * These mirror the backend Pydantic models exactly.
 */

export type Gender = "male" | "female" | "other";
export type GoalType = "weight_loss" | "weight_gain" | "maintenance" | "muscle_gain";
export type Lifestyle =
  | "sedentary"
  | "lightly_active"
  | "moderately_active"
  | "very_active"
  | "extra_active";

export interface ProfileResponse {
  id: string;
  name: string;
  email: string;
  age: number | null;
  height_cm: number | null;
  weight_kg: number | null;
  gender: Gender | null;
  goal: GoalType | null;
  diseases: string[];
  allergies: string[];
  cuisine_preference: string[];
  lifestyle: Lifestyle | null;
  created_at: string;
  updated_at: string | null;
}

export interface ProfileUpdate {
  name?: string;
  age?: number;
  height_cm?: number;
  weight_kg?: number;
  gender?: Gender;
  goal?: GoalType;
  diseases?: string[];
  allergies?: string[];
  cuisine_preference?: string[];
  lifestyle?: Lifestyle;
}
