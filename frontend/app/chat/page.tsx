"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import ChatWindow from "@/components/ChatWindow";
import InputBar from "@/components/InputBar";
import MemoryPanel from "@/components/MemoryPanel";
import { ApiError, getShortTermHistory, streamChatMessage, type ChatMessage } from "@/lib/api";

const SESSION_STORAGE_KEY = "jarvis:session_id";

function describeSendError(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.status === 502) return "Le modèle IA (LLM) est indisponible côté serveur.";
    if (err.status === 422) return "Message invalide.";
    return `Erreur serveur inattendue (code ${err.status}).`;
  }

  return "Impossible de joindre Jarvis. Vérifie que le backend tourne (docker-compose up).";
}

function loadOrCreateSessionId(): string {
  const existing = localStorage.getItem(SESSION_STORAGE_KEY);
  if (existing) return existing;

  const fresh = crypto.randomUUID();
  localStorage.setItem(SESSION_STORAGE_KEY, fresh);
  return fresh;
}

export default function ChatPage() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [streamingReply, setStreamingReply] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isMemoryPanelOpen, setIsMemoryPanelOpen] = useState(false);

  // La session est résolue côté client uniquement (localStorage n'existe pas
  // pendant le rendu serveur), d'où l'aller via useEffect plutôt qu'un état initial.
  useEffect(() => {
    setSessionId(loadOrCreateSessionId());
  }, []);

  useEffect(() => {
    if (!sessionId) return;

    let cancelled = false;
    getShortTermHistory(sessionId)
      .then((history) => {
        if (!cancelled) setMessages(history);
      })
      .catch(() => {
        // Pas d'historique disponible (backend éteint, session expirée...) : on démarre à vide.
      })
      .finally(() => {
        if (!cancelled) setIsLoadingHistory(false);
      });

    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  function startNewConversation() {
    const fresh = crypto.randomUUID();
    localStorage.setItem(SESSION_STORAGE_KEY, fresh);
    setSessionId(fresh);
    setMessages([]);
    setError(null);
  }

  async function handleSend(message: string) {
    if (!sessionId) return;

    setError(null);
    setMessages((prev) => [...prev, { role: "user", content: message, ts: Date.now() }]);
    setIsSending(true);
    setStreamingReply("");

    try {
      const { reply, failed } = await streamChatMessage(message, sessionId, setStreamingReply);

      if (reply) {
        setMessages((prev) => [...prev, { role: "assistant", content: reply, ts: Date.now() }]);
      }
      if (failed) {
        setError("Le LLM a rencontré une erreur pendant la génération de la réponse.");
      }
    } catch (err) {
      setError(describeSendError(err));
    } finally {
      setIsSending(false);
      setStreamingReply("");
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
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsMemoryPanelOpen((open) => !open)}
              className="text-sm text-zinc-400 hover:text-zinc-200"
            >
              Profil & mémoire
            </button>
            <button
              onClick={startNewConversation}
              className="text-sm text-zinc-400 hover:text-zinc-200"
            >
              Nouvelle conversation
            </button>
          </div>
        </header>

        {isMemoryPanelOpen && <MemoryPanel />}

        {isLoadingHistory ? (
          <div className="flex flex-1 items-center justify-center text-sm text-zinc-500">
            Chargement de la conversation...
          </div>
        ) : (
          <ChatWindow messages={messages} streamingReply={streamingReply} isSending={isSending} />
        )}

        {error && <p className="mb-2 text-sm text-red-400">{error}</p>}

        <InputBar onSend={handleSend} disabled={isSending || !sessionId} />
      </div>
    </div>
  );
}
