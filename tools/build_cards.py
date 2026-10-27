"""Render one card per side project: a live-looking demo of the app on top, what it is below.

Usage:
    python tools/build_cards.py <asset_dir> <out_dir>

<asset_dir> holds the fonts named in svgkit plus `thaiduong.jpg`, a 900px-wide screenshot of
the top of thaiduongvlxd.com. Needs fontTools and Pillow.
"""

import html
import re
import sys
from pathlib import Path

import demos
from svgkit import DISPLAY_FONT, MONO_FONT, PALETTE as C, escape, font_face
from timeline import Timeline

WIDTH, HEIGHT = 600, 500
WINDOW = {"x": 16, "y": 16, "w": 568, "h": 304}
CHROME_H = 36

CARDS = [
    {
        "slug": "travel-assistant",
        "title": "travel-assistant",
        "accent": "aurora",
        "lines": ["RAG travel assistant: answers from curated", "guides, in your language, with sources."],
        "tags": ["LangGraph", "pgvector", "AWS CDK"],
        "chrome": ("browser", "bachphung.dev/chat"),
        "demo": "chat",
        "cycle": 13,
    },
    {
        "slug": "voice-wake",
        "title": "voice-wake",
        "accent": "rose",
        "lines": ["Vietnamese voice assistant for Claude Code,", "from wake word to the lights turning on."],
        "tags": ["Python", "PhoWhisper", "MCP"],
        "chrome": ("terminal", "~/voice-claude"),
        "demo": "voice",
        "cycle": 11,
    },
    {
        "slug": "thaiduong",
        "title": "ThaiDuong",
        "accent": "gold",
        "lines": ["Product catalogue for a building-materials", "shop in Hà Nội, live at thaiduongvlxd.com."],
        "tags": ["Next.js", "Wix SDK", "Cloudflare"],
        "chrome": ("browser", "thaiduongvlxd.com"),
        "demo": "browser",
        "cycle": 14,
    },
    {
        "slug": "kubernetes",
        "title": "Kubernetes-Helsinki",
        "accent": "auroraBlue",
        "lines": ["DevOps with Kubernetes: a todo app shipped", "to k3d through ArgoCD, staging and prod."],
        "tags": ["Kubernetes", "ArgoCD", "k3d"],
        "chrome": ("terminal", "kubectl  staging"),
        "demo": "cluster",
        "cycle": 10,
    },
]


def window_chrome(kind, label, accent):
    x, y, w = WINDOW["x"], WINDOW["y"], WINDOW["w"]
    bar = (
        f'<rect x="{x}" y="{y}" width="{w}" height="{CHROME_H}" rx="14" fill="{C["panelRaised"]}"/>'
        f'<rect x="{x}" y="{y + CHROME_H - 14}" width="{w}" height="14" fill="{C["panelRaised"]}"/>'
        f'<line x1="{x}" y1="{y + CHROME_H}" x2="{x + w}" y2="{y + CHROME_H}" stroke="{C["border"]}"/>'
    )
    if kind == "browser":
        pill_w = 300
        px = x + (w - pill_w) / 2
        return bar + (
            f'<rect x="{px}" y="{y + 7}" width="{pill_w}" height="22" rx="11" fill="{C["sky"]}"/>'
            f'<path d="M{px + 14},{y + 18} v-2.5 a3.2,3.2 0 0 1 6.4,0 v2.5" fill="none" stroke="{C["muted"]}" stroke-width="1.4"/>'
            f'<rect x="{px + 12.5}" y="{y + 17.5}" width="9.4" height="7" rx="1.5" fill="{C["muted"]}"/>'
            f'<text class="mono" x="{px + 30}" y="{y + 22.5}" fill="{C["muted"]}">{escape(label)}</text>'
        )
    return bar + (
        f'<text class="mono" x="{x + 16}" y="{y + 23}" fill="{C["muted"]}">{escape(label)}</text>'
        f'<circle cx="{x + w - 20}" cy="{y + CHROME_H / 2}" r="4" fill="{C[accent]}" class="pulse"/>'
    )


def demo_body(card, tl, font_dir, screenshot):
    box = {"x": WINDOW["x"], "y": WINDOW["y"] + CHROME_H, "w": WINDOW["w"], "h": WINDOW["h"] - CHROME_H}
    if card["demo"] == "browser":
        return demos.browser(tl, box, font_dir, card["accent"], screenshot)
    return getattr(demos, card["demo"])(tl, box, font_dir, card["accent"])


