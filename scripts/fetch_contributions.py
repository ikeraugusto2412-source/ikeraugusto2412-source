"""Descarga el calendario público de contribuciones (sin token) a data/contributions.json."""
import json
import os
import re
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
USER = os.environ.get("GH_USER", "ikeraugusto2412-source")
URL = f"https://github.com/users/{USER}/contributions"


def fetch_days() -> list[dict]:
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-heatmap"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    # El número exacto solo aparece en el tooltip asociado a cada celda
    counts = {}
    for tip in soup.find_all("tool-tip"):
        m = re.match(r"\s*(\d[\d,]*) contribution", tip.get_text())
        counts[tip.get("for")] = int(m.group(1).replace(",", "")) if m else 0
    days = [
        {
            "date": cell["data-date"],
            "level": int(cell.get("data-level", 0)),
            "count": counts.get(cell.get("id"), 0),
        }
        for cell in soup.select("td.ContributionCalendar-day[data-date]")
    ]
    if not days:
        raise SystemExit("No se encontraron celdas: ¿ha cambiado el HTML de GitHub?")
    return sorted(days, key=lambda d: d["date"])


def streaks(days: list[dict]) -> tuple[int, int]:
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    # La racha actual no se rompe por un "hoy" todavía sin contribuciones
    past = [d for d in days if d["date"] <= date.today().isoformat()]
    if past and not past[-1]["count"]:
        past = past[:-1]
    current = 0
    for d in reversed(past):
        if not d["count"]:
            break
        current += 1
    return current, longest


def main() -> None:
    days = fetch_days()
    current, longest = streaks(days)
    best = max(days, key=lambda d: d["count"])
    monthly: dict[str, int] = {}
    for d in days:
        monthly[d["date"][:7]] = monthly.get(d["date"][:7], 0) + d["count"]
    data = {
        "user": USER,
        "total": sum(d["count"] for d in days),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": monthly,
        "days": days,
    }
    out = ROOT / "data" / "contributions.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, indent=1) + "\n")
    print(f"{data['total']} contribuciones, {len(days)} días -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
