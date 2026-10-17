#!/usr/bin/env python3
"""Build the static SVG assets for the profile README.

Generates hero, section headers, project cards, connect buttons and the divider
(dark + light variants each) into assets/. Run from the repo root:

    python scripts/build_assets.py

Dynamic, data-driven cards (stats, languages, activity) come from
scripts/generate_cards.py instead. Zero dependencies — stdlib only.

Design rules: black surfaces with two solid accents — royal blue and crimson —
used side by side, never blended. No gradients anywhere. Hero, cards and buttons
stay black in both GitHub themes; only section headers adapt to the page.
"""

import pathlib
from html import escape

ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace"

# Keep in sync with scripts/generate_cards.py.
# *_fill: solid shapes (white text on top passes WCAG AA) · *_text: accent text on black
INK = dict(bg="#07080B", surface="#0F1117", border="#232836", text="#F5F7FA", muted="#8C93A3",
           blue="#2563EB", blue_text="#5B9BFF", red="#DC2640", red_text="#FF4D67", on_accent="#FFFFFF")
# section headers sit directly on the GitHub page, so they follow its theme
PAGE = {
    "dark": dict(text="#F0F6FC", border="#30363D"),
    "light": dict(text="#1F2328", border="#D1D9E0"),
}


def accents(color: str) -> tuple[str, str, str]:
    """(fill, text, other-fill) for 'blue' or 'red'."""
    other = "red" if color == "blue" else "blue"
    return INK[color], INK[f"{color}_text"], INK[other]


# ---------------------------------------------------------------- hero
def network(ox: int, oy: int) -> str:
    """Feed-forward network: blue nodes, crimson signals travelling input → output."""
    layers = [[40, 100, 160], [10, 70, 130, 190], [55, 145]]
    xs = [0, 120, 240]
    nodes = [[(xs[i] + ox, y + oy) for y in col] for i, col in enumerate(layers)]
    edges = [(a, b) for i in range(len(nodes) - 1) for a in nodes[i] for b in nodes[i + 1]]
    out = [f'    <line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{INK["border"]}" stroke-width="1.2"/>'
           for a, b in edges]
    for k, (i, h, o) in enumerate([(0, 1, 0), (1, 2, 1), (2, 3, 1), (0, 0, 0), (1, 1, 1), (2, 2, 0)]):
        a, b, c = nodes[0][i], nodes[1][h], nodes[2][o]
        out.append(f'''    <circle r="3.4" fill="{INK['red']}" opacity="0">
      <animateMotion dur="2.4s" begin="{k * 0.55:.2f}s" repeatCount="indefinite" path="M{a[0]},{a[1]} L{b[0]},{b[1]} L{c[0]},{c[1]}"/>
      <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.85;1" dur="2.4s" begin="{k * 0.55:.2f}s" repeatCount="indefinite"/>
    </circle>''')
    for i, col in enumerate(nodes):
        for j, (x, y) in enumerate(col):
            flash = INK["blue"] if (i + j) % 2 == 0 else INK["red"]
            out.append(f'    <circle cx="{x}" cy="{y}" r="8" fill="{INK["bg"]}" stroke="{INK["blue_text"]}" stroke-width="2">'
                       f'<animate attributeName="fill" values="{INK["bg"]};{flash};{INK["bg"]}" dur="3.3s" '
                       f'begin="{(i * 0.9 + j * 0.45):.2f}s" repeatCount="indefinite"/></circle>')
    return "\n".join(out)


def hero() -> str:
    w, h = 1012, 280
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Aryan Ranade — AI/ML Engineer, Computer Science Student">
  <defs><clipPath id="card"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="18"/></clipPath></defs>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="18" fill="{INK['bg']}"/>
  <g clip-path="url(#card)">
    <rect x="0" y="0" width="8" height="{h // 2}" fill="{INK['blue']}"/>
    <rect x="0" y="{h // 2}" width="8" height="{h // 2}" fill="{INK['red']}"/>
  </g>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="18" stroke="{INK['border']}" stroke-width="1.5"/>

  <text x="52" y="58" font-family="{MONO}" font-size="13" fill="{INK['muted']}"><tspan fill="{INK['blue_text']}">~</tspan>/aryanranade <tspan fill="{INK['red_text']}">$</tspan> whoami</text>
  <text x="50" y="128" font-family="{FONT}" font-size="58" font-weight="800" letter-spacing="-1" fill="{INK['text']}">Aryan Ranade</text>
  <rect x="52" y="150" width="44" height="5" rx="2.5" fill="{INK['blue']}"/>
  <rect x="102" y="150" width="20" height="5" rx="2.5" fill="{INK['red']}"/>
  <text x="52" y="188" font-family="{FONT}" font-size="16" font-weight="600" letter-spacing="2.5" fill="{INK['muted']}">AI/ML ENGINEER<tspan fill="{INK['red_text']}" dx="10">/</tspan><tspan dx="10">COMPUTER SCIENCE STUDENT</tspan></text>

  <g transform="translate(52,214)">
    <rect width="232" height="32" rx="16" fill="{INK['surface']}" stroke="{INK['blue']}" stroke-width="1.4"/>
    <circle cx="19" cy="16" r="4.5" fill="{INK['red']}">
      <animate attributeName="r" values="4.5;6;4.5" dur="1.8s" repeatCount="indefinite"/>
    </circle>
    <text x="33" y="20.5" font-family="{MONO}" font-size="11" font-weight="600" letter-spacing="1" fill="{INK['text']}">OPEN TO AI/ML INTERNSHIPS</text>
  </g>

  <g>
{network(690, 40)}
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


