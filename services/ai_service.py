"""Appels à l'API OpenAI, avec un prompt spécialisé dans les jours fériés marocains."""
import os

from openai import OpenAI

from services import holidays_service as hs

LEVELS = {
    "simple": "Explique comme à un enfant de 10 ans : phrases courtes, mots simples.",
    "intermediaire": "Explique pour un adulte curieux : clair, avec quelques repères historiques.",
    "expert": "Explique avec précision historique, vocabulaire riche et nuances.",
}

SYSTEM_PROMPT = """Tu es « Dalil », un assistant spécialisé UNIQUEMENT dans les jours fériés
officiels du Maroc (fêtes nationales et religieuses), leur histoire, leur signification et leurs traditions.

Règles :
- Réponds en français, sauf si l'utilisateur écrit dans une autre langue.
- Si la question n'a aucun rapport avec les fêtes et la culture marocaines, redirige poliment.
- Distingue clairement les fêtes NATIONALES (dates fixes, calendrier grégorien) des fêtes
  RELIGIEUSES (calendrier hégirien, dates dépendant de l'observation du croissant lunaire).
- Les dates des fêtes religieuses sont toujours PRÉVISIONNELLES : écris « date prévisionnelle »
  et précise que l'annonce officielle revient au ministère des Habous et des Affaires islamiques.
  Ne présente JAMAIS une telle date comme définitive.
- Si tu n'es pas sûr d'un fait, dis-le au lieu d'inventer. N'invente ni source ni citation.
- {niveau}
"""


def _client() -> OpenAI | None:
    key = os.getenv("OPENAI_API_KEY")
    return OpenAI(api_key=key) if key else None


def _context(slug: str | None, year: int) -> str:
    """Données de référence injectées dans le prompt pour limiter les hallucinations."""
    lines = [f"Calendrier {year} (calculé automatiquement) :"]
    for h in hs.holidays_for_year(year):
        tag = " [PRÉVISIONNELLE]" if h["is_forecast"] else ""
        lines.append(f"- {h['name_fr']} ({h['type']}) : {', '.join(h['dates_fr'])}{tag}")
    if slug and (h := hs.get_by_slug(slug)):
        lines.append(f"\nFête actuellement consultée : {h['name_fr']}")
        lines.append(f"Origine : {h['origin']}\nSignification : {h['meaning']}")
        lines.append(f"Importance au Maroc : {h['importance']}")
        lines.append("Traditions : " + " ; ".join(h["traditions"]))
    return "\n".join(lines)


def ask(question: str, history: list[dict], slug: str | None = None,
        level: str = "simple", year: int = 2026) -> str:
    client = _client()
    if client is None:
        return ("⚠️ Clé API manquante. Ajoutez OPENAI_API_KEY dans le fichier .env "
                "puis relancez l'application.")

    system = SYSTEM_PROMPT.format(niveau=LEVELS.get(level, LEVELS["simple"]))
    messages = [{"role": "system", "content": system + "\n\n" + _context(slug, year)}]
    for m in history[-6:]:  # on garde seulement les derniers échanges
        if m.get("role") in ("user", "assistant") and isinstance(m.get("content"), str):
            messages.append({"role": m["role"], "content": m["content"][:2000]})
    messages.append({"role": "user", "content": question[:1500]})

    try:
        r = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages, temperature=0.4, max_tokens=700)
        return r.choices[0].message.content
    except Exception as exc:  # réseau, quota, clé invalide...
        return f"Désolé, l'IA est indisponible pour le moment ({type(exc).__name__})."
