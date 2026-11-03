import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import {
  DEPOTS,
  DOCS,
  LIENS,
  VIDEO_EMBED,
  VIDEO_URL,
  type Lien,
} from "./liens";

export const metadata: Metadata = {
  title: "Démo O-jarvis — Jarvis sur Ubuntu",
  description:
    "La vidéo, le téléchargement et le code d'O-jarvis et d'O-jarvis Shell : un assistant qui agit sur le terminal, Chrome et le bureau, toujours avec votre accord.",
};

const externe = { target: "_blank", rel: "noreferrer" } as const;

const bouton =
  "rounded-full px-6 py-3 font-semibold transition focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300";
const boutonPlein = `${bouton} bg-cyan-400 text-zinc-950 hover:bg-cyan-300`;
const boutonVide = `${bouton} border border-zinc-600 text-zinc-100 hover:border-zinc-400 hover:bg-zinc-800`;

const LIEUX = [
  {
    titre: "Dans le terminal",
    texte:
      "o-jarvis-shell s'ouvre dans n'importe quel dossier. Il lit tout de suite (fichiers, git, df…) et propose les commandes qui changent quelque chose.",
  },
  {
    titre: "Dans Chrome",
    texte:
      "Une extension met Jarvis à côté de la page que vous lisez : il la résume, clique ou remplit les champs de votre onglet.",
  },
  {
    titre: "Sur le bureau",
    texte:
      "SAM 3.1 repère les boutons de n'importe quelle application ; Jarvis clique le bon par le portail de GNOME, et vous voyez le pointeur y aller.",
  },
];

const NIVEAUX = [
  {
    nom: "Lecture",
    regle: "s'exécute tout de suite",
    couleur: "text-cyan-300 border-cyan-400/40 bg-cyan-400/10",
  },
  {
    nom: "Action",
    regle: "attend votre « o »",
    couleur: "text-amber-300 border-amber-400/40 bg-amber-400/10",
  },
  {
    nom: "Destruction",
    regle: "demande « oui » tapé en entier",
    couleur: "text-rose-300 border-rose-400/40 bg-rose-400/10",
  },
];

const CAPTURES = [
  { src: "/demo/accueil.webp", legende: "L'accueil : la sphère montre l'état de Jarvis." },
  { src: "/demo/automatisations.webp", legende: "Rappels et tâches qui survivent au redémarrage." },
  { src: "/demo/skills-et-plugins.webp", legende: "Skills testés en bac à sable et serveurs MCP." },
];

const ETAPES = [
  {
    titre: "Téléchargez le .deb",
    code: "sudo apt install ./O-jarvis_*_amd64.deb",
    note: "Il installe l'application, O-jarvis Shell et l'extension Chrome.",
  },
  {
    titre: "Ouvrez l'application une fois",
    code: "o-jarvis",
    note: "L'écran d'accueil demande vos clés et les permissions de GNOME.",
  },
  {
    titre: "Parlez-lui depuis un dossier",
    code: "cd ~/mon-projet && o-jarvis-shell",
    note: "Puis demandez : « Combien d'espace reste-t-il sur le disque ? »",
  },
];

function Titre({ sur, children }: { sur: string; children: React.ReactNode }) {
  return (
    <div className="mb-6">
      <p className="mb-2 text-sm uppercase tracking-[0.25em] text-cyan-300">{sur}</p>
      <h2 className="text-2xl font-bold text-zinc-100 sm:text-3xl">{children}</h2>
    </div>
  );
}

function CarteLien({ lien }: { lien: Lien }) {
  return (
    <a
      href={lien.href}
      {...externe}
      className="group rounded-2xl border border-zinc-700/70 bg-zinc-900/60 p-5 transition hover:-translate-y-1 hover:border-cyan-400/40"
    >
      <p className="font-semibold text-zinc-100">
        {lien.titre}{" "}
        <span aria-hidden className="text-cyan-300 transition group-hover:translate-x-1">
          ↗
        </span>
      </p>
      <p className="mt-1 text-sm text-zinc-400">{lien.texte}</p>
    </a>
  );
}

