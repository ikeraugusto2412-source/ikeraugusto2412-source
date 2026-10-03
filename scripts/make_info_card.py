"""Tarjeta estilo neofetch (info-card.svg). Edita ROWS para cambiar el contenido.

STATIC=1 emite el fotograma final sin animación.
"""
import os
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H = 880, 665  # misma proporción que el hueco de 490px junto al retrato
BG, BAR, FG, MUTED = "#0d1117", "#161b22", "#c9d1d9", "#8b949e"
KEY, ACCENT = "#39d353", "#58a6ff"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
STATIC = os.environ.get("STATIC") == "1"

TITLE = "iker@github"
# (clave, valor). Clave vacía = línea de continuación; None = línea en blanco.
ROWS = [
    ("Now", "Junior DAW developer"),
    ("Where", "Barcelona"),
    None,
    ("Stack", "Python · TypeScript · Next.js"),
    ("", "Supabase · HTML/CSS"),
    None,
    ("Projects", "garmin-coach"),
    ("", "  entrenador con Claude + Garmin (MCP)"),
    ("", "bajo-control"),
    ("", "  app de finanzas personales"),
    ("", "ikeraugusto"),
    ("", "  portfolio web"),
    None,
    ("Also", "Fotografía y vídeo"),
]
SWATCHES = ["#0e4429", "#006d32", "#26a641", "#39d353", "#58a6ff", "#bc8cff", "#f778ba", "#ffa657"]


def main() -> None:
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'font-family="{FONT}" font-size="24">',
        "<style>"
        ".l{opacity:0;animation:in .4s ease-out forwards}"
        "@keyframes in{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}"
        "</style>" if not STATIC else "",
        f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>',
        f'<path d="M0 14a14 14 0 0 1 14-14h{W - 28}a14 14 0 0 1 14 14v38H0z" fill="{BAR}"/>',
    ]
    for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        out.append(f'<circle cx="{30 + i * 26}" cy="26" r="8" fill="{c}"/>')
    out.append(f'<text x="{W / 2}" y="33" fill="{MUTED}" font-size="18" text-anchor="middle">neofetch</text>')

    step = 0

    def line(y: float, body: str) -> None:
        nonlocal step
        cls = "" if STATIC else f' class="l" style="animation-delay:{0.3 + step * 0.09:.2f}s"'
        out.append(f'<g{cls}>{body}</g>')
        step += 1

    y = 104
    user, host = TITLE.split("@")
    line(y, f'<text x="40" y="{y}" font-weight="700"><tspan fill="{KEY}">{user}</tspan>'
            f'<tspan fill="{FG}">@</tspan><tspan fill="{KEY}">{host}</tspan></text>')
    y += 22
    line(y, f'<rect x="40" y="{y - 8}" width="{len(TITLE) * 14.5:.0f}" height="2" fill="{MUTED}"/>')
    y += 34
    section = ""
    for row in ROWS:
        if row is None:
            y += 16
            continue
        key, value = row
        section = key or section
        is_desc = value.startswith("  ")
        color = MUTED if is_desc else (ACCENT if section == "Projects" else FG)
        body = f'<text x="40" y="{y}" fill="{KEY}" font-weight="700">{escape(key)}</text>' if key else ""
        size = ' font-size="20"' if is_desc else ""
        body += f'<text x="200" y="{y}" fill="{color}"{size} xml:space="preserve">{escape(value)}</text>'
        line(y, body)
        y += 34
    y += 12
    line(y, "".join(
        f'<rect x="{40 + n * 44}" y="{y - 16}" width="36" height="22" rx="4" fill="{c}"/>'
        for n, c in enumerate(SWATCHES)
    ))
    out.append("</svg>")
    (ROOT / "info-card.svg").write_text("\n".join(filter(None, out)) + "\n")
    print(f"info-card.svg (última línea en y={y}, alto {H})")


if __name__ == "__main__":
    main()
