#!/usr/bin/env python3
"""Build the static SVG assets for the profile README.

Generates hero, section headers, project cards, connect buttons and the divider
(dark + light variants each) into assets/. Run from the repo root:

    python scripts/build_assets.py

Dynamic, data-driven cards (stats, languages, activity) come from
scripts/generate_cards.py instead. Zero dependencies — stdlib only.

Design rule: one solid accent colour, no gradients anywhere.
"""

import pathlib
from html import escape

ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace"

# Single solid accent — keep in sync with scripts/generate_cards.py.
# accent: fills, bars, large type · accent_text: small text (contrast-safe) · on_accent: text on accent fills
THEMES = {
    "dark": dict(bg="#0D1117", surface="#161B22", border="#30363D", text="#F0F6FC",
                 muted="#9198A1", accent="#FB923C", accent_text="#FB923C", on_accent="#0D1117"),
    "light": dict(bg="#FFFFFF", surface="#F6F8FA", border="#D1D9E0", text="#1F2328",
                  muted="#59636E", accent="#EA580C", accent_text="#C2410C", on_accent="#FFFFFF"),
}


# ---------------------------------------------------------------- hero
def network(t: dict, ox: int, oy: int) -> str:
    """Small feed-forward network with signals travelling along its edges."""
    layers = [[40, 100, 160], [10, 70, 130, 190], [55, 145]]
    xs = [0, 120, 240]
    nodes = [[(xs[i] + ox, y + oy) for y in col] for i, col in enumerate(layers)]
    edges = [(a, b) for i in range(len(nodes) - 1) for a in nodes[i] for b in nodes[i + 1]]
    lines = "\n".join(
        f'    <line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{t["border"]}" stroke-width="1.2"/>'
        for a, b in edges)
    # a few signal paths: input -> hidden -> output, staggered
    routes = [(0, 1, 0), (1, 2, 1), (2, 3, 1), (0, 0, 0), (1, 1, 1), (2, 2, 0)]
    signals = []
    for k, (i, h, o) in enumerate(routes):
        a, b, c = nodes[0][i], nodes[1][h], nodes[2][o]
        signals.append(f'''    <circle r="3.2" fill="{t['accent']}" opacity="0">
      <animateMotion dur="2.4s" begin="{k * 0.55:.2f}s" repeatCount="indefinite" path="M{a[0]},{a[1]} L{b[0]},{b[1]} L{c[0]},{c[1]}"/>
      <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.85;1" dur="2.4s" begin="{k * 0.55:.2f}s" repeatCount="indefinite"/>
    </circle>''')
    circles = []
    for i, col in enumerate(nodes):
        for j, (x, y) in enumerate(col):
            pulse = (f'<animate attributeName="fill" values="{t["bg"]};{t["accent"]};{t["bg"]}" dur="3.3s" '
                     f'begin="{(i * 0.9 + j * 0.45):.2f}s" repeatCount="indefinite"/>')
            circles.append(f'    <circle cx="{x}" cy="{y}" r="8" fill="{t["bg"]}" stroke="{t["accent"]}" stroke-width="2">{pulse}</circle>')
    return "\n".join([lines, *signals, *circles])


def hero(t: dict) -> str:
    w, h = 1012, 280
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Aryan Ranade — AI/ML Engineer, Computer Science Student">
  <defs><clipPath id="card"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="18"/></clipPath></defs>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="18" fill="{t['bg']}"/>
  <rect x="0" y="0" width="8" height="{h}" fill="{t['accent']}" clip-path="url(#card)"/>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="18" stroke="{t['border']}" stroke-width="1.5"/>

  <text x="52" y="58" font-family="{MONO}" font-size="13" fill="{t['muted']}"><tspan fill="{t['accent_text']}">~</tspan>/aryanranade <tspan fill="{t['accent_text']}">$</tspan> whoami</text>
  <text x="50" y="128" font-family="{FONT}" font-size="58" font-weight="800" letter-spacing="-1" fill="{t['text']}">Aryan Ranade</text>
  <rect x="52" y="150" width="64" height="5" rx="2.5" fill="{t['accent']}"/>
  <text x="52" y="188" font-family="{FONT}" font-size="16" font-weight="600" letter-spacing="2.5" fill="{t['muted']}">AI/ML ENGINEER<tspan fill="{t['accent_text']}" dx="10">/</tspan><tspan dx="10">COMPUTER SCIENCE STUDENT</tspan></text>

  <g transform="translate(52,214)">
    <rect width="232" height="32" rx="16" fill="{t['surface']}" stroke="{t['accent']}" stroke-width="1.2"/>
    <circle cx="19" cy="16" r="4.5" fill="{t['accent']}">
      <animate attributeName="r" values="4.5;6;4.5" dur="1.8s" repeatCount="indefinite"/>
    </circle>
    <text x="33" y="20.5" font-family="{MONO}" font-size="11" font-weight="600" letter-spacing="1" fill="{t['text']}">OPEN TO AI/ML INTERNSHIPS</text>
  </g>

  <g>
{network(t, 690, 40)}
  </g>
