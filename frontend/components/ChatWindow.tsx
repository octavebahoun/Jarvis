"use client";

import { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";

import PlanViewer from "@/components/PlanViewer";
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

function formatTime(ts: number): string {
  return new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function ChatWindow({
  messages,
  streamingReply = "",
  isSending = false,
}: {
  messages: ChatMessage[];
  streamingReply?: string;
  isSending?: boolean;
}) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const showThinking = isSending && streamingReply.length === 0;
  const showStreaming = streamingReply.length > 0;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, showThinking, showStreaming]);

  if (messages.length === 0 && !showThinking && !showStreaming) {
    return (
      <div className="flex flex-1 items-center justify-center text-sm text-zinc-500">
        Dis bonjour à Jarvis pour démarrer la conversation.
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col gap-3 overflow-y-auto px-1 py-4">
      {messages.map((message, index) => {
        if (message.role === "plan") {
          return <PlanViewer key={index} planId={message.planId} />;
        }

        return (
          <div
            key={index}
            className={`flex max-w-[80%] flex-col ${message.role === "user" ? "self-end items-end" : "self-start items-start"}`}
          >
            <div
              className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                message.role === "user"
                  ? "bg-cyan-400 text-zinc-950"
                  : "border border-zinc-700/70 bg-zinc-900/70 text-zinc-100"
              }`}
            >
              {message.role === "assistant" ? (
                <div className="prose prose-invert prose-sm max-w-none prose-p:my-1 prose-p:first:mt-0 prose-p:last:mb-0">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
              ) : (
                message.content
              )}
            </div>
            <span className="mt-1 px-1 text-xs text-zinc-500">{formatTime(message.ts)}</span>
          </div>
        );
      })}
      {showStreaming && (
        <div className="max-w-[80%] self-start rounded-2xl border border-zinc-700/70 bg-zinc-900/70 px-4 py-2.5 text-sm leading-relaxed text-zinc-100">
          <div className="prose prose-invert prose-sm max-w-none prose-p:my-1 prose-p:first:mt-0 prose-p:last:mb-0">
            <ReactMarkdown>{streamingReply}</ReactMarkdown>
          </div>
        </div>
      )}
      {showThinking && <ThinkingBubble />}
      <div ref={bottomRef} />
    </div>
  );
}
