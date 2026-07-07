"use client";

import { useEffect, useRef } from "react";
import { Bot, Trash2 } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { useChat } from "@/hooks/useChat";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { ChatMessageBubble } from "@/components/chat/ChatMessageBubble";
import { ChatInput } from "@/components/chat/ChatInput";

function WelcomeBanner() {
  return (
    <div className="flex flex-col items-center justify-center flex-1 gap-4 p-8 text-center">
      <div className="w-16 h-16 rounded-2xl bg-gray-800 border border-gray-700 flex items-center justify-center">
        <Bot size={32} className="text-brand-400" />
      </div>
      <div>
        <h2 className="text-2xl font-bold text-white">NutriGenie AI</h2>
        <p className="text-gray-400 mt-1 max-w-sm">
          Ask me anything about nutrition, meal planning, or healthy eating habits.
        </p>
      </div>
    </div>
  );
}

function ChatPageContent() {
  const { user } = useAuth();
  const { messages, isLoading, send, giveFeedback, clearHistory } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleSend(text: string) {
    if (!user) return;
    send(text, user.id);
  }

  function handleFeedback(messageId: string, helpful: boolean) {
    if (!user) return;
    giveFeedback(messageId, helpful, user.id);
  }

  return (
    <div className="flex flex-col h-[calc(100vh-3.5rem)] md:h-screen bg-gray-950">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-gray-800 bg-gray-950">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gray-800 border border-gray-700 flex items-center justify-center">
            <Bot size={18} className="text-brand-400" />
          </div>
          <div>
            <h1 className="font-semibold text-white text-sm">NutriGenie AI</h1>
            <p className="text-xs text-gray-500">Powered by IBM Granite</p>
          </div>
        </div>
        {messages.length > 0 && (
          <button
            onClick={clearHistory}
            className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-red-400 transition-colors px-2 py-1 rounded"
          >
            <Trash2 size={13} />
            Clear
          </button>
        )}
      </header>

      {/* Message list */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
        {messages.length === 0 ? (
          <WelcomeBanner />
        ) : (
          messages.map((msg) => (
            <ChatMessageBubble
              key={msg.id}
              message={msg}
              onFeedback={handleFeedback}
            />
          ))
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={handleSend} isLoading={isLoading} />
    </div>
  );
}

export default function ChatPage() {
  return (
    <ProtectedRoute>
      <ChatPageContent />
    </ProtectedRoute>
  );
}


