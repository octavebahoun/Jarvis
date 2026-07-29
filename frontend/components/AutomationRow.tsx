"use client";

import TaskStatus from "@/components/TaskStatus";
import { describeCron, localTimeHint } from "@/lib/cron";
import type { AutomationResponse } from "@/lib/api";

function formatLastRun(isoDate: string): string {
  const date = new Date(isoDate);
  if (Number.isNaN(date.getTime())) return isoDate;

  return date.toLocaleString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

interface AutomationRowProps {
  automation: AutomationResponse;
  /** `true` pendant l'aller-retour réseau du toggle : évite les double-clics. */
  isToggling: boolean;
  onToggle: (automation: AutomationResponse) => void;
}

export default function AutomationRow({ automation, isToggling, onToggle }: AutomationRowProps) {
  const localHint = localTimeHint(automation.schedule);

  return (
    <article
      className={`rounded-2xl border p-4 transition ${
        automation.active
          ? "border-zinc-700/70 bg-zinc-900/70"
          : "border-zinc-800 bg-zinc-900/30 opacity-60"
      }`}
    >
      <div className="mb-2 flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="truncate text-sm font-medium text-zinc-100">{automation.name}</h3>
          <p className="mt-1 text-sm text-zinc-400">{automation.task}</p>
        </div>

        <button
          type="button"
          onClick={() => onToggle(automation)}
          disabled={isToggling}
          aria-pressed={automation.active}
          className={`shrink-0 rounded-full border px-3 py-1 text-xs font-medium transition disabled:opacity-40 ${
            automation.active
              ? "border-emerald-400/40 bg-emerald-400/20 text-emerald-300 hover:bg-emerald-400/30"
              : "border-zinc-600 bg-zinc-700/40 text-zinc-300 hover:bg-zinc-700/60"
          }`}
        >
          {automation.active ? "Active" : "Inactive"}
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-zinc-500">
        <span className="text-zinc-400">{describeCron(automation.schedule)}</span>
        {localHint && <span>≈ {localHint}</span>}
        <span className="font-mono">{automation.schedule}</span>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-zinc-500">
        {automation.last_run_status ? (
          <>
            <TaskStatus status={automation.last_run_status} />
            {automation.last_run_at && <span>le {formatLastRun(automation.last_run_at)}</span>}
          </>
        ) : (
          <span>Jamais exécutée</span>
        )}
      </div>
    </article>
  );
}
