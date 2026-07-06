"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bot, User, ChevronDown, ChevronUp, ThumbsUp, ThumbsDown } from "lucide-react";
import clsx from "clsx";
import type { UIMessage } from "@/services/types/chat";

interface ChatMessageProps {
  message: UIMessage;
  onFeedback: (messageId: string, helpful: boolean) => void;
}

function TypingIndicator() {
  return (
    <div className="flex gap-1 items-center px-1 py-2">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="w-2 h-2 rounded-full bg-brand-400 animate-bounce"
          style={{ animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </div>
  );
}

export function ChatMessageBubble({ message, onFeedback }: ChatMessageProps) {
  const isUser = message.role === "user";
  const [showExplanation, setShowExplanation] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState<boolean | null>(null);

  function handleFeedback(helpful: boolean) {
    if (feedbackGiven !== null || !message.id) return;
    setFeedbackGiven(helpful);
    onFeedback(message.id, helpful);
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={clsx("flex gap-3 max-w-3xl w-full", isUser ? "ml-auto flex-row-reverse" : "")}
    >
      {/* Avatar */}
      <div
        className={clsx(
          "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
          isUser ? "bg-brand-600" : "bg-gray-700"
        )}
      >
        {isUser ? (
          <User size={16} className="text-white" />
        ) : (
          <Bot size={16} className="text-brand-400" />
        )}
      </div>

      {/* Bubble */}
      <div className={clsx("flex flex-col gap-2 max-w-[85%]", isUser ? "items-end" : "items-start")}>
        <div
          className={clsx(
            "rounded-2xl px-4 py-3 text-sm leading-relaxed",
            isUser
              ? "bg-brand-600 text-white rounded-tr-sm"
              : "bg-gray-800 text-gray-100 rounded-tl-sm border border-gray-700"
          )}
        >
          {message.isLoading ? <TypingIndicator /> : <p className="whitespace-pre-wrap">{message.content}</p>}
        </div>

        {/* Explanation + feedback — assistant messages only */}
        {!isUser && !message.isLoading && (
          <div className="w-full space-y-1">
            {/* Collapsible explanation */}
            {message.explanation && (
              <button
                onClick={() => setShowExplanation((v) => !v)}
                className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-300 transition-colors"
              >
                {showExplanation ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                Why this recommendation?
              </button>
            )}
            <AnimatePresence>
              {showExplanation && message.explanation && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="text-xs text-gray-400 bg-gray-900 rounded-lg px-3 py-2 border border-gray-800"
                >
                  {message.explanation}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Feedback buttons */}
            <div className="flex items-center gap-2 pt-0.5">
              <span className="text-xs text-gray-600">Helpful?</span>
              <button
                onClick={() => handleFeedback(true)}
                disabled={feedbackGiven !== null}
                className={clsx(
                  "p-1 rounded transition-colors",
                  feedbackGiven === true
                    ? "text-brand-400"
                    : "text-gray-600 hover:text-brand-400 disabled:opacity-40"
                )}
                aria-label="Mark as helpful"
              >
                <ThumbsUp size={13} />
              </button>
              <button
                onClick={() => handleFeedback(false)}
                disabled={feedbackGiven !== null}
                className={clsx(
                  "p-1 rounded transition-colors",
                  feedbackGiven === false
                    ? "text-red-400"
                    : "text-gray-600 hover:text-red-400 disabled:opacity-40"
                )}
                aria-label="Mark as not helpful"
              >
                <ThumbsDown size={13} />
              </button>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