</svg>
'''


# ---------------------------------------------------------------- section headers
SECTIONS = [
    ("about", "ABOUT"),
    ("projects", "FEATURED PROJECTS"),
    ("stack", "TECH STACK"),
    ("analytics", "GITHUB ANALYTICS"),
    ("connect", "CONNECT"),
]


def header(index: int, title: str, t: dict) -> str:
    w, h, mid = 1012, 52, 26
    title_x = 50
    # approximate rendered width: bold 17px caps + 3px tracking
    line_x = round(title_x + len(title) * 14.6 + 20)
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title.title()}">
  <rect x="0" y="{mid - 17}" width="36" height="34" rx="8" fill="{t['accent']}"/>
  <text x="18" y="{mid + 5}" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="800" fill="{t['on_accent']}">{index:02d}</text>
  <text x="{title_x}" y="{mid + 6}" font-family="{FONT}" font-size="17" font-weight="800" letter-spacing="3" fill="{t['text']}">{escape(title)}</text>
  <rect x="{line_x}" y="{mid}" width="{w - line_x - 18}" height="1.5" fill="{t['border']}"/>
  <rect x="{w - 12}" y="{mid - 3}" width="8" height="8" rx="2" fill="{t['accent']}" transform="rotate(45 {w - 8} {mid + 1})"/>
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
    w, h, pad = 408, 226, 24
    pill_w = round(len(p["metric"]) * 7.1 + 32)
    desc = "\n".join(
        f'  <text x="{pad}" y="{100 + i * 19}" font-family="{FONT}" font-size="13" fill="{t["muted"]}">{line}</text>'
        for i, line in enumerate(p["desc"]))
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{p['name']}">
  <defs><clipPath id="cc"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14"/></clipPath></defs>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="{t['surface']}"/>
  <rect x="0" y="0" width="{w}" height="5" fill="{t['accent']}" clip-path="url(#cc)"/>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" stroke="{t['border']}" stroke-width="1.5"/>
  <text x="{pad}" y="38" font-family="{MONO}" font-size="10.5" font-weight="700" letter-spacing="1.4" fill="{t['accent_text']}">{p['kicker']}</text>
  <text x="{pad}" y="66" font-family="{MONO}" font-size="17" font-weight="700" fill="{t['text']}">{p['name']}</text>
  <g transform="translate({w - 44},24)">
    <rect width="24" height="24" rx="6" fill="{t['bg']}" stroke="{t['border']}"/>
    <path d="M8 16 L16 8 M10 8 H16 V14" stroke="{t['accent']}" stroke-width="1.8" stroke-linecap="round" fill="none">
      <animateTransform attributeName="transform" type="translate" values="0 0;1.5 -1.5;0 0" dur="2.6s" repeatCount="indefinite"/>
    </path>
  </g>
{desc}
  <rect x="{pad}" y="152" width="{pill_w}" height="26" rx="13" fill="{t['accent']}"/>
  <text x="{pad + 16}" y="169" font-family="{MONO}" font-size="11.5" font-weight="700" fill="{t['on_accent']}">{p['metric']}</text>
  <rect x="{pad}" y="190" width="{w - 2 * pad}" height="1" fill="{t['border']}"/>
  <text x="{pad}" y="210" font-family="{MONO}" font-size="11" fill="{t['muted']}">{p['tech']}</text>
</svg>
'''


# ---------------------------------------------------------------- connect buttons
BUTTONS = [
    dict(slug="email", label="EMAIL ME", primary=True,
         icon='<rect x="2" y="4" width="20" height="16" rx="2.5"/><path d="M2.5 6.5 12 13.5 21.5 6.5"/>'),
    dict(slug="linkedin", label="LINKEDIN", primary=False,
         icon='<rect x="2.5" y="2.5" width="19" height="19" rx="4"/>'
              '<path d="M7.5 10.5 V17 M7.5 7.2 V7.4 M11.5 17 V12.8 Q11.5 10.5 13.8 10.5 T16.2 12.8 V17"/>'),
    dict(slug="portfolio", label="PORTFOLIO", primary=False,
         icon='<circle cx="12" cy="12" r="9.5"/><ellipse cx="12" cy="12" rx="4.2" ry="9.5"/><path d="M2.5 12 H21.5"/>'),
]


def connect_button(b: dict, t: dict) -> str:
    w, h = 236, 54
    fill, stroke, fg = ((t["accent"], t["accent"], t["on_accent"]) if b["primary"]
                        else (t["surface"], t["accent"], t["text"]))
    icon_c = t["on_accent"] if b["primary"] else t["accent"]
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{b['label'].title()}">
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>
  <g transform="translate(26,15)" stroke="{icon_c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="none">{b['icon']}</g>
  <text x="{(w + 44) // 2}" y="{h // 2 + 5}" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="800" letter-spacing="2.5" fill="{fg}">{b['label']}</text>
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
