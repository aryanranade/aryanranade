#!/usr/bin/env python3
"""Build the static SVG assets for the profile README.

Generates hero, section headers, project cards, connect buttons and the divider
(dark + light variants each) into assets/. Run from the repo root:

    python scripts/build_assets.py

Dynamic, data-driven cards (stats, languages, activity) come from
scripts/generate_cards.py instead. Zero dependencies — stdlib only.
"""

import pathlib
from html import escape

ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace"

# Single-accent theme — keep in sync with scripts/generate_cards.py
THEMES = {
    "dark": dict(bg="#0D1117", surface="#161B22", border="#30363D", text="#E6EDF3",
                 muted="#8B949E", accent="#2DD4BF"),
    "light": dict(bg="#FFFFFF", surface="#F6F8FA", border="#D0D7DE", text="#1F2328",
                  muted="#57606A", accent="#0D9488"),
}


# ---------------------------------------------------------------- hero
def hero(t: dict) -> str:
    w, h = 1012, 250
    wave = "q55,-14 110,0 " + "t110,0 " * 11
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Aryan Ranade — AI/ML Engineer, Computer Science Student">
  <defs>
    <clipPath id="card"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="16"/></clipPath>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0%" stop-color="{t['accent']}" stop-opacity="0.13"/>
      <stop offset="100%" stop-color="{t['accent']}" stop-opacity="0"/>
    </radialGradient>
    <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="1.5" cy="1.5" r="1.1" fill="{t['muted']}" opacity="0.16"/>
    </pattern>
  </defs>

  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="16" fill="{t['bg']}"/>
  <g clip-path="url(#card)">
    <rect width="{w}" height="{h}" fill="url(#dots)"/>
    <circle cx="890" cy="10" r="320" fill="url(#glow)">
      <animate attributeName="opacity" values="1;0.6;1" dur="8s" repeatCount="indefinite"/>
    </circle>
    <path d="M0,206 {wave}" stroke="{t['accent']}" stroke-opacity="0.32" stroke-width="1.4">
      <animateTransform attributeName="transform" type="translate" from="0 0" to="-220 0" dur="18s" repeatCount="indefinite"/>
    </path>
    <path d="M0,222 {wave}" stroke="{t['accent']}" stroke-opacity="0.16" stroke-width="1.4">
      <animateTransform attributeName="transform" type="translate" from="-220 0" to="0 0" dur="24s" repeatCount="indefinite"/>
    </path>
  </g>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="16" stroke="{t['border']}" stroke-width="1.5"/>

  <text x="30" y="44" font-family="{MONO}" font-size="13" fill="{t['muted']}"><tspan fill="{t['accent']}">~</tspan>/aryanranade <tspan fill="{t['accent']}">$</tspan></text>
  <g transform="translate(756,24)">
    <rect width="230" height="30" rx="15" fill="{t['surface']}" stroke="{t['border']}"/>
    <circle cx="18" cy="15" r="4" fill="{t['accent']}">
      <animate attributeName="opacity" values="1;0.25;1" dur="2s" repeatCount="indefinite"/>
    </circle>
    <text x="30" y="19.5" font-family="{MONO}" font-size="11" letter-spacing="1" fill="{t['muted']}">OPEN TO AI/ML INTERNSHIPS</text>
  </g>

  <text x="{w // 2}" y="122" text-anchor="middle" font-family="{FONT}" font-size="50" font-weight="800" letter-spacing="0.5" fill="{t['text']}">Aryan Ranade</text>
  <rect x="{w // 2 - 32}" y="142" width="64" height="2.5" rx="1.25" fill="{t['accent']}"/>
  <text x="{w // 2}" y="176" text-anchor="middle" font-family="{FONT}" font-size="16" font-weight="500" letter-spacing="2.5" fill="{t['muted']}">AI/ML ENGINEER<tspan fill="{t['accent']}" dx="10">·</tspan><tspan dx="10">COMPUTER SCIENCE STUDENT</tspan></text>
