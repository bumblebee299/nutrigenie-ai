/**
 * Shared TypeScript types for Food Image Analysis.
 * These mirror the backend Pydantic models exactly.
 */

export interface FoodItem {
  name: string;
  confidence: number;
  estimated_calories: number;
  portion_size: string;
}

export interface HealthierAlternative {
  original: string;
  alternative: string;
  reason: string;
  calorie_difference: number;
}

export interface ImageAnalysisResponse {
  detected_foods: FoodItem[];
  total_estimated_calories: number;
  healthier_alternatives: HealthierAlternative[];
  nutritional_notes: string;
  explanation: string;
  image_url: string | null;
}
