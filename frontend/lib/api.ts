const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
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
    throw new Error(`Jarvis API error ${res.status}: ${await res.text()}`);
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
