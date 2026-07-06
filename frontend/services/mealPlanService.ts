/**
 * Meal plan API service — calls to POST /meal-plan/.
 */
import type { MealPlanRequest, MealPlanResponse } from "@/services/types/meal_plan";
import apiClient from "@/services/apiClient";

export async function createMealPlan(payload: MealPlanRequest): Promise<MealPlanResponse> {
  const { data } = await apiClient.post<MealPlanResponse>("/meal-plan/", payload);
  return data;
}
