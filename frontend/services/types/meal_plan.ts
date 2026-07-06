/**
 * Shared TypeScript types for the Meal Planner.
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

export interface Meal {
  name: string;
  ingredients: string[];
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  preparation_time_minutes: number;
  instructions: string;
  explanation: string;
}

export interface DailyNutritionSummary {
  total_calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
  water_ml: number;
}

export interface MealPlanRequest {
  user_id: string;
  age: number;
  height_cm: number;
  weight_kg: number;
  gender: Gender;
  goal: GoalType;
  diseases: string[];
  allergies: string[];
  cuisine_preference: string[];
  budget_usd_per_day?: number | null;
  lifestyle: Lifestyle;
}

export interface MealPlanResponse {
  user_id: string;
  breakfast: Meal;
  lunch: Meal;
  dinner: Meal;
  snacks: Meal[];
  nutrition_summary: DailyNutritionSummary;
  explanation: string;
}
