#!/usr/bin/env python3
"""Generate the themed dynamic SVG cards (top languages + GitHub analytics).

Runs in GitHub Actions (GITHUB_TOKEN provided → GraphQL) or locally
(unauthenticated → REST + streak-stats fallback). Writes:
  assets/langs-dark.svg / langs-light.svg
  assets/stats-dark.svg / stats-light.svg

Zero dependencies — stdlib only.
"""

import json
import os
import urllib.request

USERNAME = os.environ.get("GH_USERNAME", "aryanranade")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
TOP_N = 6
W, H, PAD = 408, 330, 24

# Design tokens — keep in sync with assets/hero-*.svg
THEMES = {
    "dark": dict(bg="#0D1117", border="#21262D", text="#E6EDF3", muted="#8B949E",
                 track="#21262D", teal="#2DD4BF", violet="#8B5CF6"),
    "light": dict(bg="#FFFFFF", border="#D0D7DE", text="#1F2328", muted="#57606A",
                  track="#EAEEF2", teal="#0D9488", violet="#7C3AED"),
}

FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def http_json(url: str, data: dict | None = None, headers: dict | None = None):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                                 headers={"User-Agent": f"{USERNAME}-profile-cards", **(headers or {})})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def api(path: str):
    headers = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    return http_json(f"https://api.github.com{path}", headers=headers)


# ---------------------------------------------------------------- data
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


def collect_stats() -> dict:
    user = api(f"/users/{USERNAME}")
    stats = {"repos": user["public_repos"], "followers": user["followers"]}
    if TOKEN:
        q = """query($login:String!){ user(login:$login){
            contributionsCollection{
              contributionCalendar{ totalContributions }
              totalCommitContributions
              totalPullRequestContributions }}}"""
        r = http_json("https://api.github.com/graphql",
                      data={"query": q, "variables": {"login": USERNAME}},
                      headers={"Authorization": f"Bearer {TOKEN}",
                               "Content-Type": "application/json"})
        cc = r["data"]["user"]["contributionsCollection"]
        stats["contributions"] = cc["contributionCalendar"]["totalContributions"]
        stats["commits"] = cc["totalCommitContributions"]
        stats["prs"] = cc["totalPullRequestContributions"]
    else:  # local fallback, no token
        streak = http_json(f"https://streak-stats.demolab.com/?user={USERNAME}&type=json")
        stats["contributions"] = streak["totalContributions"]
        search = {"Accept": "application/vnd.github+json"}
        stats["commits"] = http_json(
            f"https://api.github.com/search/commits?q=author:{USERNAME}", headers=search)["total_count"]
        stats["prs"] = http_json(
            f"https://api.github.com/search/issues?q=author:{USERNAME}+type:pr", headers=search)["total_count"]
    return stats


# ---------------------------------------------------------------- rendering
def card_shell(t: dict, title: str, body: str) -> str:
    return f"""<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title}">
  <defs>
    <linearGradient id="acc" x1="0" y1="0" x2="1" y2="0.25">
      <stop offset="0%" stop-color="{t['teal']}"/><stop offset="100%" stop-color="{t['violet']}"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{t['bg']}" stroke="{t['border']}" stroke-width="1.5"/>
  <text x="{PAD}" y="36" font-family="{FONT}" font-size="13" font-weight="600" letter-spacing="2" fill="{t['muted']}">{title}</text>
  <rect x="{PAD}" y="44" width="34" height="2" fill="url(#acc)"/>
{body}
</svg>
"""


def render_langs(langs: list[tuple[str, float]], t: dict) -> str:
    bar_w = W - 2 * PAD
    max_pct = max((pct for _, pct in langs), default=1)
    rows = []
    for i, (lang, pct) in enumerate(langs):
        y = 58 + i * 42
        opacity = 1.0 - i * 0.13
        fill_w = round(bar_w * pct / max_pct, 1)
        rows.append(f"""  <g transform="translate({PAD},{y})">
    <text x="0" y="12" font-family="{FONT}" font-size="14" font-weight="600" fill="{t['text']}">{lang}</text>
    <text x="{bar_w}" y="12" text-anchor="end" font-family="{FONT}" font-size="13" fill="{t['muted']}">{pct:.1f}%</text>
    <rect x="0" y="20" width="{bar_w}" height="6" rx="3" fill="{t['track']}"/>
    <rect x="0" y="20" width="{fill_w}" height="6" rx="3" fill="{t['teal']}" opacity="{opacity:.2f}">
      <animate attributeName="width" dur="0.9s" begin="0s" fill="freeze" calcMode="spline" keySplines="0.25 0.1 0.25 1" keyTimes="0;1" values="0;{fill_w}"/>
    </rect>
  </g>""")
    return card_shell(t, "MOST USED LANGUAGES", "\n".join(rows))


def render_stats(s: dict, t: dict) -> str:
    inner_w = W - 2 * PAD
    rows_def = [("COMMITS · LAST YEAR", s["commits"], "teal"),
                ("PULL REQUESTS", s["prs"], "violet"),
                ("PUBLIC REPOSITORIES", s["repos"], "teal"),
                ("FOLLOWERS", s["followers"], "violet")]
    rows = []
    for i, (label, value, color) in enumerate(rows_def):
        y = 168 + i * 40
        rows.append(f"""  <g transform="translate({PAD},{y})">
    <rect x="0" y="-10" width="3" height="14" rx="1.5" fill="{t[color]}"/>
    <text x="14" y="2" font-family="{FONT}" font-size="12.5" letter-spacing="1" fill="{t['muted']}">{label}</text>
    <text x="{inner_w}" y="2" text-anchor="end" font-family="{FONT}" font-size="16" font-weight="700" fill="{t['text']}">{value:,}</text>
    <rect x="0" y="16" width="{inner_w}" height="1" fill="{t['border']}" opacity="0.6"/>
  </g>""")
    body = f"""  <text x="{PAD}" y="114" font-family="{FONT}" font-size="44" font-weight="800" fill="url(#acc)">{s['contributions']:,}</text>
  <text x="{PAD}" y="138" font-family="{FONT}" font-size="12.5" letter-spacing="2" fill="{t['muted']}">CONTRIBUTIONS · LAST YEAR</text>
{chr(10).join(rows)}"""
    return card_shell(t, "GITHUB ANALYTICS", body)


def main() -> None:
    langs = collect_languages()
    stats = collect_stats()
    if not langs:
        raise SystemExit("no language data returned; refusing to write empty cards")
    os.makedirs("assets", exist_ok=True)
    for name, t in THEMES.items():
        for kind, svg in (("langs", render_langs(langs, t)), ("stats", render_stats(stats, t))):
            path = f"assets/{kind}-{name}.svg"
            with open(path, "w") as f:
                f.write(svg)
            print(f"wrote {path}")
    print("stats:", stats)


if __name__ == "__main__":
    main()
