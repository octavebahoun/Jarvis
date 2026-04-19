function NeuralFace() {
  const baseNodes = [
    { x: 110, y: 80 },
    { x: 160, y: 60 },
    { x: 210, y: 80 },
    { x: 125, y: 95 },
    { x: 195, y: 95 },
    { x: 90, y: 140 },
    { x: 115, y: 135 },
    { x: 140, y: 130 },
    { x: 165, y: 128 },
    { x: 190, y: 130 },
    { x: 215, y: 135 },
    { x: 230, y: 145 },
    { x: 82, y: 178 },
    { x: 102, y: 176 },
    { x: 128, y: 176 },
    { x: 160, y: 174 },
    { x: 192, y: 176 },
    { x: 218, y: 176 },
    { x: 238, y: 178 },
    { x: 105, y: 210 },
    { x: 128, y: 214 },
    { x: 155, y: 200 },
    { x: 180, y: 204 },
    { x: 205, y: 210 },
    { x: 223, y: 214 },
    { x: 95, y: 245 },
    { x: 125, y: 252 },
    { x: 160, y: 256 },
    { x: 195, y: 252 },
    { x: 225, y: 245 },
    { x: 120, y: 275 },
    { x: 170, y: 290 },
    { x: 220, y: 275 },
  ];

  const noise = (seed: number) => {
    const x = Math.sin(seed * 12.9898) * 43758.5453123;
    return x - Math.floor(x);
  };

  const nodes = baseNodes.map((node, i) => {
    const dx = (noise(i + 1) - 0.5) * 8;
    const dy = (noise(i + 97) - 0.5) * 8;
    return {
      x: node.x + dx,
      y: node.y + dy,
    };
  });

  const links: Array<[number, number]> = [];
  const seen = new Set<string>();

  nodes.forEach((node, i) => {
    const neighbors = nodes
      .map((other, j) => ({
        j,
        d:
          i === j
            ? Number.POSITIVE_INFINITY
            : Math.hypot(node.x - other.x, node.y - other.y),
      }))
      .sort((a, b) => a.d - b.d)
      .slice(0, i < 18 ? 4 : 3);

    neighbors.forEach(({ j }) => {
      const a = Math.min(i, j);
      const b = Math.max(i, j);
      const key = `${a}-${b}`;
      if (!seen.has(key)) {
        seen.add(key);
        links.push([a, b]);
      }
    });
  });

  const noiseParticles = Array.from({ length: 70 }, (_, i) => {
    const x = 50 + noise(i * 3 + 11) * 220;
    const y = 46 + noise(i * 7 + 29) * 280;
    const r = 0.6 + noise(i * 13 + 43) * 1.6;

    return {
      x,
      y,
      r,
      delay: `${(noise(i * 17 + 59) * 2.5).toFixed(2)}s`,
      duration: `${(1.6 + noise(i * 19 + 71) * 2.8).toFixed(2)}s`,
      opacity: 0.12 + noise(i * 23 + 83) * 0.4,
    };
  });

  return (
    <div className="relative overflow-hidden rounded-3xl border border-cyan-400/30 bg-zinc-950/70 p-4 shadow-2xl">
      <div className="absolute inset-0 bg-radial-[circle_at_center] from-cyan-400/10 via-transparent to-transparent" />
      <div className="neural-scan absolute inset-x-4 h-8 rounded-full bg-cyan-300/10 blur-md" />

      <svg viewBox="0 0 320 380" className="relative h-auto w-full">
        <defs>
          <linearGradient id="jarvisStroke" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#22d3ee" />
            <stop offset="100%" stopColor="#a78bfa" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="2.8" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <path
          d="M160 28
             C230 28 280 78 280 160
             C280 255 222 335 160 350
             C98 335 40 255 40 160
             C40 78 90 28 160 28Z"
          fill="none"
          stroke="url(#jarvisStroke)"
          strokeWidth="2.5"
          opacity="0.9"
          filter="url(#glow)"
        />

        {noiseParticles.map((p, i) => (
          <circle
            key={`noise-${i}`}
            className="neural-noise"
            cx={p.x}
            cy={p.y}
            r={p.r}
            fill="#a5f3fc"
            opacity={p.opacity}
            style={{
              animationDelay: p.delay,
              animationDuration: p.duration,
            }}
          />
        ))}

        <ellipse
          className="neural-eye"
          cx="125"
          cy="170"
          rx="22"
          ry="8"
          fill="#22d3ee"
          opacity="0.7"
        />
        <ellipse
          className="neural-eye"
          cx="195"
          cy="170"
          rx="22"
          ry="8"
          fill="#22d3ee"
          opacity="0.7"
        />

        {links.map(([a, b], i) => (
          <line
            key={i}
            x1={nodes[a].x}
            y1={nodes[a].y}
            x2={nodes[b].x}
            y2={nodes[b].y}
            stroke="url(#jarvisStroke)"
            strokeOpacity={0.18 + ((i % 7) / 7) * 0.34}
            strokeWidth={0.9 + (i % 3) * 0.32}
          />
        ))}

        {nodes.map((n, i) => (
          <circle
            key={i}
            className="neural-node"
            cx={n.x}
            cy={n.y}
            r={i % 5 === 0 ? 4.6 : i % 2 === 0 ? 3.4 : 2.7}
            fill="#67e8f9"
            opacity={0.72 + ((i % 4) / 4) * 0.25}
            filter="url(#glow)"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </svg>

      <p className="mt-2 text-center text-xs tracking-[0.2em] text-cyan-300/90">
        JARVIS NEURAL SIGNATURE
      </p>
    </div>
  );
}

export default function Home() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-linear-to-b from-zinc-950 via-zinc-900 to-black text-zinc-100">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 left-1/2 h-96 w-96 -translate-x-1/2 rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="absolute bottom-0 left-0 h-72 w-72 rounded-full bg-violet-500/10 blur-3xl" />
        <div className="absolute right-0 top-1/3 h-80 w-80 rounded-full bg-emerald-500/10 blur-3xl" />
      </div>

      <main className="relative mx-auto flex w-full max-w-6xl flex-col px-6 py-10 md:px-10 lg:px-16">
        <header className="mb-16 flex items-center justify-between">
          <div className="inline-flex items-center gap-3 rounded-full border border-zinc-700/70 bg-zinc-900/70 px-4 py-2 backdrop-blur">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />
            <span className="text-sm tracking-wide text-zinc-200">
              JARVIS · Double Numérique Intelligent
            </span>
          </div>
          <a
            href="#roadmap"
            className="rounded-full border border-zinc-700 px-4 py-2 text-sm text-zinc-200 transition hover:border-zinc-500 hover:bg-zinc-800"
          >
            Voir la roadmap
          </a>
        </header>

        <section className="mb-20 grid gap-10 lg:grid-cols-2 lg:items-center">
          <div>
            <p className="mb-4 text-sm uppercase tracking-[0.25em] text-cyan-300">
              Assistant IA personnel
            </p>
            <h1 className="mb-6 text-4xl font-bold leading-tight sm:text-5xl lg:text-6xl">
              Construire un{" "}
              <span className="text-cyan-300">Jarvis réaliste</span>,
              <br />
              progressif et contrôlé.
            </h1>
            <p className="mb-8 max-w-xl text-lg text-zinc-300">
              Une IA qui mémorise votre contexte, raisonne selon votre style,
              propose des plans d’action et exécute les tâches avec validation
              humaine.
            </p>
            <div className="flex flex-wrap items-center gap-3">
              <a
                href="#vision"
                className="rounded-full bg-cyan-400 px-6 py-3 font-semibold text-zinc-950 transition hover:bg-cyan-300"
              >
                Découvrir Jarvis
              </a>
              <a
                href="#architecture"
                className="rounded-full border border-zinc-600 px-6 py-3 font-semibold text-zinc-100 transition hover:border-zinc-400 hover:bg-zinc-800"
              >
                Architecture
              </a>
            </div>
          </div>

          <div className="space-y-4">
            <NeuralFace />

            <div className="rounded-3xl border border-zinc-700/70 bg-zinc-900/70 p-6 shadow-2xl backdrop-blur">
              <p className="mb-4 text-sm text-zinc-400">PROMESSE PRODUIT</p>
              <div className="space-y-3">
                {[
                  "Comprendre l’utilisateur et son contexte",
                  "Mémoriser court terme, long terme et sémantique (RAG)",
                  "Planifier et exécuter des actions utiles",
                  "Évoluer en continu grâce aux interactions",
                ].map((item) => (
                  <div
                    key={item}
                    className="flex items-start gap-3 rounded-xl bg-zinc-800/70 p-3"
                  >
                    <span className="mt-1 h-2 w-2 rounded-full bg-cyan-300" />
                    <p className="text-zinc-200">{item}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section id="vision" className="mb-16 grid gap-4 md:grid-cols-3">
          {[
            {
              title: "Raisonnement personnalisé",
              text: "Analyse des problèmes selon votre logique pour proposer des réponses cohérentes et actionnables.",
            },
            {
              title: "Mémoire augmentée",
              text: "Conservation du contexte et rappel intelligent via PostgreSQL, Redis et ChromaDB.",
            },
            {
              title: "Agent semi-autonome",
              text: "Jarvis agit avec validation explicite pour garantir sécurité, contrôle et traçabilité.",
            },
          ].map((card) => (
            <article
              key={card.title}
              className="rounded-2xl border border-zinc-700/70 bg-zinc-900/60 p-6 transition hover:-translate-y-1 hover:border-cyan-400/40"
            >
              <h2 className="mb-2 text-xl font-semibold text-zinc-100">
                {card.title}
              </h2>
              <p className="text-zinc-300">{card.text}</p>
            </article>
          ))}
        </section>

        <section
          id="architecture"
          className="mb-16 rounded-3xl border border-zinc-700/60 bg-zinc-900/70 p-8"
        >
          <h2 className="mb-6 text-2xl font-bold text-zinc-100">
            Architecture cible
          </h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[
              "Identity Core",
              "Memory System",
              "Reasoning Engine",
              "Planner",
              "Tool System",
              "Agent Controller",
            ].map((item) => (
              <div
                key={item}
                className="rounded-xl border border-zinc-700 bg-zinc-800/60 px-4 py-3 text-zinc-200"
              >
                {item}
              </div>
            ))}
          </div>
          <p className="mt-5 text-zinc-400">
            Stack prévue : FastAPI, LangChain/OpenAI, PostgreSQL, Redis,
            ChromaDB, Next.js + Tailwind.
          </p>
        </section>

        <section id="roadmap" className="mb-14">
          <h2 className="mb-6 text-2xl font-bold">Roadmap de construction</h2>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {[
              [
                "Phase 1",
                "MVP",
                "Chat intelligent, mémoire vectorielle, personnalisation",
              ],
              ["Phase 2", "Agent", "Tools, planification, actions simples"],
              [
                "Phase 3",
                "Assistant avancé",
                "Automatisation des tâches, dashboard",
              ],
              [
                "Phase 4",
                "Jarvis-like",
                "Voix, contrôle système, anticipation",
              ],
            ].map(([phase, title, desc]) => (
              <div
                key={phase}
                className="rounded-2xl border border-zinc-700 bg-zinc-900/70 p-5"
              >
                <p className="text-sm font-medium text-cyan-300">{phase}</p>
                <h3 className="mt-1 text-lg font-semibold text-zinc-100">
                  {title}
                </h3>
                <p className="mt-2 text-sm text-zinc-300">{desc}</p>
              </div>
            ))}
          </div>
        </section>

        <footer className="mt-auto rounded-2xl border border-cyan-500/30 bg-cyan-500/10 px-6 py-5 text-center">
          <p className="text-lg font-semibold">
            Jarvis : comprendre, raisonner, agir, évoluer.
          </p>
          <p className="mt-1 text-sm text-zinc-300">
            Une version augmentée de l’utilisateur, construite étape par étape.
          </p>
        </footer>
      </main>
    </div>
  );
}
