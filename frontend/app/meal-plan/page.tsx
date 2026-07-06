"use client";

import { RefreshCw } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { useMealPlan } from "@/hooks/useMealPlan";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { MealPlanForm } from "@/components/meal-plan/MealPlanForm";
import { MealCard } from "@/components/meal-plan/MealCard";
import { NutritionSummaryCard } from "@/components/meal-plan/NutritionSummaryCard";
import type { MealPlanRequest } from "@/services/types/meal_plan";

const MEAL_SECTIONS = [
  { key: "breakfast" as const, label: "Breakfast", color: "yellow" },
  { key: "lunch" as const, label: "Lunch", color: "green" },
  { key: "dinner" as const, label: "Dinner", color: "blue" },
];

function MealPlanPageContent() {
  const { user } = useAuth();
  const { plan, isLoading, generate, reset } = useMealPlan();

  async function handleGenerate(payload: MealPlanRequest) {
    await generate(payload);
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Meal Planner</h1>
          <p className="text-gray-400 text-sm mt-1">
            AI-generated personalised daily nutrition plan
          </p>
        </div>
        {plan && (
          <button
            onClick={reset}
            className="btn-secondary flex items-center gap-2 text-sm"
          >
            <RefreshCw size={14} />
            New Plan
          </button>
        )}
      </div>

      {/* Form — hidden once plan is generated */}
      {!plan && (
        <MealPlanForm
          userId={user?.id ?? ""}
          onSubmit={handleGenerate}
          isLoading={isLoading}
        />
      )}

      {/* Results */}
      {plan && (
        <div className="space-y-6 animate-fade-in">
          {/* Overall explanation */}
          <div className="rounded-xl bg-gray-900 border border-brand-800 p-4">
            <p className="text-xs font-medium text-brand-400 uppercase tracking-wide mb-1">
              Why this plan?
            </p>
            <p className="text-sm text-gray-300 leading-relaxed">{plan.explanation}</p>
          </div>

          {/* Meals + nutrition summary */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left: Meal cards */}
            <div className="lg:col-span-2 space-y-4">
              {MEAL_SECTIONS.map(({ key, label, color }) => (
                <MealCard
                  key={key}
                  title={label}
                  meal={plan[key]}
                  accentColor={color}
                />
              ))}

              {/* Snacks */}
              {plan.snacks.length > 0 && (
                <div className="space-y-3">
                  <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wide">
                    Snacks
                  </h3>
                  {plan.snacks.map((snack, i) => (
                    <MealCard
                      key={i}
                      title={`Snack ${i + 1}`}
                      meal={snack}
                      accentColor="purple"
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Right: Nutrition summary */}
            <div className="lg:col-span-1">
              <NutritionSummaryCard
                summary={plan.nutrition_summary}
                targetCalories={plan.nutrition_summary.total_calories}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function MealPlanPage() {
  return (
    <ProtectedRoute>
      <MealPlanPageContent />
    </ProtectedRoute>
  );
}