def header(index: int, title: str, page: dict) -> str:
    w, h, mid = 1012, 52, 26
    tag, _, other = accents("blue" if index % 2 else "red")
    title_x = 50
    # approximate rendered width: heavy 17px caps + 3px tracking
    line_x = round(title_x + len(title) * 14.6 + 20)
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title.title()}">
  <rect x="0" y="{mid - 17}" width="36" height="34" rx="8" fill="{tag}"/>
  <text x="18" y="{mid + 5}" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="800" fill="{INK['on_accent']}">{index:02d}</text>
  <text x="{title_x}" y="{mid + 6}" font-family="{FONT}" font-size="17" font-weight="800" letter-spacing="3" fill="{page['text']}">{escape(title)}</text>
  <rect x="{line_x}" y="{mid}" width="{w - line_x - 34}" height="1.5" fill="{page['border']}"/>
  <rect x="{w - 26}" y="{mid - 3}" width="8" height="8" rx="2" fill="{tag}" transform="rotate(45 {w - 22} {mid + 1})"/>
  <rect x="{w - 12}" y="{mid - 3}" width="8" height="8" rx="2" fill="{other}" transform="rotate(45 {w - 8} {mid + 1})"/>
</svg>
'''


# ---------------------------------------------------------------- project cards
# color alternates in a checkerboard across the 2-column grid
PROJECTS = [
    dict(slug="autonomous-issue-resolver", name="autonomous-issue-resolver", color="blue",
         kicker="AUTONOMOUS AGENTS",
         desc=["Coding agent that plans, edits and tests fixes for",
               "real GitHub issues inside per-task Docker sandboxes,",
               "with a provider-agnostic LLM layer."],
         metric="Graded by the official SWE-bench harness",
         tech="Python · Docker · SWE-bench · Groq · Gemini"),
    dict(slug="ledgerloop", name="ledgerloop", color="red",
         kicker="AI FINANCE · RAZORPAY AI BUILDATHON",
         desc=["Three-way settlement reconciliation agent: a",
               "deterministic matching cascade, a bounded LLM",
               "adjudicator and a deterministic verifier."],
         metric="98.3% precision on held-out bench",
         tech="Python · FastAPI · Groq · DuckDB · Next.js"),
    dict(slug="TBSentinel", name="TBSentinel", color="red",
         kicker="MEDICAL IMAGING · EXPLAINABLE AI",
         desc=["Tuberculosis screening from chest X-rays — fine-tuned",
               "ResNet18, sensitivity-tuned thresholds, cross-hospital",
               "generalization testing and Grad-CAM heatmaps."],
         metric="0.896 ROC-AUC on held-out test set",
         tech="PyTorch · timm · Grad-CAM · scikit-learn · Gradio"),
    dict(slug="Development-of-AI-Based-Knowledge-Retrieval-Platform-with-Query-Resolution-System",
         name="knowledge-retrieval-platform", color="blue", kicker="AGENTIC RAG",
         desc=["Document Q&amp;A platform built on a two-level LangGraph",
               "agent over a ChromaDB vector store, with JWT auth,",
               "conversation memory and query analytics."],
         metric="Two-level agentic RAG pipeline",
         tech="FastAPI · LangGraph · ChromaDB · Ollama · Streamlit"),
    dict(slug="finance-tracker", name="finance-tracker", color="blue",
         kicker="FULL-STACK · LLM",
         desc=["Personal finance tracker with Groq Llama 3.3 insights,",
               "natural-language auto-categorization, budgets and a",
               "financial health score."],
         metric="Live on Vercel",
         tech="React · Express · MongoDB · Groq · Tailwind"),
    dict(slug="horizon-dashboard", name="horizon-dashboard", color="red",
         kicker="GENERATIVE AI · WEB",
         desc=["Travel planner that turns a prompt into multi-day",
               "itineraries, budget breakdowns and weather-aware",
               "packing lists."],
         metric="Live on Vercel",
         tech="Next.js · TypeScript · Gemini API · Tailwind"),
]


def project_card(p: dict) -> str:
    w, h, pad = 408, 226, 24
    fill, text, other = accents(p["color"])
    pill_w = round(len(p["metric"]) * 7.1 + 32)
    desc = "\n".join(
        f'  <text x="{pad}" y="{100 + i * 19}" font-family="{FONT}" font-size="13" fill="{INK["muted"]}">{line}</text>'
        for i, line in enumerate(p["desc"]))
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{p['name']}">
  <defs><clipPath id="cc"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14"/></clipPath></defs>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="{INK['bg']}"/>
  <g clip-path="url(#cc)">
    <rect x="0" y="0" width="{w}" height="5" fill="{fill}"/>
    <rect x="{w - 64}" y="0" width="64" height="5" fill="{other}"/>
  </g>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" stroke="{INK['border']}" stroke-width="1.5"/>
  <text x="{pad}" y="38" font-family="{MONO}" font-size="10.5" font-weight="700" letter-spacing="1.4" fill="{text}">{p['kicker']}</text>
  <text x="{pad}" y="66" font-family="{MONO}" font-size="17" font-weight="700" fill="{INK['text']}">{p['name']}</text>
  <g transform="translate({w - 44},24)">
    <rect width="24" height="24" rx="6" fill="{INK['surface']}" stroke="{INK['border']}"/>
    <path d="M8 16 L16 8 M10 8 H16 V14" stroke="{text}" stroke-width="1.8" stroke-linecap="round" fill="none">
      <animateTransform attributeName="transform" type="translate" values="0 0;1.5 -1.5;0 0" dur="2.6s" repeatCount="indefinite"/>
    </path>
  </g>
{desc}
  <rect x="{pad}" y="152" width="{pill_w}" height="26" rx="13" fill="{fill}"/>
  <text x="{pad + 16}" y="169" font-family="{MONO}" font-size="11.5" font-weight="700" fill="{INK['on_accent']}">{p['metric']}</text>
  <rect x="{pad}" y="190" width="{w - 2 * pad}" height="1" fill="{INK['border']}"/>
  <text x="{pad}" y="210" font-family="{MONO}" font-size="11" fill="{INK['muted']}">{p['tech']}</text>
</svg>
'''


