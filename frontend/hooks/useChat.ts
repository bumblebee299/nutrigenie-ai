"use client";

import { useState, useCallback, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import toast from "react-hot-toast";
import type { UIMessage, ChatMessage } from "@/services/types/chat";
import { sendMessage, submitFeedback } from "@/services/chatService";

interface UseChatReturn {
  messages: UIMessage[];
  isLoading: boolean;
  send: (text: string, userId: string) => Promise<void>;
  giveFeedback: (messageId: string, helpful: boolean, userId: string) => Promise<void>;
  clearHistory: () => void;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<UIMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  // Ref so send() always reads the latest messages without stale closure
  const messagesRef = useRef<UIMessage[]>([]);

  function syncMessages(updated: UIMessage[]) {
    messagesRef.current = updated;
    setMessages(updated);
  }

  const send = useCallback(async (text: string, userId: string): Promise<void> => {
    const userMsg: UIMessage = {
      id: uuidv4(),
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };

    // Optimistic placeholder for the assistant reply
    const placeholderMsg: UIMessage = {
      id: uuidv4(),
      role: "assistant",
      content: "",
      isLoading: true,
    };

    const withUser = [...messagesRef.current, userMsg, placeholderMsg];
    syncMessages(withUser);
    setIsLoading(true);

    try {
      // Build the history to send (exclude the placeholder)
      const history: ChatMessage[] = messagesRef.current
        .filter((m) => !m.isLoading)
        .map(({ role, content, timestamp }) => ({ role, content, timestamp }));

      const response = await sendMessage({ message: text, history, user_id: userId });

      const assistantMsg: UIMessage = {
        id: placeholderMsg.id,
        role: "assistant",
        content: response.reply,
        explanation: response.explanation,
        sources: response.sources,
        timestamp: response.timestamp,
        isLoading: false,
      };

      syncMessages([...messagesRef.current.filter((m) => m.id !== placeholderMsg.id), assistantMsg]);
    } catch (err) {
      // Remove placeholder and show error toast
      syncMessages(messagesRef.current.filter((m) => m.id !== placeholderMsg.id));
      toast.error(err instanceof Error ? err.message : "Failed to get a response.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const giveFeedback = useCallback(
    async (messageId: string, helpful: boolean, userId: string): Promise<void> => {
      try {
        await submitFeedback({ message_id: messageId, helpful, user_id: userId });
        toast.success(helpful ? "Thanks for the positive feedback!" : "Noted — we will improve.");
      } catch {
        toast.error("Could not save your feedback.");
      }
    },
    []
  );

  const clearHistory = useCallback(() => syncMessages([]), []);

  return { messages, isLoading, send, giveFeedback, clearHistory };
}
