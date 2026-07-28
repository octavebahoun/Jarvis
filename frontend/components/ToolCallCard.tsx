import TaskStatus from "@/components/TaskStatus";
import type { PlanStepResponse } from "@/lib/api";

export default function ToolCallCard({ step }: { step: PlanStepResponse }) {
  return (
    <div className="rounded-xl border border-zinc-700/70 bg-zinc-900/60 p-3">
      <div className="mb-1 flex items-center justify-between gap-2">
        <span className="font-mono text-xs text-cyan-300">{step.tool}</span>
        <TaskStatus status={step.status} />
      </div>
      <p className="text-sm text-zinc-200">{step.description}</p>
      {step.result && (
        <pre className="mt-2 max-h-40 overflow-auto rounded-lg bg-black/40 p-2 text-xs whitespace-pre-wrap text-zinc-300">
          {step.result}
        </pre>
      )}
      {step.error && (
        <p className="mt-2 rounded-lg bg-red-950/40 p-2 text-xs text-red-300">{step.error}</p>
      )}
    </div>
  );
}
