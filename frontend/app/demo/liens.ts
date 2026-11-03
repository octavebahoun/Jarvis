// Liens publics de la démo. Un seul endroit à mettre à jour à chaque version.

export const VIDEO_ID = "U_sVJ2BQKUo";
export const VIDEO_URL = `https://www.youtube.com/watch?v=${VIDEO_ID}`;
export const VIDEO_EMBED = `https://www.youtube-nocookie.com/embed/${VIDEO_ID}`;

const SHELL = "https://github.com/octavebahoun/o-jarvis-shell";
const OJARVIS = "https://github.com/octavebahoun/O-jarvis";

export const LIENS = {
  shell: SHELL,
  shellDeb: `${SHELL}/releases/latest`,
  shellPreuves: `${SHELL}/tree/main/docs/evidence`,
  shellHackathon: `${SHELL}/blob/main/HACKATHON.md`,
  ojarvis: OJARVIS,
  ojarvisVersion: `${OJARVIS}/releases/latest`,
  ojarvisLisezMoi: `${OJARVIS}/blob/main/README.fr.md`,
  ojarvisArchitecture: `${OJARVIS}/blob/main/docs/architecture.md`,
} as const;

export type Lien = { titre: string; texte: string; href: string };

export const DEPOTS: Lien[] = [
  {
    titre: "O-jarvis Shell",
    texte:
      "Jarvis dans le terminal, dans Chrome et sur le bureau, sur les modèles Meta.",
    href: LIENS.shell,
  },
  {
    titre: "O-jarvis",
    texte:
      "L'application de bureau (Tauri, React) et son moteur Python (FastAPI).",
    href: LIENS.ojarvis,
  },
];

export const DOCS: Lien[] = [
  {
    titre: "Preuves",
    texte: "Essais enregistrés et transcriptions, sur un vrai Ubuntu.",
    href: LIENS.shellPreuves,
  },
  {
    titre: "Fait pendant le hackathon",
    texte: "Ce qui a été construit du 26 octobre au 4 novembre 2026.",
    href: LIENS.shellHackathon,
  },
  {
    titre: "Lisez-moi d'O-jarvis",
    texte: "Installation depuis les sources, vérifications, licence.",
    href: LIENS.ojarvisLisezMoi,
  },
  {
    titre: "Architecture",
    texte: "Le moteur, l'application et la façon dont ils se parlent.",
    href: LIENS.ojarvisArchitecture,
  },
];
