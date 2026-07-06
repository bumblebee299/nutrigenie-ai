"use client";

import { useState, useCallback } from "react";
import toast from "react-hot-toast";
import type { ImageAnalysisResponse } from "@/services/types/image_analysis";
import { analyseImage } from "@/services/imageAnalysisService";

interface UseImageAnalysisReturn {
  result: ImageAnalysisResponse | null;
  isLoading: boolean;
  analyse: (file: File, userId: string) => Promise<void>;
  reset: () => void;
}

export function useImageAnalysis(): UseImageAnalysisReturn {
  const [result, setResult] = useState<ImageAnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const analyse = useCallback(async (file: File, userId: string): Promise<void> => {
    setIsLoading(true);
    try {
      const analysis = await analyseImage(file, userId);
      setResult(analysis);
      toast.success("Image analysed successfully!");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Image analysis failed.");
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => setResult(null), []);

  return { result, isLoading, analyse, reset };
}
