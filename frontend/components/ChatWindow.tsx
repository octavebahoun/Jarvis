"use client";

import { useEffect, useRef } from "react";

import type { ChatMessage } from "@/lib/api";

export default function ChatWindow({ messages }: { messages: ChatMessage[] }) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
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
      <div ref={bottomRef} />
    </div>
  );
}
