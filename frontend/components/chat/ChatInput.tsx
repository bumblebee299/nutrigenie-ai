"use client";

import { useState, useRef, type FormEvent, type KeyboardEvent } from "react";
import { Send, Loader2 } from "lucide-react";
import clsx from "clsx";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  placeholder?: string;
}

const SUGGESTION_PILLS = [
  "What should I eat for breakfast?",
  "How much water should I drink daily?",
  "Best foods for weight loss?",
  "High-protein vegetarian meals?",
];

export function ChatInput({ onSend, isLoading, placeholder = "Ask a nutrition question…" }: ChatInputProps) {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function autoResize() {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }

  function handleSubmit(e?: FormEvent) {
    e?.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setText("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  return (
    <div className="border-t border-gray-800 bg-gray-950 px-4 py-3 space-y-2">
      {/* Suggestion pills — shown only when chat is empty */}
      {!isLoading && (
        <div className="flex flex-wrap gap-2">
          {SUGGESTION_PILLS.map((pill) => (
            <button
              key={pill}
              onClick={() => {
                setText(pill);
                textareaRef.current?.focus();
              }}
              className="text-xs px-3 py-1 rounded-full bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-gray-200 border border-gray-700 transition-colors"
            >
              {pill}
            </button>
          ))}
        </div>
      )}

      {/* Input row */}
      <form onSubmit={handleSubmit} className="flex items-end gap-3">
        <textarea
          ref={textareaRef}
          rows={1}
          value={text}
          onChange={(e) => {
            setText(e.target.value);
            autoResize();
          }}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isLoading}
          className="input-field resize-none overflow-hidden flex-1 py-2.5 leading-relaxed"
        />
        <button
          type="submit"
          disabled={!text.trim() || isLoading}
          className={clsx(
            "flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-colors",
            text.trim() && !isLoading
              ? "bg-brand-600 hover:bg-brand-500 text-white"
              : "bg-gray-800 text-gray-600 cursor-not-allowed"
          )}
          aria-label="Send message"
        >
          {isLoading ? (
            <Loader2 size={18} className="animate-spin" />
          ) : (
            <Send size={18} />
          )}
        </button>
      </form>
      <p className="text-xs text-gray-600 text-center">
        Shift + Enter for new line · Enter to send
      </p>
    </div>
  );
}
