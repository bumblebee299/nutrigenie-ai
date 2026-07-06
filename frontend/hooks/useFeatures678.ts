"use client";

import { useState, useCallback } from "react";
import toast from "react-hot-toast";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
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
import {
  getFoodSwaps,
  analyseLabel,
  getWeeklyDashboard,
  logMeal,
  logWater,
  logWeight,
  logFeedback,
} from "@/services/tasks678Service";

// ── useFood Swap ──────────────────────────────────────────────────────────

export function useFoodSwap() {
  const [result, setResult] = useState<FoodSwapResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const getSwaps = useCallback(async (payload: FoodSwapRequest) => {
    setIsLoading(true);
    try {
      const data = await getFoodSwaps(payload);
      setResult(data);
      toast.success("Healthier swaps found!");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to get swap suggestions.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { result, isLoading, getSwaps, reset: () => setResult(null) };
}

// ── useLabel Analysis ─────────────────────────────────────────────────────

export function useLabelAnalysis() {
  const [result, setResult] = useState<LabelAnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const analyse = useCallback(async (file: File, userId: string) => {
    setIsLoading(true);
    try {
      const data = await analyseLabel(file, userId);
      setResult(data);
      toast.success("Label analysed successfully!");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Label analysis failed.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { result, isLoading, analyse, reset: () => setResult(null) };
}

// ── useDashboard ──────────────────────────────────────────────────────────

export function useDashboard(userId: string, weekStart: string) {
  return useQuery<DashboardResponse, Error>({
    queryKey: ["dashboard", userId, weekStart],
    queryFn: () => getWeeklyDashboard(userId, weekStart),
    enabled: Boolean(userId && weekStart),
    staleTime: 5 * 60 * 1000,
  });
}

export function useLogMeal(userId: string, weekStart: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: LogMealRequest) => logMeal(userId, payload),
    onSuccess: () => {
      toast.success("Meal logged successfully!");
      queryClient.invalidateQueries({ queryKey: ["dashboard", userId, weekStart] });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to log meal.");
    },
  });
}

export function useLogWater(userId: string, weekStart: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: LogWaterRequest) => logWater(userId, payload),
    onSuccess: () => {
      toast.success("Water logged successfully!");
      queryClient.invalidateQueries({ queryKey: ["dashboard", userId, weekStart] });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to log water.");
    },
  });
}

export function useLogWeight(userId: string, weekStart: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: LogWeightRequest) => logWeight(userId, payload),
    onSuccess: () => {
      toast.success("Weight logged successfully!");
      queryClient.invalidateQueries({ queryKey: ["dashboard", userId, weekStart] });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to log weight.");
    },
  });
}

export function useLogFeedback(userId: string, weekStart: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: LogFeedbackRequest) => logFeedback(userId, payload),
    onSuccess: () => {
      toast.success("Daily feedback submitted!");
      queryClient.invalidateQueries({ queryKey: ["dashboard", userId, weekStart] });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to submit feedback.");
    },
  });
}

