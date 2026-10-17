#!/usr/bin/env python3
"""Generate the data-driven SVG cards for the profile README.

Writes (dark + light variants each) into assets/:
  stats-*.svg     contributions, commits, PRs, repos at a glance
  langs-*.svg     most-used languages across owned, non-fork repos
  activity-*.svg  weekly contributions over the last 12 months

Runs daily in GitHub Actions with GITHUB_TOKEN (GraphQL). Locally, pass a token:
    GITHUB_TOKEN=$(gh auth token) python scripts/generate_cards.py

Zero dependencies — stdlib only.
"""

import datetime as dt
import json
import os
import pathlib
import urllib.request

USERNAME = os.environ.get("GH_USERNAME", "aryanranade")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"
TOP_N = 6
# markup/config "languages" that distort a skills breakdown
IGNORED_LANGS = {"HTML", "CSS", "SCSS", "Dockerfile", "Makefile", "Procfile", "Batchfile"}

# Black cards, royal blue + crimson as solid accents, no gradients.
# Cards stay black in both GitHub themes. Keep in sync with scripts/build_assets.py.
INK = dict(bg="#07080B", border="#232836", text="#F5F7FA", muted="#8C93A3", track="#1A1E28",
           blue="#2563EB", blue_text="#5B9BFF", red="#DC2640", red_text="#FF4D67")
THEMES = {"dark": INK, "light": INK}
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace"
CARD_W, CARD_H, PAD = 408, 330, 24


