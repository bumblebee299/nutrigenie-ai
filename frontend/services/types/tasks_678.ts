/**
 * TypeScript types for Tasks 6, 7, and 8.
 */

// ── Task 6: Food Swap ─────────────────────────────────────────────────────

export interface SwapOption {
  original: string;
  healthier_option: string;
  calorie_reduction: number;
  benefits: string[];
  preparation_tip: string;
  explanation: string;
}

export interface FoodSwapRequest {
  food_item: string;
  user_id: string;
  dietary_restrictions: string[];
}

export interface FoodSwapResponse {
  original_food: string;
  swaps: SwapOption[];
  general_advice: string;
}

// ── Task 7: Label Analysis ────────────────────────────────────────────────

export interface NutrientDetail {
  name: string;
  amount: string;
  daily_value_percent: number | null;
  assessment: string;
}

export interface LabelWarning {
  category: string;
  message: string;
  severity: "low" | "medium" | "high";
}

export interface LabelAnalysisResponse {
  product_name: string | null;
  serving_size: string;
  calories_per_serving: number;
  sugar: NutrientDetail;
  fat: NutrientDetail;
  protein: NutrientDetail;
  sodium: NutrientDetail;
  additional_nutrients: NutrientDetail[];
  warnings: LabelWarning[];
  overall_assessment: string;
  explanation: string;
}

// ── Task 8: Dashboard ────────────────────────────────────────────────────

export interface DailyEntry {
  date: string;
  calories_consumed: number;
  protein_g: number;
  water_ml: number;
  weight_kg: number | null;
  meals?: {
    type: string;
    name: string;
    calories: number;
    protein_g: number;
    logged_at: string;
  }[] | null;
  feedback_rating?: number | null;
  feedback_comment?: string | null;
}

export interface WeeklySummary {
  avg_calories: number;
  avg_protein_g: number;
  avg_water_ml: number;
  weight_change_kg: number | null;
  goal_adherence_percent: number;
}

export interface ChartPoint {
  date: string;
  value: number | null;
}

export interface GoalTargets {
  calorie_target: number;
  protein_target_g: number;
  water_target_ml: number;
}

export interface DashboardResponse {
  user_id: string;
  week_start: string;
  week_end: string;
  daily_entries: DailyEntry[];
  summary: WeeklySummary;
  charts_data: {
    calories: ChartPoint[];
    protein: ChartPoint[];
    water: ChartPoint[];
    weight: ChartPoint[];
  };
  goals?: GoalTargets | null;
}

// ── Log Request Payloads ───────────────────────────────────────────

export interface LogMealRequest {
  date: string;
  type: string; // "breakfast" | "lunch" | "dinner" | "snack"
  name: string;
  calories: number;
  protein_g: number;
}

export interface LogWaterRequest {
  date: string;
  amount_ml: number;
}

export interface LogWeightRequest {
  date: string;
  weight_kg: number;
}

export interface LogFeedbackRequest {
  date: string;
  rating: number; // 1-5
  comment?: string | null;
}