export default function Demo() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-linear-to-b from-zinc-950 via-zinc-900 to-black font-[family-name:var(--font-geist-sans)] text-zinc-100">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 left-1/2 h-96 w-96 -translate-x-1/2 rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="absolute right-0 top-1/3 h-80 w-80 rounded-full bg-violet-500/10 blur-3xl" />
      </div>

      <main className="relative mx-auto flex w-full max-w-6xl flex-col gap-20 px-4 py-10 sm:px-6 md:px-10 lg:px-16">
        <header className="flex flex-wrap items-center justify-between gap-3">
          <div className="inline-flex items-center gap-3 rounded-full border border-zinc-700/70 bg-zinc-900/70 px-4 py-2 backdrop-blur">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />
            <span className="text-sm tracking-wide text-zinc-200">O-jarvis · Démo</span>
          </div>
          <Link
            href="/"
            className="rounded-full border border-zinc-700 px-4 py-2 text-sm text-zinc-200 transition hover:border-zinc-500 hover:bg-zinc-800"
          >
            ← Le projet Jarvis
          </Link>
        </header>

        <section className="grid gap-10 lg:grid-cols-[1.1fr_1fr] lg:items-center">
          <div>
            <p className="mb-4 text-sm uppercase tracking-[0.25em] text-cyan-300">
              Assistant personnel pour Ubuntu
            </p>
            <h1 className="mb-6 text-4xl font-bold leading-tight sm:text-5xl">
              Jarvis ne fait pas que parler. <span className="text-cyan-300">Il agit</span>, avec
              votre accord.
            </h1>
            <p className="mb-8 max-w-xl text-lg text-zinc-300">
              Sur votre terminal, votre Chrome et votre bureau. O-jarvis Shell n&apos;appelle que des
              modèles Meta : Muse Spark répond, SAM 3.1 trouve où cliquer, les voix MMS parlent sur
              votre processeur.
            </p>
            <div className="flex flex-wrap gap-3">
              <a href="#video" className={boutonPlein}>
                Voir la vidéo
              </a>
              <a href={LIENS.shellDeb} {...externe} className={boutonVide}>
                Télécharger le .deb
              </a>
              <a href={LIENS.shell} {...externe} className={boutonVide}>
                Code source
              </a>
            </div>
          </div>
          <Image
            src="/demo/accueil.webp"
            alt="Accueil d'O-jarvis : une sphère de points lumineux, « Jarvis est prêt »"
            width={1440}
            height={900}
            priority
            className="rounded-3xl border border-cyan-400/30 shadow-2xl"
          />
        </section>

        <section id="video" className="scroll-mt-8">
          <Titre sur="La démo">2 min 56, sur un vrai Ubuntu, avec les vrais modèles</Titre>
          <div className="overflow-hidden rounded-3xl border border-zinc-700/70 bg-black shadow-2xl">
            <iframe
              src={VIDEO_EMBED}
              title="Vidéo de démonstration d'O-jarvis Shell"
              loading="lazy"
              allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              referrerPolicy="strict-origin-when-cross-origin"
              allowFullScreen
              className="aspect-video w-full"
            />
          </div>
          <p className="mt-3 text-sm text-zinc-400">
            La vidéo ne se lance pas ?{" "}
            <a href={VIDEO_URL} {...externe} className="text-cyan-300 underline-offset-4 hover:underline">
              Ouvrez-la sur YouTube
            </a>
            .
          </p>
        </section>

        <section>
          <Titre sur="Ce qu'il fait">Trois endroits, un seul Jarvis</Titre>
          <div className="grid gap-4 md:grid-cols-3">
            {LIEUX.map((lieu) => (
              <article
                key={lieu.titre}
                className="rounded-2xl border border-zinc-700/70 bg-zinc-900/60 p-6 transition hover:-translate-y-1 hover:border-cyan-400/40"
              >
                <h3 className="mb-2 text-xl font-semibold text-zinc-100">{lieu.titre}</h3>
                <p className="text-zinc-300">{lieu.texte}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="grid gap-10 lg:grid-cols-2 lg:items-center">
          <div>
            <Titre sur="Sous votre contrôle">Le code décide, pas le modèle</Titre>
            <p className="mb-6 text-zinc-300">
              Chaque commande est classée par des règles écrites dans le code. Toute action devient
              un plan que vous validez.
            </p>
            <ul className="space-y-3">
              {NIVEAUX.map((niveau, i) => (
                <li
                  key={niveau.nom}
                  className="flex flex-col items-start gap-2 rounded-xl bg-zinc-800/70 px-4 py-3 sm:flex-row sm:items-center sm:justify-between sm:gap-4"
                >
                  <span className={`rounded-full border px-3 py-1 text-xs font-semibold tracking-wider uppercase ${niveau.couleur}`}>
                    Niveau {i + 1} · {niveau.nom}
                  </span>
                  <span className="text-zinc-200 sm:text-right">{niveau.regle}</span>
                </li>
              ))}
            </ul>
            <p className="mt-6 text-sm text-zinc-400">
              Chaque action entre dans un journal en ajout seul, chaîné par SHA-256 et vérifié au
              démarrage. Les clés restent dans le trousseau du système.
            </p>
          </div>
          <Image
            src="/demo/plan.webp"
            alt="Un plan en trois étapes, « Action en attente de ta validation », avec les boutons Refuser et Valider"
            width={1440}
            height={900}
            className="rounded-3xl border border-zinc-700/70 shadow-2xl"
          />
        </section>

        <section>
          <Titre sur="L'application">Tout se voit, tout se modifie</Titre>
          <div className="grid gap-4 md:grid-cols-3">
            {CAPTURES.map((capture) => (
              <figure key={capture.src} className="rounded-2xl border border-zinc-700/70 bg-zinc-900/60 p-3">
                <Image
                  src={capture.src}
                  alt={capture.legende}
                  width={1440}
                  height={900}
                  sizes="(min-width: 768px) 33vw, 100vw"
                  className="rounded-xl"
                />
                <figcaption className="mt-3 px-1 text-sm text-zinc-300">{capture.legende}</figcaption>
              </figure>
            ))}
          </div>
        </section>

        <section>
          <Titre sur="L'essayer">Trois commandes</Titre>
          <p className="mb-6 text-zinc-300">
            Il faut Ubuntu 24.04 ou plus récent (x86_64, GNOME sous Wayland pour le bureau) et une
            clé de l&apos;API Meta.{" "}
            <a href={LIENS.shellDeb} {...externe} className="text-cyan-300 underline-offset-4 hover:underline">
              Dernière version
            </a>
            .
          </p>
          <ol className="grid gap-4 md:grid-cols-3">
            {ETAPES.map((etape, i) => (
              <li key={etape.titre} className="rounded-2xl border border-zinc-700 bg-zinc-900/70 p-5">
                <p className="text-sm font-medium text-cyan-300">Étape {i + 1}</p>
                <h3 className="mt-1 text-lg font-semibold text-zinc-100">{etape.titre}</h3>
                <pre className="mt-3 rounded-lg bg-black/60 px-3 py-2 font-mono text-sm whitespace-pre-wrap break-all text-emerald-300">
                  <code>{etape.code}</code>
                </pre>
                <p className="mt-3 text-sm text-zinc-400">{etape.note}</p>
              </li>
            ))}
          </ol>
        </section>

        <section>
          <Titre sur="Les liens">Le code et les preuves</Titre>
          <div className="grid gap-4 sm:grid-cols-2">
            {DEPOTS.map((lien) => (
              <CarteLien key={lien.href} lien={lien} />
            ))}
          </div>
          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {DOCS.map((lien) => (
              <CarteLien key={lien.href} lien={lien} />
            ))}
          </div>
        </section>

        <footer className="rounded-2xl border border-cyan-500/30 bg-cyan-500/10 px-6 py-5 text-center">
          <p className="text-lg font-semibold">Comprendre, raisonner, agir, avec votre accord.</p>
          <p className="mt-1 text-sm text-zinc-300">
            Construit pour le Meta Global AI Developer Hackathon (26 octobre – 4 novembre 2026). Code
            ouvert sous licence MIT.
          </p>
        </footer>
      </main>
    </div>
  );
}
