"""Dibuja data/contributions.json como calendario animado (contrib-heatmap.svg).

STATIC=1 emite el fotograma final sin animación.
"""
import json
import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]  # nivel 0 -> 4
BG, FG, MUTED = "#0d1117", "#c9d1d9", "#8b949e"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
CELL, GAP = 12, 3
LEFT, TOP = 46, 44
WIDTH = 860
MONTHS = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
STATIC = os.environ.get("STATIC") == "1"


def main() -> None:
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    days = data["days"]
    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # las columnas empiezan en domingo, como en GitHub
    pitch = CELL + GAP
    weeks = (offset + len(days) + 6) // 7
    height = TOP + 7 * pitch + 62

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}" font-family="{FONT}" font-size="11">',
        "<style>"
        ".c{opacity:0;animation:drop .45s ease-out forwards}"
        "@keyframes drop{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}"
        ".t{opacity:0;animation:fade .6s ease-out forwards}"
        "@keyframes fade{to{opacity:1}}"
        "</style>" if not STATIC else "",
        f'<rect width="{WIDTH}" height="{height}" rx="12" fill="{BG}"/>',
    ]
    for row, label in ((1, "lun"), (3, "mié"), (5, "vie")):
        out.append(f'<text x="14" y="{TOP + row * pitch + 10}" fill="{MUTED}">{label}</text>')

    last_month, label_week = None, -99
    for i, d in enumerate(days):
        week, row = divmod(i + offset, 7)
        x, y = LEFT + week * pitch, TOP + row * pitch
        month = d["date"][5:7]
        if month != last_month and row == 0:
            last_month = month
        # Una etiqueta por mes, salvo que quede pegada a la anterior o al borde
        if month == last_month and row == 0 and d["date"][8:] <= "07" and week - label_week >= 3 and week < weeks - 1:
            label_week = week
            out.append(f'<text x="{x}" y="{TOP - 10}" fill="{MUTED}">{MONTHS[int(month) - 1]}</text>')
        anim = "" if STATIC else f' class="c" style="animation-delay:{(week + row) * 0.022:.3f}s"'
        out.append(
            f'<rect{anim} x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{PALETTE[min(d["level"], 4)]}"><title>{d["date"]}: {d["count"]}</title></rect>'
        )

    foot = TOP + 7 * pitch + 28
    tcls = "" if STATIC else ' class="t" style="animation-delay:1.4s"'
    total = f'{data["total"]:,}'.replace(",", ".")
    out.append(
        f'<text{tcls} x="{LEFT}" y="{foot}" fill="{FG}" font-size="13">'
        f'{total} contribuciones en el último año</text>'
    )
    best = data["best_day"]
    out.append(
        f'<text{tcls} x="{LEFT}" y="{foot + 20}" fill="{MUTED}">'
        f'racha actual {data["current_streak"]}d · racha más larga {data["longest_streak"]}d · '
        f'mejor día {best["count"]} ({best["date"]})</text>'
    )
    # Leyenda Menos -> Más, alineada a la derecha de la rejilla
    right = LEFT + weeks * pitch - GAP
    lx = right - 5 * pitch - 34
    out.append(f'<text{tcls} x="{lx - 44}" y="{foot}" fill="{MUTED}">Menos</text>')
    for n, color in enumerate(PALETTE):
        out.append(f'<rect{tcls} x="{lx + n * pitch}" y="{foot - 10}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"/>')
    out.append(f'<text{tcls} x="{lx + 5 * pitch + 4}" y="{foot}" fill="{MUTED}">Más</text>')
    out.append("</svg>")
    (ROOT / "contrib-heatmap.svg").write_text("\n".join(filter(None, out)) + "\n")
    print(f"contrib-heatmap.svg ({weeks} semanas)")


if __name__ == "__main__":
    main()