# ---------------------------------------------------------------- data
def http_json(url: str, data: dict | None = None) -> dict:
    headers = {"User-Agent": f"{USERNAME}-profile-cards", "Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def collect_languages() -> list[tuple[str, float]]:
    repos = http_json(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner")
    totals: dict[str, int] = {}
    for repo in repos:
        if repo["fork"] or repo["name"] == USERNAME:  # skip forks and this profile repo
            continue
        langs = http_json(f"https://api.github.com/repos/{USERNAME}/{repo['name']}/languages")
        for lang, size in langs.items():
            if lang not in IGNORED_LANGS:
                totals[lang] = totals.get(lang, 0) + size
    grand = sum(totals.values()) or 1
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:TOP_N]
    return [(lang, size / grand * 100) for lang, size in ranked]


def collect_contributions() -> dict:
    if not TOKEN:
        raise SystemExit("GITHUB_TOKEN is required (GraphQL); try GITHUB_TOKEN=$(gh auth token)")
    query = """query($login: String!) { user(login: $login) {
        repositories(ownerAffiliations: OWNER, privacy: PUBLIC) { totalCount }
        contributionsCollection {
          totalCommitContributions
          totalPullRequestContributions
          totalRepositoriesWithContributedCommits
          contributionCalendar { totalContributions
            weeks { contributionDays { date contributionCount } } } } } }"""
    user = http_json("https://api.github.com/graphql",
                     {"query": query, "variables": {"login": USERNAME}})["data"]["user"]
    cc = user["contributionsCollection"]
    weeks = [(w["contributionDays"][0]["date"], sum(d["contributionCount"] for d in w["contributionDays"]))
             for w in cc["contributionCalendar"]["weeks"]]
    return {
        "contributions": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "contributed_to": cc["totalRepositoriesWithContributedCommits"],
        "repos": user["repositories"]["totalCount"],
        "weeks": weeks,
    }


# ---------------------------------------------------------------- rendering
def fade_in(delay: float) -> str:
    return f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{delay:.2f}s" fill="freeze"/>'


def card_shell(t: dict, title: str, body: str, w: int = CARD_W, h: int = CARD_H,
               bar: str = "blue", tip: str = "red") -> str:
    return f"""<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title.title()}">
  <defs><clipPath id="cc"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14"/></clipPath></defs>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="{t['bg']}"/>
  <g clip-path="url(#cc)">
    <rect x="0" y="0" width="{w}" height="5" fill="{t[bar]}"/>
    <rect x="{w - 64}" y="0" width="64" height="5" fill="{t[tip]}"/>
  </g>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" stroke="{t['border']}" stroke-width="1.5"/>
  <text x="{PAD}" y="38" font-family="{FONT}" font-size="12.5" font-weight="700" letter-spacing="2" fill="{t['text']}">{title}</text>
{body}
</svg>
"""


def render_stats(s: dict, t: dict) -> str:
    inner_w = CARD_W - 2 * PAD
    rows = []
    for i, (label, value) in enumerate([("COMMITS · LAST 12 MONTHS", s["commits"]),
                                        ("PULL REQUESTS", s["prs"]),
                                        ("REPOS CONTRIBUTED TO", s["contributed_to"]),
                                        ("PUBLIC REPOSITORIES", s["repos"])]):
        rows.append(f"""  <g transform="translate({PAD},{168 + i * 40})" opacity="0">
    {fade_in(0.5 + 0.15 * i)}
    <rect x="0" y="-10" width="3" height="14" rx="1.5" fill="{t['blue' if i % 2 == 0 else 'red']}"/>
    <text x="14" y="2" font-family="{FONT}" font-size="12.5" letter-spacing="1" fill="{t['muted']}">{label}</text>
    <text x="{inner_w}" y="2" text-anchor="end" font-family="{FONT}" font-size="16" font-weight="700" fill="{t['text']}">{value:,}</text>
    <rect x="0" y="16" width="{inner_w}" height="1" fill="{t['border']}" opacity="0.7"/>
  </g>""")
    body = f"""  <g opacity="0">
    {fade_in(0.1)}
    <text x="{PAD}" y="112" font-family="{FONT}" font-size="44" font-weight="800" fill="{t['blue_text']}">{s['contributions']:,}</text>
  </g>
  <text x="{PAD}" y="136" font-family="{FONT}" font-size="12.5" letter-spacing="2" fill="{t['muted']}">CONTRIBUTIONS · LAST 12 MONTHS</text>
{chr(10).join(rows)}"""
    return card_shell(t, "AT A GLANCE", body)


def render_langs(langs: list[tuple[str, float]], t: dict) -> str:
    bar_w = CARD_W - 2 * PAD
    top = max((pct for _, pct in langs), default=1)
    rows = []
    for i, (lang, pct) in enumerate(langs):
        fill_w = round(bar_w * pct / top, 1)
        rows.append(f"""  <g transform="translate({PAD},{60 + i * 42})" opacity="0">
    {fade_in(0.15 * i)}
    <text x="0" y="12" font-family="{FONT}" font-size="14" font-weight="600" fill="{t['text']}">{lang}</text>
    <text x="{bar_w}" y="12" text-anchor="end" font-family="{FONT}" font-size="13" fill="{t['muted']}">{pct:.1f}%</text>
    <rect x="0" y="20" width="{bar_w}" height="6" rx="3" fill="{t['track']}"/>
    <rect x="0" y="20" width="{fill_w}" height="6" rx="3" fill="{t['blue' if i % 2 == 0 else 'red']}">
      <animate attributeName="width" values="0;{fill_w}" dur="0.9s" begin="{0.15 * i:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.1 0.25 1"/>
    </rect>
  </g>""")
    return card_shell(t, "MOST USED LANGUAGES", "\n".join(rows), bar="red", tip="blue")


def render_activity(s: dict, t: dict) -> str:
    w, h = 832, 236
    weeks = s["weeks"]
    left, right, base, max_h = PAD, w - PAD, 182, 104
    step = (right - left) / len(weeks)
    bar_w = max(step - 4, 2)
    peak = max((c for _, c in weeks), default=0) or 1
    bars, labels, last_month = [], [], None
    for i, (start, count) in enumerate(weeks):
        x = left + i * step + (step - bar_w) / 2
        bh = max(count / peak * max_h, 2 if count else 0)
        if bh:
            bars.append(f'  <rect x="{x:.1f}" y="{base - bh:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" rx="2" '
                        f'fill="{t["red"] if count == peak else t["blue"]}" opacity="{1 if count == peak else 0.45 + 0.55 * count / peak:.2f}">'
                        f'<animate attributeName="height" values="0;{bh:.1f}" dur="0.6s" begin="{0.02 * i:.2f}s" fill="freeze"/>'
                        f'<animate attributeName="y" values="{base};{base - bh:.1f}" dur="0.6s" begin="{0.02 * i:.2f}s" fill="freeze"/></rect>')
        else:
            bars.append(f'  <rect x="{x:.1f}" y="{base - 2}" width="{bar_w:.1f}" height="2" rx="1" fill="{t["track"]}"/>')
        month = dt.date.fromisoformat(start).strftime("%b")
        if month != last_month and i < len(weeks) - 2:
            labels.append(f'  <text x="{x:.1f}" y="{base + 20}" font-family="{MONO}" font-size="10.5" fill="{t["muted"]}">{month}</text>')
            last_month = month
    best = max(weeks, key=lambda wk: wk[1]) if weeks else ("", 0)
    summary = (f'<text x="{right}" y="36" text-anchor="end" font-family="{FONT}" font-size="12.5" fill="{t["muted"]}">'
               f'<tspan fill="{t["text"]}" font-weight="700">{s["contributions"]:,}</tspan> contributions · '
               f'best week <tspan fill="{t["red_text"]}" font-weight="700">{best[1]}</tspan></text>')
    body = "\n".join([f"  {summary}",
                      f'  <rect x="{left}" y="{base}" width="{right - left}" height="1" fill="{t["border"]}"/>',
                      *bars, *labels])
    return card_shell(t, "WEEKLY ACTIVITY · LAST 12 MONTHS", body, w, h)


def main() -> None:
    langs = collect_languages()
    contrib = collect_contributions()
    if not langs:
        raise SystemExit("no language data returned; refusing to write empty cards")
    for mode, t in THEMES.items():
        for kind, svg in (("stats", render_stats(contrib, t)),
                          ("langs", render_langs(langs, t)),
                          ("activity", render_activity(contrib, t))):
            path = ASSETS / f"{kind}-{mode}.svg"
            path.write_text(svg)
            print(f"wrote {path.relative_to(ASSETS.parent)}")
    print("stats:", {k: v for k, v in contrib.items() if k != "weeks"}, "| langs:", [l for l, _ in langs])


if __name__ == "__main__":
    main()
