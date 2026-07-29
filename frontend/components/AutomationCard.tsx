"use client";

import { useEffect, useState } from "react";

import TaskStatus from "@/components/TaskStatus";
import { getAutomation, type AutomationResponse } from "@/lib/api";

export default function AutomationCard({ automationId }: { automationId: string }) {
  const [automation, setAutomation] = useState<AutomationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    getAutomation(automationId)
      .then((data) => {
        if (!cancelled) setAutomation(data);
      })
      .catch(() => {
        if (!cancelled) setError("Impossible de charger cette automatisation.");
      });

    return () => {
      cancelled = true;
    };
  }, [automationId]);

  if (error) {
    return <p className="text-sm text-red-400">{error}</p>;
  }

  if (!automation) {
    return <p className="text-sm text-zinc-500">Chargement de l&apos;automatisation...</p>;
  }

  return (
    <div className="w-full max-w-[80%] self-start rounded-2xl border border-zinc-700/70 bg-zinc-900/70 p-4">
      <div className="mb-2 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="shrink-0 rounded-full border border-cyan-400/40 bg-cyan-400/20 px-2.5 py-0.5 text-xs font-medium text-cyan-300">
            Programmé
          </span>
          <p className="text-sm font-medium text-zinc-100">{automation.name}</p>
        </div>
        {automation.last_run_status && <TaskStatus status={automation.last_run_status} />}
      </div>

      <p className="text-sm text-zinc-400">{automation.task}</p>
      <p className="mt-2 font-mono text-xs text-zinc-500">{automation.schedule} (UTC)</p>

      {!automation.active && <p className="mt-2 text-xs text-zinc-500">Désactivée</p>}
    </div>
  );
}
