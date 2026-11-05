"""Génère une illustration SVG par fête (placeholder facile à remplacer).
Pour utiliser de vraies photos : déposez-les dans static/images/ et modifiez le champ
"image" du fichier data/holidays.json (ex. "images/aid-al-fitr.jpg")."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for h in json.loads((ROOT / "data" / "holidays.json").read_text(encoding="utf-8")):
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="{h['color']}"/><stop offset="1" stop-color="#111"/></linearGradient></defs>
<rect width="800" height="450" fill="url(#g)"/>
<circle cx="650" cy="90" r="120" fill="#fff" opacity=".08"/>
<circle cx="120" cy="400" r="160" fill="#fff" opacity=".06"/>
<text x="400" y="240" font-size="150" text-anchor="middle">{h['emoji']}</text>
<text x="400" y="360" font-size="38" fill="#fff" text-anchor="middle" font-family="sans-serif">{h['name_ar']}</text>
</svg>"""
    (ROOT / "static" / "images" / f"{h['slug']}.svg").write_text(svg, encoding="utf-8")
print("Images générées.")
