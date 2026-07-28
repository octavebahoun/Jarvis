"use client";

import { useState } from "react";
import Link from "next/link";

import ChatWindow from "@/components/ChatWindow";
import InputBar from "@/components/InputBar";
import { sendChatMessage, type ChatMessage } from "@/lib/api";

export default function ChatPage() {
  const [sessionId] = useState(() => crypto.randomUUID());
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSend(message: string) {
    setError(null);
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setIsSending(true);

    try {
      const { reply } = await sendChatMessage(message, sessionId);
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch {
      setError("Jarvis est indisponible. Vérifie que le backend tourne bien.");
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-linear-to-b from-zinc-950 via-zinc-900 to-black text-zinc-100">
      <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col px-6 py-8">
        <header className="mb-4 flex items-center justify-between">
          <Link href="/" className="text-sm text-zinc-400 hover:text-zinc-200">
            ← Retour
          </Link>
          <span className="text-sm tracking-wide text-zinc-300">JARVIS · Chat</span>
        </header>

        <ChatWindow messages={messages} />

        {error && <p className="mb-2 text-sm text-red-400">{error}</p>}

        <InputBar onSend={handleSend} disabled={isSending} />
      </div>
    </div>
  );
}
