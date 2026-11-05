"""Lecture des jours fériés et calcul des dates pour une année donnée."""
import json
from datetime import date, timedelta
from pathlib import Path

from hijri_converter import Hijri

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "holidays.json"

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def format_fr(d: date) -> str:
    return f"{JOURS[d.weekday()]} {d.day} {MOIS[d.month - 1]} {d.year}"


def load_all() -> list[dict]:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def get_by_slug(slug: str) -> dict | None:
    return next((h for h in load_all() if h["slug"] == slug), None)


def _start_date(rule: dict, year: int) -> date | None:
    """Date grégorienne de début d'une fête pour l'année demandée."""
    if rule["calendar"] == "gregorian":
        return date(year, rule["month"], rule["day"])
    # Calendrier hégirien : une même fête tombe une fois par année grégorienne
    # L'année hégirienne (lunaire) est plus courte : 1 an grégorien ≈ 1,0307 an hégirien
    approx = round((year - 621.57) * 1.0307)
    for hijri_year in (approx - 1, approx, approx + 1):
        try:
            g = Hijri(hijri_year, rule["month"], rule["day"]).to_gregorian()
        except (ValueError, OverflowError):
            continue
        if g.year == year:
            return date(g.year, g.month, g.day)
    return None


def enrich(holiday: dict, year: int) -> dict | None:
    """Ajoute les dates calculées à une fête."""
    start = _start_date(holiday["rule"], year)
    if start is None:
        return None
    days = [start + timedelta(days=i) for i in range(holiday["rule"].get("duration", 1))]
    item = dict(holiday)
    item["year"] = year
    item["start"] = start
    item["dates_fr"] = [format_fr(d) for d in days]
    item["month"] = start.month
    # Les fêtes religieuses dépendent de l'observation de la lune : jamais définitives
    item["is_forecast"] = holiday["type"] == "religieuse"
    return item


def holidays_for_year(year: int) -> list[dict]:
    items = [enrich(h, year) for h in load_all()]
    return sorted((i for i in items if i), key=lambda i: i["start"])