def tags(card):
    x, out = 24, []
    for label in card["tags"]:
        w = len(label) * 13 * 0.6 + 22
        out.append(
            f'<rect x="{x:.1f}" y="448" width="{w:.1f}" height="28" rx="14" fill="none" stroke="{C[card["accent"]]}" stroke-opacity=".55"/>'
            f'<text class="tag" x="{x + 11:.1f}" y="466.5" fill="{C[card["accent"]]}">{escape(label)}</text>'
        )
        x += w + 8
    return "".join(out)


def text_of(svg_body, cls_pattern):
    found = re.findall(rf'<text class="[^"]*(?:{cls_pattern})[^"]*"[^>]*>([^<]*)</text>', svg_body)
    return "".join(html.unescape(t) for t in found)


def style_block(font_dir, card, body, tl):
    return f"""{font_face(font_dir, DISPLAY_FONT, "Display", card["title"], weight=800)}
{font_face(font_dir, DISPLAY_FONT, "Display", text_of(body, "body|chat"), weight=400)}
{font_face(font_dir, MONO_FONT, "Mono", text_of(body, "mono|tag"))}
text{{font-kerning:none}}
.title{{font-family:Display,sans-serif;font-weight:800;font-size:28px;fill:{C['text']}}}
.body{{font-family:Display,sans-serif;font-size:17px;fill:{C['muted']}}}
.chat{{font-family:Display,sans-serif;font-size:15px}}
.mono{{font-family:Mono,monospace;font-size:{demos.MONO_SIZE}px;white-space:pre}}
.tag{{font-family:Mono,monospace;font-size:13px}}
.dot{{animation:bounce .5s ease-in-out infinite alternate}}
.bar{{animation:eq .7s ease-in-out infinite alternate}}
.pulse{{animation:pulse 1.6s ease-in-out infinite}}
.scroll{{animation:scroll {card['cycle']}s cubic-bezier(.45,0,.25,1) infinite}}
@keyframes bounce{{to{{transform:translateY(-4px)}}}}
@keyframes eq{{from{{transform:scaleY(.25)}}to{{transform:scaleY(1)}}}}
@keyframes pulse{{50%{{opacity:.3}}}}
@keyframes scroll{{0%,12%{{transform:none}}40%,55%{{transform:translateY(calc(var(--travel) * .45))}}82%,92%{{transform:translateY(var(--travel))}}100%{{transform:none}}}}
{tl.css()}
@media (prefers-reduced-motion:reduce){{.dot,.bar,.pulse,.scroll{{animation:none}}}}
"""


def render(font_dir, card, screenshot):
    tl = Timeline(card["cycle"])
    accent = C[card["accent"]]
    w = WINDOW
    body = (
        f'<rect x="{w["x"]}" y="{w["y"]}" width="{w["w"]}" height="{w["h"]}" rx="14" fill="{C["sky"]}"/>'
        + demo_body(card, tl, font_dir, screenshot)
        + window_chrome(*card["chrome"], card["accent"])
        + f'<rect x="{w["x"]}" y="{w["y"]}" width="{w["w"]}" height="{w["h"]}" rx="14" fill="none" stroke="{C["border"]}"/>'
        + f'<text class="title" x="24" y="372">{escape(card["title"])}</text>'
        + "".join(f'<text class="body" x="24" y="{402 + i * 24}">{escape(line)}</text>' for i, line in enumerate(card["lines"]))
        + tags(card)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{escape(card['title'])}: {escape(' '.join(card['lines']))}">
<style>{style_block(font_dir, card, body, tl)}</style>
<defs><radialGradient id="halo" cx="0" cy="0" r="1"><stop offset="0" stop-color="{accent}" stop-opacity=".28"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
<clipPath id="card"><rect x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" rx="20"/></clipPath>
<clipPath id="demo-body"><rect x="{w['x']}" y="{w['y'] + CHROME_H}" width="{w['w']}" height="{w['h'] - CHROME_H}" rx="14"/></clipPath></defs>
<g clip-path="url(#card)">
<rect width="{WIDTH}" height="{HEIGHT}" fill="{C['panel']}"/>
<circle cx="0" cy="{HEIGHT}" r="420" fill="url(#halo)"/>
{body}
</g>
<rect x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" rx="20" fill="none" stroke="{C['border']}" stroke-width="1.5"/>
</svg>
"""


def main(asset_dir, out_dir):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    screenshot = Path(asset_dir) / "thaiduong.jpg"
    for card in CARDS:
        out = Path(out_dir) / f"card-{card['slug']}.svg"
        out.write_text(render(asset_dir, card, screenshot))
        print(f"{out}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
