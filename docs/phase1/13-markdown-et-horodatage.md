# 13 — Rendu markdown + horodatage des messages

## Ce qui a été construit

- **Rendu markdown** (`ChatWindow.tsx`) : les messages de l'assistant (message
  final et bulle en cours de streaming) passent par `react-markdown` au lieu
  d'un texte brut — gras/italique, listes, code inline, liens sont maintenant
  rendus correctement. Stylé avec `@tailwindcss/typography`
  (`prose prose-invert prose-sm`), ajouté via `@plugin` dans `globals.css`
  (syntaxe CSS-first de Tailwind v4).
  - Les messages **utilisateur** restent en texte brut : ce sont ceux qu'on a
    tapés soi-même, pas une sortie LLM à mettre en forme — et ça évite un
    mauvais contraste avec `prose-invert` sur un fond clair (bulle cyan).
- **Horodatage** : chaque bulle affiche l'heure locale (`HH:MM`, via
  `toLocaleTimeString`), sous la bulle. Utilise le `ts` déjà stocké côté
  backend (doc 09) et rapatrié par `getShortTermHistory`.

## Sécurité

`react-markdown` n'exécute pas de HTML brut par défaut (pas de plugin
`rehype-raw` ajouté) : impossible d'injecter du HTML/script via une réponse du
LLM ou un message utilisateur affiché en markdown.

## Vérifié

- `tsc --noEmit` et `npm run lint` propres (a aussi révélé et corrigé une
  erreur de lint préexistante sur l'effet de résolution du `session_id`,
  passée inaperçue faute d'avoir relancé `lint` depuis la doc 09).
- Test réel en navigateur : réponse contenant gras, liste à puces, code inline
  et lien, rendus correctement ; horodatage visible sous chaque bulle.
