/**
 * Image Analysis API service — calls to POST /image-analysis/.
 */
import type { ImageAnalysisResponse } from "@/services/types/image_analysis";
import apiClient from "@/services/apiClient";

export async function analyseImage(
  imageFile: File,
  userId: string
): Promise<ImageAnalysisResponse> {
  const form = new FormData();
  form.append("user_id", userId);
  form.append("image", imageFile);

  const { data } = await apiClient.post<ImageAnalysisResponse>("/image-analysis/", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}
