#!/usr/bin/env python3
"""Generate themed top-languages SVG cards from the GitHub API.

Runs in GitHub Actions (GITHUB_TOKEN provided) or locally (unauthenticated,
subject to rate limits). Writes assets/langs-dark.svg and assets/langs-light.svg.

Zero dependencies — stdlib only.
"""

import json
import os
import urllib.request

USERNAME = os.environ.get("GH_USERNAME", "aryanranade")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
TOP_N = 6

# Design tokens — keep in sync with assets/hero-*.svg
THEMES = {
    "dark": {
        "bg": "#0D1117",
        "border": "#21262D",
        "title": "#E6EDF3",
        "text": "#E6EDF3",
        "muted": "#8B949E",
        "track": "#21262D",
        "accent": "#2DD4BF",
    },
    "light": {
        "bg": "#FFFFFF",
        "border": "#D0D7DE",
        "title": "#1F2328",
        "text": "#1F2328",
        "muted": "#57606A",
        "track": "#EAEEF2",
        "accent": "#0D9488",
    },
}

FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def api(path: str):
    req = urllib.request.Request(f"https://api.github.com{path}")
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def collect_languages() -> list[tuple[str, float]]:
    repos = api(f"/users/{USERNAME}/repos?per_page=100&type=owner")
    totals: dict[str, int] = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        for lang, size in api(f"/repos/{USERNAME}/{repo['name']}/languages").items():
            totals[lang] = totals.get(lang, 0) + size
    grand = sum(totals.values()) or 1
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:TOP_N]
    return [(lang, size / grand * 100) for lang, size in ranked]


def render(langs: list[tuple[str, float]], theme: dict) -> str:
    width, pad, row_h = 494, 28, 42
    header_h = 58
    height = header_h + len(langs) * row_h + pad - 8
    bar_w = width - 2 * pad
    max_pct = max((pct for _, pct in langs), default=1)

    rows = []
    for i, (lang, pct) in enumerate(langs):
        y = header_h + i * row_h
        opacity = 1.0 - i * 0.13
        fill_w = round(bar_w * pct / max_pct, 1)
        rows.append(f"""  <g transform="translate({pad},{y})">
    <text x="0" y="12" font-family="{FONT}" font-size="14" font-weight="600" fill="{theme['text']}">{lang}</text>
    <text x="{bar_w}" y="12" text-anchor="end" font-family="{FONT}" font-size="13" fill="{theme['muted']}">{pct:.1f}%</text>
    <rect x="0" y="20" width="{bar_w}" height="6" rx="3" fill="{theme['track']}"/>
    <rect x="0" y="20" width="{fill_w}" height="6" rx="3" fill="{theme['accent']}" opacity="{opacity:.2f}">
      <animate attributeName="width" from="0" to="{fill_w}" dur="0.9s" begin="0s" fill="freeze" calcMode="spline" keySplines="0.25 0.1 0.25 1" keyTimes="0;1" values="0;{fill_w}"/>
    </rect>
  </g>""")

    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Most used languages">
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14" fill="{theme['bg']}" stroke="{theme['border']}" stroke-width="1.5"/>
  <text x="{pad}" y="36" font-family="{FONT}" font-size="14" font-weight="600" letter-spacing="2" fill="{theme['muted']}">MOST USED LANGUAGES</text>
  <rect x="{pad}" y="44" width="34" height="2" fill="{theme['accent']}"/>
{chr(10).join(rows)}
</svg>
"""


def main() -> None:
    langs = collect_languages()
    if not langs:
        raise SystemExit("no language data returned; refusing to write empty cards")
    os.makedirs("assets", exist_ok=True)
    for name, theme in THEMES.items():
        path = f"assets/langs-{name}.svg"
        with open(path, "w") as f:
            f.write(render(langs, theme))
        print(f"wrote {path}")
    for lang, pct in langs:
        print(f"  {lang:15} {pct:5.1f}%")


if __name__ == "__main__":
    main()
