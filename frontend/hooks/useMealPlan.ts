"use client";

import { useState, useCallback } from "react";
import toast from "react-hot-toast";
import type { MealPlanRequest, MealPlanResponse } from "@/services/types/meal_plan";
import { createMealPlan } from "@/services/mealPlanService";

interface UseMealPlanReturn {
  plan: MealPlanResponse | null;
  isLoading: boolean;
  generate: (payload: MealPlanRequest) => Promise<void>;
  reset: () => void;
}

export function useMealPlan(): UseMealPlanReturn {
  const [plan, setPlan] = useState<MealPlanResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const generate = useCallback(async (payload: MealPlanRequest): Promise<void> => {
    setIsLoading(true);
    try {
      const result = await createMealPlan(payload);
      setPlan(result);
      toast.success("Your personalised meal plan is ready!");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to generate meal plan.");
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => setPlan(null), []);

  return { plan, isLoading, generate, reset };
}
