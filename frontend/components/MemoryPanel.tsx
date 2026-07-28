"use client";

import { useEffect, useState } from "react";

import { getLongTermMemory, getProfile, type FactItem, type ProfileResponse } from "@/lib/api";

export default function MemoryPanel() {
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [facts, setFacts] = useState<FactItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    Promise.all([getProfile(), getLongTermMemory()])
      .then(([profileResponse, factItems]) => {
        setProfile(profileResponse);
        setFacts(factItems);
      })
      .catch(() => setError("Impossible de charger le profil et la mémoire."))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="mb-4 rounded-2xl border border-zinc-700/70 bg-zinc-900/60 p-4 text-sm">
      {isLoading && <p className="text-zinc-500">Chargement...</p>}
      {error && <p className="text-red-400">{error}</p>}

      {profile && (
        <div className="mb-3">
          <p className="mb-1 text-xs tracking-wide text-zinc-500 uppercase">Profil</p>
          <p className="text-zinc-200">{profile.username}</p>
          {profile.tech_stack.length > 0 && (
            <div className="mt-1 flex flex-wrap gap-1">
              {profile.tech_stack.map((tech) => (
                <span key={tech} className="rounded-full bg-zinc-800 px-2 py-0.5 text-xs text-zinc-300">
                  {tech}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {!isLoading && !error && (
        <div>
          <p className="mb-1 text-xs tracking-wide text-zinc-500 uppercase">Mémoire long terme</p>
          {facts.length === 0 ? (
            <p className="text-zinc-500">Aucun fait enregistré pour le moment.</p>
          ) : (
            <ul className="space-y-1">
              {facts.map((fact) => (
                <li key={fact.id} className="text-zinc-300">
                  {fact.content}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
