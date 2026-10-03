"""Sprite 8-bit animado (pixel-portrait.svg): personaje dibujado a mano tecleando en un portátil.

Edita SPRITE para retocar el dibujo: cada carácter es un píxel (ver PALETTE).
El sprite se pinta fila a fila una vez; después parpadea, teclea y salen chispas de código.
STATIC=1 emite un fotograma fijo (para previsualizar en local).
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CELL = 24
MARGIN = 2          # celdas libres alrededor del sprite
ROW_DELAY = 0.05
STATIC = os.environ.get("STATIC") == "1"

BG, TILE = "#0d1117", "#0e4429"
PALETTE = {
    "K": "#010409",  # contorno
    "H": "#3b2a1e", "h": "#5c4130",   # pelo
    "S": "#eebf95", "s": "#d99f73",   # piel y sombra
    "E": "#1b1410",                   # ojos
    "M": "#c9736b",                   # boca
    "G": "#b1b8c0", "g": "#8b939c",   # sudadera gris y sombra
    "W": "#f0f6fc",                   # cordones
    "T": "#15181d",                   # camiseta
    "L": "#57606a", "l": "#8c959f",   # tapa del portátil y brillo
    "D": "#30363d", "d": "#21262d",   # mesa
}
SPRITE = """
........KKKKKKKK........
......KKHHHHHHHHKK......
....KKHHHhhHHHHHHHKK....
...KHHHhhHHHHHHHHHHHK...
..KHHHHHHHHHHHHHhHHHHK..
..KHHHHHHHHHHHHHHHHHHK..
..KHHHHHHHHHHHHHHHHHHK..
..KHHHHHHHHHHHHHHHHHHK..
.KHHHhHHHHHHHHHHHHhHHHK.
.KHHHHHHHHHHHHHHHHHHHHK.
.KHHHHHSHHHHSSHHHSHHHHK.
.KHHHSSSSHSSSSSSSSSHHHK.
.KHHSSSSSSSSSSSSSSSSHHK.
KKHHSSSEESSSSSSEESSSHHKK
KSKHSSSEESSSSSSEESSSHKSK
KSKKSSSSSSSSSSSSSSSSKKSK
.KKKSSsSSSSSSSSSSsSSKKK.
...KSSSSSSSMMSSSSSSSK...
....KSSSSSSSSSSSSSSK....
.....KKSSSSSSSSSSKK.....
...KKKGgKSSSSSSKgGKKK...
..KGGGGGgWTTTTWgGGGGGK..
.KGGGGGGGWgTTgWGGGGGGGK.
.KGGGGKKKKKKKKKKKKGGGGK.
.KGGGGKLLLLLLLLLLKGGGGK.
.KGGgGKLlLLLLLLLLKGgGGK.
.KGGgGKLLLLLLLLLLKGgGGK.
.KKKKKKLLLLLLLLLLKKKKKK.
......KLLLLLLLLLLK......
KKKKKKKKKKKKKKKKKKKKKKKK
DDDDDDDDDDDDDDDDDDDDDDDD
dddddddddddddddddddddddd
""".strip().splitlines()
COLS, ROWS = len(SPRITE[0]), len(SPRITE)
assert all(len(r) == COLS for r in SPRITE), [len(r) for r in SPRITE]
SIDE = max(COLS, ROWS) + MARGIN * 2
SIZE = SIDE * CELL
OX, OY = (SIDE - COLS) // 2, (SIDE - ROWS) // 2

EYES = [(7, 13), (15, 13)]            # esquina superior izquierda de cada ojo (2x2)
HANDS = [(1, 27), (18, 27)]           # manos (4x2) a los lados del portátil
SPARKS = [(-1, 0, "#39d353"), (24, -1, "#58a6ff"), (-1, -3, "#ffa657"), (24, 2, "#39d353")]  # a los lados, relativo a la tapa


def rect(x, y, w, h, fill, extra="", body=""):
    attrs = (f'x="{(OX + x) * CELL}" y="{(OY + y) * CELL}" width="{w * CELL}" '
             f'height="{h * CELL}" fill="{fill}"{extra}')
    return f"<rect {attrs}>{body}</rect>" if body else f"<rect {attrs}/>"


def main() -> None:
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" '
        f'width="{SIZE}" height="{SIZE}" shape-rendering="crispEdges">',
        f'<rect width="{SIZE}" height="{SIZE}" rx="24" fill="{BG}"/>',
        f'<rect x="{CELL}" y="{CELL}" width="{SIZE - 2 * CELL}" height="{SIZE - 2 * CELL}" rx="18" fill="{TILE}"/>',
    ]

    # 1) Sprite fijo: se enciende fila a fila
    for y, row in enumerate(SPRITE):
        runs, x = [], 0
        while x < COLS:
            ch, start = row[x], x
            while x < COLS and row[x] == ch:
                x += 1
            if ch != ".":
                runs.append(rect(start, y, x - start, 1, PALETTE[ch]))
        hide = "" if STATIC else ' opacity="0"'
        anim = "" if STATIC else f'<set attributeName="opacity" to="1" begin="{y * ROW_DELAY:.2f}s" fill="freeze"/>'
        out.append(f"<g{hide}>{anim}{''.join(runs)}</g>")
    done = round(ROWS * ROW_DELAY + 0.2, 2)

    # 2) Capa viva: aparece al terminar el barrido
    live = []
    for ex, ey in EYES:  # parpadeo: un párpado de piel tapa el ojo un instante
        blink = "" if STATIC else (
            '<animate attributeName="opacity" values="0;0;1;0" keyTimes="0;0.93;0.95;1" '
            f'calcMode="discrete" dur="3.8s" begin="{done}s" repeatCount="indefinite"/>')
        live.append(rect(ex, ey, 2, 2, PALETTE["s"], ' opacity="0"', blink))
    for n, (hx, hy) in enumerate(HANDS):  # manos que suben y bajan alternándose
        tap = "" if STATIC else (
            f'<animateTransform attributeName="transform" type="translate" values="0 0;0 {-CELL};0 0" '
            f'keyTimes="0;0.5;1" calcMode="discrete" dur="0.4s" begin="{done + n * 0.2:.2f}s" repeatCount="indefinite"/>')
        live.append(f'<g>{tap}{rect(hx, hy, 5, 1, PALETTE["K"])}{rect(hx, hy + 1, 5, 1, PALETTE["S"])}'
                    f'{rect(hx + (0 if n else 4), hy + 1, 1, 1, PALETTE["s"])}</g>')
    for n, (sx, dy, color) in enumerate(SPARKS):  # chispas de código que suben desde el portátil
        if STATIC:
            continue
        y0 = (OY + 23 + dy) * CELL
        live.append(rect(
            sx, 23 + dy, 1, 1, color, ' opacity="0"',
            f'<animate attributeName="y" values="{y0};{y0 - 3 * CELL}" dur="1.8s" begin="{done + n * 0.6:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;0" dur="1.8s" begin="{done + n * 0.6:.2f}s" repeatCount="indefinite"/>'))
    hide = "" if STATIC else ' opacity="0"'
    appear = "" if STATIC else f'<set attributeName="opacity" to="1" begin="{done}s" fill="freeze"/>'
    out.append(f"<g{hide}>{appear}{''.join(live)}</g>")
    out.append("</svg>")
    (ROOT / "pixel-portrait.svg").write_text("\n".join(out) + "\n")
    print(f"pixel-portrait.svg ({COLS}x{ROWS} px, lienzo {SIZE}, barrido {done}s)")


if __name__ == "__main__":
    main()
