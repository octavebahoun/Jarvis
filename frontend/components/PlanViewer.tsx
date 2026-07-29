"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

import TaskStatus from "@/components/TaskStatus";
import ToolCallCard from "@/components/ToolCallCard";
import { approveTask, getTask, getTaskWebSocketUrl, type PlanResponse } from "@/lib/api";

const TERMINAL_STATUSES = new Set(["done", "failed"]);

export default function PlanViewer({ planId }: { planId: string }) {
  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isApproving, setIsApproving] = useState(false);
  // true dès que le plan est approuvé (par cette session ou une précédente) :
  // stable une fois passé à true, pour ne pas rouvrir le WebSocket à chaque
  // changement de statut reçu (sinon l'effet ci-dessous se relancerait en boucle).
  const [hasStarted, setHasStarted] = useState(false);

  useEffect(() => {
    let cancelled = false;

    getTask(planId)
      .then((data) => {
        if (cancelled) return;
        setPlan(data);
        if (data.status !== "pending") setHasStarted(true);
      })
      .catch(() => {
        if (!cancelled) setError("Impossible de charger ce plan.");
      });

    return () => {
      cancelled = true;
    };
  }, [planId]);

  useEffect(() => {
    if (!hasStarted) return;

    const socket = new WebSocket(getTaskWebSocketUrl(planId));

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.error) return;

      setPlan(data);
      if (TERMINAL_STATUSES.has(data.status)) socket.close();
    };

    return () => socket.close();
  }, [planId, hasStarted]);

  async function handleApprove() {
    setIsApproving(true);
    setError(null);

    try {
      const updated = await approveTask(planId);
      setPlan(updated);
      setHasStarted(true);
    } catch {
      setError("Impossible d'approuver ce plan.");
    } finally {
      setIsApproving(false);
    }
  }

  if (error) {
    return <p className="text-sm text-red-400">{error}</p>;
  }

  if (!plan) {
    return <p className="text-sm text-zinc-500">Chargement du plan...</p>;
  }

  return (
    <div className="w-full max-w-[80%] self-start rounded-2xl border border-zinc-700/70 bg-zinc-900/70 p-4">
      <div className="mb-3 flex items-center justify-between gap-2">
        <p className="text-sm font-medium text-zinc-100">{plan.goal}</p>
        <TaskStatus status={plan.status} />
      </div>

      <div className="space-y-2">
        {plan.steps.map((step) => (
          <ToolCallCard key={step.id} step={step} />
        ))}
      </div>

      {plan.summary && (
        <div className="prose prose-invert prose-sm mt-3 max-w-none border-t border-zinc-700/70 pt-3 prose-p:my-1 prose-p:first:mt-0 prose-p:last:mb-0">
          <ReactMarkdown>{plan.summary}</ReactMarkdown>
        </div>
      )}

      {plan.status === "pending" && (
        <button
          onClick={handleApprove}
          disabled={isApproving}
          className="mt-3 rounded-full bg-cyan-400 px-4 py-1.5 text-sm font-semibold text-zinc-950 hover:bg-cyan-300 disabled:opacity-50"
        >
          {isApproving ? "Approbation..." : "Approuver l'exécution"}
        </button>
      )}
    </div>
  );
}
