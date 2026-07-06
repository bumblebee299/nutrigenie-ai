/**
 * Chat API service — calls to /chat/* endpoints.
 */
import type { ChatRequest, ChatResponse, FeedbackRequest } from "@/services/types/chat";
import apiClient from "@/services/apiClient";

export async function sendMessage(payload: ChatRequest): Promise<ChatResponse> {
  const { data } = await apiClient.post<ChatResponse>("/chat/", payload);
  return data;
}

export async function submitFeedback(payload: FeedbackRequest): Promise<void> {
  await apiClient.post("/chat/feedback", payload);
}
