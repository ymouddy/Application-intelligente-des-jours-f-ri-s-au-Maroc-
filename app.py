"""Point d'entrée de l'application Flask."""
from datetime import date

from flask import Flask, abort, jsonify, render_template, request  # pyright: ignore[reportMissingImports]
from importlib import import_module

try:
    import_module("dotenv").load_dotenv()
except ModuleNotFoundError:
    pass

from services import ai_service, holidays_service as hs  # noqa: E402

app = Flask(__name__)
MIN_YEAR, MAX_YEAR = 2024, 2040


def _year() -> int:
    try:
        y = int(request.args.get("year", date.today().year))
    except ValueError:
        y = date.today().year
    return min(max(y, MIN_YEAR), MAX_YEAR)


@app.route("/")
def home():
    year = _year()
    today = date.today()
    items = hs.holidays_for_year(year)
    upcoming = [h for h in items if h["start"] >= today][:3] or items[:3]
    return render_template("index.html", year=year, upcoming=upcoming)


@app.route("/calendrier")
def calendar():
    year = _year()
    kind = request.args.get("type", "toutes")
    items = hs.holidays_for_year(year)
    if kind in ("nationale", "religieuse"):
        items = [h for h in items if h["type"] == kind]
    return render_template("calendar.html", year=year, kind=kind, items=items,
                           years=range(MIN_YEAR, MAX_YEAR + 1), mois=hs.MOIS)


@app.route("/fete/<slug>")
def detail(slug):
    base = hs.get_by_slug(slug)
    if not base:
        abort(404)
    year = _year()
    return render_template("detail.html", h=hs.enrich(base, year), year=year)


@app.route("/chat")
def chat_page():
    return render_template("chat.html", year=_year())


@app.post("/api/chat")
def api_chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify(error="Question vide"), 400
    answer = ai_service.ask(question, data.get("history", []), data.get("slug"),
                            data.get("level", "simple"), int(data.get("year", date.today().year)))
    return jsonify(answer=answer)


@app.errorhandler(404)
def not_found(_):
    return render_template("base.html", content="Page introuvable."), 404


if __name__ == "__main__":
    app.run(debug=True)
