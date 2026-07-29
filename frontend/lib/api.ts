const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

export type ChatMessage =
  | { role: "user" | "assistant"; content: string; ts: number }
  | { role: "plan"; planId: string; ts: number }
  | { role: "automation"; automationId: string; ts: number };

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
// Doit rester identique à agent.controller.PLAN_MARKER côté backend.
const PLAN_MARKER = "\n\n<<JARVIS_PLAN>>";
// Doit rester identique à agent.controller.AUTOMATION_MARKER côté backend.
const AUTOMATION_MARKER = "\n\n<<JARVIS_AUTOMATION>>";

export type ChatStreamResult =
  | { type: "reply"; reply: string; failed: boolean }
  | { type: "plan"; planId: string }
  | { type: "automation"; automationId: string };

export async function streamChatMessage(
  message: string,
  sessionId: string,
  onChunk: (textSoFar: string) => void,
): Promise<ChatStreamResult> {
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
    // Un plan/une automatisation tient dans un unique chunk : tant qu'on ne
    // sait pas encore ce que c'est, mieux vaut ne rien afficher que de
    // flasher le marqueur brut.
    if (!accumulated.startsWith(PLAN_MARKER) && !accumulated.startsWith(AUTOMATION_MARKER)) {
      onChunk(accumulated.replace(STREAM_ERROR_MARKER, ""));
    }
  }

  if (accumulated.startsWith(PLAN_MARKER)) {
    return { type: "plan", planId: accumulated.slice(PLAN_MARKER.length).trim() };
  }
  if (accumulated.startsWith(AUTOMATION_MARKER)) {
    return { type: "automation", automationId: accumulated.slice(AUTOMATION_MARKER.length).trim() };
  }

  const failed = accumulated.includes(STREAM_ERROR_MARKER);
  return { type: "reply", reply: accumulated.replace(STREAM_ERROR_MARKER, "").trim(), failed };
}

export interface PlanStepResponse {
  id: string;
  tool: string;
  description: string;
  status: string;
  result: string | null;
  error: string | null;
}

export interface PlanResponse {
  id: string;
  session_id: string;
  goal: string;
  status: string;
  summary: string | null;
  steps: PlanStepResponse[];
}

export function getTask(planId: string) {
  return request<PlanResponse>(`/tasks/${encodeURIComponent(planId)}`);
}

export function approveTask(planId: string) {
  return request<PlanResponse>(`/tasks/${encodeURIComponent(planId)}/approve`, { method: "POST" });
}

export function getTaskWebSocketUrl(planId: string): string {
  return `${API_URL.replace(/^http/, "ws")}/ws/tasks/${encodeURIComponent(planId)}`;
}

export interface AutomationResponse {
  id: string;
  name: string;
  schedule: string;
  task: string;
  active: boolean;
  last_run_at: string | null;
  last_run_status: string | null;
  last_run_plan_id: string | null;
}

export function getAutomation(automationId: string) {
  return request<AutomationResponse>(`/automations/${encodeURIComponent(automationId)}`);
}