# ---------------------------------------------------------------- connect buttons
BUTTONS = [
    dict(slug="email", label="EMAIL ME", fill=INK["red"], stroke=INK["red"],
         icon='<rect x="2" y="4" width="20" height="16" rx="2.5"/><path d="M2.5 6.5 12 13.5 21.5 6.5"/>'),
    dict(slug="linkedin", label="LINKEDIN", fill=INK["blue"], stroke=INK["blue"],
         icon='<rect x="2.5" y="2.5" width="19" height="19" rx="4"/>'
              '<path d="M7.5 10.5 V17 M7.5 7.2 V7.4 M11.5 17 V12.8 Q11.5 10.5 13.8 10.5 T16.2 12.8 V17"/>'),
    dict(slug="portfolio", label="PORTFOLIO", fill=INK["bg"], stroke=INK["muted"],
         icon='<circle cx="12" cy="12" r="9.5"/><ellipse cx="12" cy="12" rx="4.2" ry="9.5"/><path d="M2.5 12 H21.5"/>'),
]


def connect_button(b: dict) -> str:
    w, h = 236, 54
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{b['label'].title()}">
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="12" fill="{b['fill']}" stroke="{b['stroke']}" stroke-width="1.5"/>
  <g transform="translate(26,15)" stroke="{INK['on_accent']}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="none">{b['icon']}</g>
  <text x="{(w + 44) // 2}" y="{h // 2 + 5}" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="800" letter-spacing="2.5" fill="{INK['on_accent']}">{b['label']}</text>
</svg>
'''


# ---------------------------------------------------------------- divider
def divider(page: dict) -> str:
    return f'''<svg width="1012" height="4" viewBox="0 0 1012 4" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <rect x="0" y="1.5" width="1012" height="1" fill="{page['border']}"/>
</svg>
'''


def main() -> None:
    keep = {"stats", "langs", "activity"}  # owned by generate_cards.py
    for old in ASSETS.glob("*.svg"):
        if old.stem.rsplit("-", 1)[0] not in keep:
            old.unlink()
    written = 0
    for mode, page in PAGE.items():
        files = {f"hero-{mode}.svg": hero(), f"divider-{mode}.svg": divider(page)}
        for i, (slug, title) in enumerate(SECTIONS, start=1):
            files[f"h-{slug}-{mode}.svg"] = header(i, title, page)
        for p in PROJECTS:
            files[f"p-{p['name']}-{mode}.svg"] = project_card(p)
        for b in BUTTONS:
            files[f"c-{b['slug']}-{mode}.svg"] = connect_button(b)
        for name, svg in files.items():
            (ASSETS / name).write_text(svg)
            written += 1
    print(f"wrote {written} static assets to {ASSETS}")


if __name__ == "__main__":
    main()
