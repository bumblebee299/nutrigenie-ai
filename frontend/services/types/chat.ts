/**
 * Shared TypeScript types for AI Chat.
 * These mirror the backend Pydantic models exactly.
 */

export type MessageRole = "user" | "assistant" | "system";

export interface ChatMessage {
  role: MessageRole;
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  message: string;
  history: ChatMessage[];
  user_id: string;
}

export interface ChatResponse {
  reply: string;
  explanation: string;
  sources: string[];
  timestamp: string;
}

export interface FeedbackRequest {
  message_id: string;
  helpful: boolean;
  comment?: string;
  user_id: string;
}

/** Extended message type used only on the frontend for UI state. */
export interface UIMessage extends ChatMessage {
  id: string;
  explanation?: string;
  sources?: string[];
  isLoading?: boolean;
}
