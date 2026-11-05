# 🇲🇦 Jours fériés du Maroc – application avec IA

Application Flask + API OpenAI pour découvrir les jours fériés marocains : calendrier par année,
fiches détaillées (FR/AR), chatbot IA spécialisé et explications à trois niveaux.

## Architecture
```
app.py                    Routes Flask (pages + API /api/chat)
services/
  holidays_service.py     Lecture du JSON + calcul des dates (grégorien / hégirien)
  ai_service.py           Prompt système spécialisé + appel OpenAI
data/holidays.json        Base de données des 14 fêtes (modifiable facilement)
templates/                Pages HTML (Jinja2)
static/css, js, images    Style, chatbot, illustrations
tools/generate_images.py  Génère les illustrations SVG
```

## Installation
```bash
python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # puis ajoutez votre clé OPENAI_API_KEY
python app.py                   # http://127.0.0.1:5000
```
Sans clé API, tout fonctionne sauf le chatbot (un message d'aide s'affiche).

## Dates religieuses : point important
Les dates de l'Aïd al-Fitr, l'Aïd al-Adha, du 1er Muharram et du Mawlid sont calculées avec le
calendrier hégirien (bibliothèque `hijri-converter`). Elles sont **toujours indiquées comme
prévisionnelles** (interface + consigne dans le prompt IA) : l'annonce officielle dépend de
l'observation du croissant et du ministère des Habous. Un écart de ±1 à 2 jours est possible.

## Personnaliser
- Ajouter/modifier une fête : éditez `data/holidays.json`.
- Vraies photos : placez-les dans `static/images/` et changez le champ `"image"`
  (vérifiez les droits d'utilisation).
- Changer de modèle : variable `OPENAI_MODEL` dans `.env`.
- Vérifiez toujours les liens « sources » avant publication.

## Pistes d'amélioration
Cache des explications IA (SQLite), version arabe de l'interface, export du calendrier (.ics), tests.
