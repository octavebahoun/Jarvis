/**
 * Traduction d'une expression cron en français lisible.
 *
 * Les crons de Jarvis sont **toujours évalués en UTC** (cf.
 * `scheduler/registry.py`). La description produite ici reste donc en UTC :
 * convertir aussi les jours de semaine ferait dériver le libellé d'un jour
 * près des bornes de minuit, ce qui serait plus trompeur qu'utile.
 * `localTimeHint()` fournit séparément l'heure locale équivalente, sans
 * toucher au jour.
 *
 * Toute expression non reconnue retombe sur l'expression brute : mieux vaut
 * afficher le cron tel quel qu'une paraphrase fausse.
 */

const DAY_NAMES = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];

const MONTH_NAMES = [
  "janvier",
  "février",
  "mars",
  "avril",
  "mai",
  "juin",
  "juillet",
  "août",
  "septembre",
  "octobre",
  "novembre",
  "décembre",
];

function pad(value: number): string {
  return String(value).padStart(2, "0");
}

/** Un champ cron représentant une valeur numérique unique (pas `*`, pas de liste/pas/intervalle). */
function fixedValue(field: string): number | null {
  if (!/^\d+$/.test(field)) return null;
  return Number(field);
}

function stepValue(field: string): number | null {
  const match = /^\*\/(\d+)$/.exec(field);
  return match ? Number(match[1]) : null;
}

export function describeCron(schedule: string): string {
  const fields = schedule.trim().split(/\s+/);
  if (fields.length !== 5) return schedule;

  const [rawMinute, rawHour, rawDom, rawMonth, rawDow] = fields;

  const minute = fixedValue(rawMinute);
  const hour = fixedValue(rawHour);
  const dom = fixedValue(rawDom);
  const month = fixedValue(rawMonth);
  const dow = fixedValue(rawDow);

  const minuteStep = stepValue(rawMinute);
  const hourStep = stepValue(rawHour);

  // Toutes les N minutes : */5 * * * *
  if (minuteStep !== null && rawHour === "*" && rawDom === "*" && rawMonth === "*" && rawDow === "*") {
    return minuteStep === 1 ? "Toutes les minutes" : `Toutes les ${minuteStep} minutes`;
  }

  // Toutes les N heures : 0 */2 * * *
  if (minute !== null && hourStep !== null && rawDom === "*" && rawMonth === "*" && rawDow === "*") {
    const suffix = minute === 0 ? "" : ` (à la minute ${minute})`;
    return hourStep === 1 ? `Toutes les heures${suffix}` : `Toutes les ${hourStep} heures${suffix}`;
  }

  // Toutes les heures à une minute fixe : 30 * * * *
  if (minute !== null && rawHour === "*" && rawDom === "*" && rawMonth === "*" && rawDow === "*") {
    return `Toutes les heures à la minute ${minute}`;
  }

  const time = minute !== null && hour !== null ? `${pad(hour)}:${pad(minute)} UTC` : null;
  if (time === null) return schedule;

  // Ponctuel / annuel : 30 14 5 8 *
  if (dom !== null && month !== null && rawDow === "*") {
    return `Le ${dom} ${MONTH_NAMES[month - 1] ?? rawMonth} à ${time}`;
  }

  // Hebdomadaire : 0 8 * * 1
  if (rawDom === "*" && rawMonth === "*" && dow !== null) {
    return `Tous les ${DAY_NAMES[dow % 7] ?? rawDow}s à ${time}`;
  }

  // Mensuel : 0 8 1 * *
  if (dom !== null && rawMonth === "*" && rawDow === "*") {
    return `Le ${dom} de chaque mois à ${time}`;
  }

  // Quotidien : 0 8 * * *
  if (rawDom === "*" && rawMonth === "*" && rawDow === "*") {
    return `Tous les jours à ${time}`;
  }

  return schedule;
}

/**
 * Heure locale équivalente à l'heure UTC du cron, ou `null` si l'expression
 * ne fixe pas d'heure précise (ex. `*​/5 * * * *`).
 *
 * Dépend du fuseau du navigateur : à n'appeler que côté client (après montage),
 * sinon le rendu serveur et le rendu client divergent.
 */
export function localTimeHint(schedule: string): string | null {
  const fields = schedule.trim().split(/\s+/);
  if (fields.length !== 5) return null;

  const minute = fixedValue(fields[0]);
  const hour = fixedValue(fields[1]);
  if (minute === null || hour === null) return null;

  const reference = new Date();
  reference.setUTCHours(hour, minute, 0, 0);

  if (reference.getUTCHours() === reference.getHours() && reference.getUTCMinutes() === reference.getMinutes()) {
    return null; // Navigateur déjà en UTC : l'indication n'apporterait rien.
  }

  return `${pad(reference.getHours())}:${pad(reference.getMinutes())} chez toi`;
}