</svg>
'''


# ---------------------------------------------------------------- section headers
SECTIONS = [
    ("about", "ABOUT"),
    ("projects", "FEATURED PROJECTS"),
    ("more", "MORE PROJECTS"),
    ("stack", "TECH STACK"),
    ("analytics", "GITHUB ANALYTICS"),
    ("connect", "CONNECT"),
]


def header(index: int, title: str, t: dict) -> str:
    w, h, base = 1012, 46, 30
    # approximate rendered width: bold 15px caps + 3px tracking
    line_x = round(30 + 34 + len(title) * 13.4 + 18)
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title.title()}">
  <defs>
    <linearGradient id="glint" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{t['accent']}" stop-opacity="0"/>
      <stop offset="50%" stop-color="{t['accent']}" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="{t['accent']}" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="track"><rect x="{line_x}" y="{base - 7}" width="{w - line_x}" height="3"/></clipPath>
  </defs>
  <rect x="2" y="{base - 15}" width="3" height="18" rx="1.5" fill="{t['accent']}"/>
  <text x="16" y="{base}" font-family="{MONO}" font-size="13" font-weight="600" fill="{t['accent']}">{index:02d}</text>
  <text x="{30 + 34}" y="{base}" font-family="{FONT}" font-size="15" font-weight="700" letter-spacing="3" fill="{t['text']}">{escape(title)}</text>
  <rect x="{line_x}" y="{base - 6}" width="{w - line_x}" height="1" fill="{t['border']}"/>
  <g clip-path="url(#track)">
    <rect x="{line_x - 140}" y="{base - 7}" width="120" height="3" fill="url(#glint)">
      <animateTransform attributeName="transform" type="translate" from="0 0" to="{w - line_x + 160} 0" dur="6s" repeatCount="indefinite"/>
    </rect>
  </g>
</svg>
'''


# ---------------------------------------------------------------- project cards
PROJECTS = [
    dict(slug="autonomous-issue-resolver", name="autonomous-issue-resolver",
         kicker="AUTONOMOUS AGENTS",
         desc=["Coding agent that plans, edits and tests fixes for",
               "real GitHub issues inside per-task Docker sandboxes,",
               "with a provider-agnostic LLM layer."],
         metric="Graded by the official SWE-bench harness",
         tech="Python · Docker · SWE-bench · Groq · Gemini"),
    dict(slug="ledgerloop", name="ledgerloop",
         kicker="AI FINANCE · RAZORPAY AI BUILDATHON",
         desc=["Three-way settlement reconciliation agent: a",
               "deterministic matching cascade, a bounded LLM",
               "adjudicator and a deterministic verifier."],
         metric="98.3% precision on held-out bench",
         tech="Python · FastAPI · Groq · DuckDB · Next.js"),
    dict(slug="TBSentinel", name="TBSentinel",
         kicker="MEDICAL IMAGING · EXPLAINABLE AI",
         desc=["Tuberculosis screening from chest X-rays — fine-tuned",
               "ResNet18, sensitivity-tuned thresholds, cross-hospital",
               "generalization testing and Grad-CAM heatmaps."],
         metric="0.896 ROC-AUC on held-out test set",
         tech="PyTorch · timm · Grad-CAM · scikit-learn · Gradio"),
    dict(slug="Development-of-AI-Based-Knowledge-Retrieval-Platform-with-Query-Resolution-System",
         name="knowledge-retrieval-platform", kicker="AGENTIC RAG",
         desc=["Document Q&amp;A platform built on a two-level LangGraph",
               "agent over a ChromaDB vector store, with JWT auth,",
               "conversation memory and query analytics."],
         metric="Two-level agentic RAG pipeline",
         tech="FastAPI · LangGraph · ChromaDB · Ollama · Streamlit"),
    dict(slug="finance-tracker", name="finance-tracker",
         kicker="FULL-STACK · LLM",
         desc=["Personal finance tracker with Groq Llama 3.3 insights,",
               "natural-language auto-categorization, budgets and a",
               "financial health score."],
         metric="Live on Vercel",
         tech="React · Express · MongoDB · Groq · Tailwind"),
    dict(slug="horizon-dashboard", name="horizon-dashboard",
         kicker="GENERATIVE AI · WEB",
         desc=["Travel planner that turns a prompt into multi-day",
               "itineraries, budget breakdowns and weather-aware",
               "packing lists."],
         metric="Live on Vercel",
         tech="Next.js · TypeScript · Gemini API · Tailwind"),
]


