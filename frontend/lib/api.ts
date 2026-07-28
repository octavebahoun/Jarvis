const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  ts: number;
}

/** Erreur HTTP renvoyée par l'API Jarvis (par opposition à une erreur réseau :
 * backend injoignable, qui lève une TypeError native de `fetch`, pas une ApiError). */
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export interface ProfileResponse {
  username: string;
  tech_stack: string[];
  preferences: Record<string, unknown>;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    throw new ApiError(res.status, await res.text().catch(() => res.statusText));
  }

  return res.json() as Promise<T>;
}

export function sendChatMessage(message: string, sessionId: string) {
  return request<{ reply: string; session_id: string }>("/chat", {
    method: "POST",
    body: JSON.stringify({ message, session_id: sessionId }),
  });
}

export function getProfile() {
  return request<ProfileResponse>("/profile");
}

export interface FactItem {
  id: string;
  content: string;
  created_at: string;
}

export async function getLongTermMemory(): Promise<FactItem[]> {
  const { items } = await request<{ items: FactItem[] }>("/memory?type=long_term");
  return items;
}

interface ShortTermItem {
  role: "user" | "assistant";
  content: string;
  ts: number;
}

export async function getShortTermHistory(sessionId: string): Promise<ChatMessage[]> {
  const { items } = await request<{ items: ShortTermItem[] }>(
    `/memory?type=short_term&session_id=${encodeURIComponent(sessionId)}`,
  );

  return items.map((item) => ({
    role: item.role,
    content: item.content,
    ts: item.ts * 1000,
  }));
}

// Doit rester identique à agent.controller.STREAM_ERROR_MARKER côté backend.
const STREAM_ERROR_MARKER = "\n\n<<JARVIS_STREAM_ERROR>>";

export async function streamChatMessage(
  message: string,
  sessionId: string,
  onChunk: (textSoFar: string) => void,
): Promise<{ reply: string; failed: boolean }> {
  const res = await fetch(`${API_URL}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (!res.ok || !res.body) {
    throw new ApiError(res.status, await res.text().catch(() => res.statusText));
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let accumulated = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    accumulated += decoder.decode(value, { stream: true });
    onChunk(accumulated.replace(STREAM_ERROR_MARKER, ""));
  }

  const failed = accumulated.includes(STREAM_ERROR_MARKER);
  return { reply: accumulated.replace(STREAM_ERROR_MARKER, "").trim(), failed };
}
