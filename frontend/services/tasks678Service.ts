/**
 * API services for Tasks 6, 7, 8.
 */
import type {
  FoodSwapRequest,
  FoodSwapResponse,
  LabelAnalysisResponse,
  DashboardResponse,
  LogMealRequest,
  LogWaterRequest,
  LogWeightRequest,
  LogFeedbackRequest,
} from "@/services/types/tasks_678";
import apiClient from "@/services/apiClient";

// ── Food Swap ────────────────────────────────────────────────────────────

export async function getFoodSwaps(payload: FoodSwapRequest): Promise<FoodSwapResponse> {
  const { data } = await apiClient.post<FoodSwapResponse>("/food-swap/", payload);
  return data;
}

// ── Label Analysis ────────────────────────────────────────────────────────

export async function analyseLabel(
  labelImage: File,
  userId: string
): Promise<LabelAnalysisResponse> {
  const form = new FormData();
  form.append("user_id", userId);
  form.append("label_image", labelImage);
  const { data } = await apiClient.post<LabelAnalysisResponse>("/label-analysis/", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

// ── Dashboard ────────────────────────────────────────────────────────────

export async function getWeeklyDashboard(
  userId: string,
  weekStart: string
): Promise<DashboardResponse> {
  const { data } = await apiClient.get<DashboardResponse>(
    `/dashboard/${userId}?week_start=${weekStart}`
  );
  return data;
}

export async function logMeal(userId: string, payload: LogMealRequest): Promise<any> {
  const { data } = await apiClient.post(`/dashboard/${userId}/meal`, payload);
  return data;
}

export async function logWater(userId: string, payload: LogWaterRequest): Promise<any> {
  const { data } = await apiClient.post(`/dashboard/${userId}/water`, payload);
  return data;
}

export async function logWeight(userId: string, payload: LogWeightRequest): Promise<any> {
  const { data } = await apiClient.post(`/dashboard/${userId}/weight`, payload);
  return data;
}

export async function logFeedback(userId: string, payload: LogFeedbackRequest): Promise<any> {
  const { data } = await apiClient.post(`/dashboard/${userId}/feedback`, payload);
  return data;
}

