const STATUS_LABELS: Record<string, string> = {
  pending: "En attente de validation",
  approved: "Approuvé",
  running: "En cours...",
  done: "Terminé",
  failed: "Échoué",
};

const STATUS_STYLES: Record<string, string> = {
  pending: "bg-amber-400/20 text-amber-300 border-amber-400/40",
  approved: "bg-cyan-400/20 text-cyan-300 border-cyan-400/40",
  running: "bg-cyan-400/20 text-cyan-300 border-cyan-400/40",
  done: "bg-emerald-400/20 text-emerald-300 border-emerald-400/40",
  failed: "bg-red-400/20 text-red-300 border-red-400/40",
};

export default function TaskStatus({ status }: { status: string }) {
  const style = STATUS_STYLES[status] ?? "border-zinc-600 bg-zinc-700/40 text-zinc-300";

  return (
    <span className={`shrink-0 rounded-full border px-2.5 py-0.5 text-xs font-medium ${style}`}>
      {STATUS_LABELS[status] ?? status}
    </span>
  );
}