def project_card(p: dict, t: dict) -> str:
    w, h, pad = 408, 222, 24
    pill_w = round(len(p["metric"]) * 7.1 + 30)
    desc = "\n".join(
        f'  <text x="{pad}" y="{96 + i * 19}" font-family="{FONT}" font-size="13" fill="{t["muted"]}">{line}</text>'
        for i, line in enumerate(p["desc"]))
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{p['name']}">
  <defs><clipPath id="cc"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14"/></clipPath></defs>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="{t['bg']}"/>
  <rect x="1" y="1" width="3" height="{h - 2}" fill="{t['accent']}" clip-path="url(#cc)"/>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" stroke="{t['border']}" stroke-width="1.5"/>
  <text x="{pad}" y="34" font-family="{MONO}" font-size="10.5" font-weight="600" letter-spacing="1.4" fill="{t['accent']}">{p['kicker']}</text>
  <text x="{pad}" y="62" font-family="{MONO}" font-size="17" font-weight="700" fill="{t['text']}">{p['name']}</text>
  <g transform="translate({w - 42},22)" stroke="{t['muted']}" stroke-width="1.7" stroke-linecap="round" fill="none">
    <path d="M4 14 L14 4 M6 4 H14 V12">
      <animateTransform attributeName="transform" type="translate" values="0 0;2 -2;0 0" dur="2.8s" repeatCount="indefinite"/>
    </path>
  </g>
{desc}
  <rect x="{pad}" y="148" width="{pill_w}" height="24" rx="12" fill="{t['accent']}" fill-opacity="0.1" stroke="{t['accent']}" stroke-opacity="0.45"/>
  <circle cx="{pad + 13}" cy="160" r="3" fill="{t['accent']}"/>
  <text x="{pad + 23}" y="164" font-family="{MONO}" font-size="11.5" font-weight="600" fill="{t['accent']}">{p['metric']}</text>
  <rect x="{pad}" y="186" width="{w - 2 * pad}" height="1" fill="{t['border']}"/>
  <text x="{pad}" y="206" font-family="{MONO}" font-size="11" fill="{t['muted']}">{p['tech']}</text>
</svg>
'''


# ---------------------------------------------------------------- connect buttons
BUTTONS = [
    dict(slug="email", label="EMAIL",
         icon='<rect x="2" y="4" width="20" height="16" rx="2.5"/><path d="M2.5 6.5 12 13.5 21.5 6.5"/>'),
    dict(slug="linkedin", label="LINKEDIN",
         icon='<rect x="2.5" y="2.5" width="19" height="19" rx="4"/>'
              '<path d="M7.5 10.5 V17 M7.5 7.2 V7.4 M11.5 17 V12.8 Q11.5 10.5 13.8 10.5 T16.2 12.8 V17"/>'),
    dict(slug="portfolio", label="PORTFOLIO",
         icon='<circle cx="12" cy="12" r="9.5"/><ellipse cx="12" cy="12" rx="4.2" ry="9.5"/><path d="M2.5 12 H21.5"/>'),
]


def connect_button(b: dict, t: dict) -> str:
    w, h = 236, 52
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{b['label'].title()}">
  <defs>
    <linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{t['accent']}" stop-opacity="0"/>
      <stop offset="50%" stop-color="{t['accent']}" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="{t['accent']}" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="bc"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="12"/></clipPath>
  </defs>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="12" fill="{t['surface']}"/>
  <g clip-path="url(#bc)">
    <rect x="-80" y="0" width="70" height="{h}" fill="url(#sheen)">
      <animateTransform attributeName="transform" type="translate" from="0 0" to="{w + 160} 0" dur="4.5s" repeatCount="indefinite"/>
    </rect>
  </g>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="12" stroke="{t['border']}" stroke-width="1.5"/>
  <g transform="translate(24,14)" stroke="{t['accent']}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" fill="none">{b['icon']}</g>
  <text x="{(w + 40) // 2}" y="{h // 2 + 5}" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="700" letter-spacing="2.5" fill="{t['text']}">{b['label']}</text>
</svg>
'''


# ---------------------------------------------------------------- divider
def divider(t: dict) -> str:
    return f'''<svg width="1012" height="4" viewBox="0 0 1012 4" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <rect x="0" y="1.5" width="1012" height="1" fill="{t['border']}"/>
</svg>
'''


def main() -> None:
    keep = {"stats", "langs", "activity"}  # owned by generate_cards.py
    for old in ASSETS.glob("*.svg"):
        if old.stem.rsplit("-", 1)[0] not in keep:
            old.unlink()
    written = 0
    for mode, t in THEMES.items():
        files = {f"hero-{mode}.svg": hero(t), f"divider-{mode}.svg": divider(t)}
        for i, (slug, title) in enumerate(SECTIONS, start=1):
            files[f"h-{slug}-{mode}.svg"] = header(i, title, t)
        for p in PROJECTS:
            files[f"p-{p['name']}-{mode}.svg"] = project_card(p, t)
        for b in BUTTONS:
            files[f"c-{b['slug']}-{mode}.svg"] = connect_button(b, t)
        for name, svg in files.items():
            (ASSETS / name).write_text(svg)
            written += 1
    print(f"wrote {written} static assets to {ASSETS}")


if __name__ == "__main__":
    main()
