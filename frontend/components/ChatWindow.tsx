"use client";

import { useEffect, useRef } from "react";

import type { ChatMessage } from "@/lib/api";

function ThinkingBubble() {
  return (
    <div className="flex w-fit items-center gap-1 self-start rounded-2xl border border-zinc-700/70 bg-zinc-900/70 px-4 py-3">
      <span className="typing-dot h-1.5 w-1.5 rounded-full bg-zinc-400" />
      <span className="typing-dot h-1.5 w-1.5 rounded-full bg-zinc-400" style={{ animationDelay: "0.15s" }} />
      <span className="typing-dot h-1.5 w-1.5 rounded-full bg-zinc-400" style={{ animationDelay: "0.3s" }} />
    </div>
  );
}

export default function ChatWindow({
  messages,
  isThinking = false,
}: {
  messages: ChatMessage[];
  isThinking?: boolean;
}) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  if (messages.length === 0 && !isThinking) {
    return (
      <div className="flex flex-1 items-center justify-center text-sm text-zinc-500">
        Dis bonjour à Jarvis pour démarrer la conversation.
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col gap-3 overflow-y-auto px-1 py-4">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
            message.role === "user"
              ? "self-end bg-cyan-400 text-zinc-950"
              : "self-start border border-zinc-700/70 bg-zinc-900/70 text-zinc-100"
          }`}
        >
          {message.content}
        </div>
      ))}
      {isThinking && <ThinkingBubble />}
      <div ref={bottomRef} />
    </div>
  );
}
