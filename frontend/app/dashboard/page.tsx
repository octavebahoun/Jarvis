"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";

import AutomationRow from "@/components/AutomationRow";
import { listAutomations, toggleAutomation, type AutomationResponse } from "@/lib/api";

const LOAD_ERROR = "Impossible de charger les automatisations. Vérifie que le backend tourne.";

export default function DashboardPage() {
  const [automations, setAutomations] = useState<AutomationResponse[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Id en cours de bascule : le bouton concerné est désactivé le temps de l'aller-retour.
  const [togglingId, setTogglingId] = useState<string | null>(null);

  // Rechargement manuel (bouton « Rafraîchir »).
  const load = useCallback(async () => {
    try {
      const items = await listAutomations();
      setAutomations(items);
      setError(null);
    } catch {
      setError(LOAD_ERROR);
    }
  }, []);

  // Chargement initial. Écrit sous forme de promesse plutôt qu'en appelant
  // `load()` : la règle react-hooks/set-state-in-effect interdit d'invoquer
  // depuis un effet une fonction qui met l'état à jour, même de façon
  // asynchrone. Le drapeau `cancelled` évite un setState après démontage.
  useEffect(() => {
    let cancelled = false;

    listAutomations()
      .then((items) => {
        if (cancelled) return;
        setAutomations(items);
        setError(null);
      })
      .catch(() => {
        if (!cancelled) setError(LOAD_ERROR);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  async function handleToggle(automation: AutomationResponse) {
    setTogglingId(automation.id);
    try {
      const updated = await toggleAutomation(automation.id);
      // Remplacement ciblé plutôt qu'un rechargement complet : évite de faire
      // clignoter la liste entière pour un changement d'une seule ligne.
      setAutomations((prev) =>
        prev ? prev.map((item) => (item.id === updated.id ? updated : item)) : prev,
      );
    } catch {
      setError("La bascule a échoué. L'automatisation n'a pas été modifiée.");
    } finally {
      setTogglingId(null);
    }
  }

  const activeCount = automations?.filter((item) => item.active).length ?? 0;

  return (
    <div className="min-h-screen bg-linear-to-b from-zinc-950 via-zinc-900 to-black text-zinc-100">
      <div className="mx-auto w-full max-w-3xl px-6 py-8">
        <header className="mb-6 flex items-center justify-between">
          <Link href="/" className="text-sm text-zinc-400 hover:text-zinc-200">
            ← Retour
          </Link>
          <span className="text-sm tracking-wide text-zinc-300">JARVIS · Dashboard</span>
          <Link href="/chat" className="text-sm text-zinc-400 hover:text-zinc-200">
            Chat
          </Link>
        </header>

        <section>
          <div className="mb-4 flex items-baseline justify-between gap-3">
            <h1 className="text-xl font-semibold">Automatisations</h1>
            <button
              type="button"
              onClick={() => void load()}
              className="text-sm text-zinc-400 hover:text-zinc-200"
            >
              Rafraîchir
            </button>
          </div>

          {error && <p className="mb-4 text-sm text-red-400">{error}</p>}

          {automations === null && !error && (
            <p className="text-sm text-zinc-500">Chargement des automatisations...</p>
          )}

          {automations !== null && automations.length === 0 && (
            <p className="text-sm text-zinc-500">
              Aucune automatisation pour l&apos;instant. Demande-en une dans le{" "}
              <Link href="/chat" className="text-cyan-300 hover:text-cyan-200">
                chat
              </Link>{" "}
              (par exemple : « rappelle-moi de relire mes notes tous les matins à 8h »).
            </p>
          )}

          {automations !== null && automations.length > 0 && (
            <>
              <p className="mb-3 text-xs text-zinc-500">
                {activeCount} active{activeCount > 1 ? "s" : ""} sur {automations.length}
              </p>
              <div className="space-y-3">
                {automations.map((automation) => (
                  <AutomationRow
                    key={automation.id}
                    automation={automation}
                    isToggling={togglingId === automation.id}
                    onToggle={handleToggle}
                  />
                ))}
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  );
}
