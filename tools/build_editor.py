"""Render the profile header: an editor window in which `bach.ts` types itself out.

Usage:
    python tools/build_header.py <font_dir> <out_dir>

<font_dir> must contain FragmentMono-Regular and -Italic (Google Fonts, OFL) as
FragmentMono.ttf and FragmentMonoI.ttf. Writes `editor.svg`.
"""

import base64
import io
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

WIDTH = 1200
FONT_SIZE = 21
CHAR_ADVANCE = 0.618  # Fragment Mono advance width, in em
CHAR_W = FONT_SIZE * CHAR_ADVANCE
LINE_H = 34
TAB_BAR_H = 52
STATUS_BAR_H = 36
PAD_Y = 26
GUTTER_X = 32
CODE_X = 96
MS_PER_CHAR = 14
MS_BETWEEN_LINES = 140
START_DELAY_MS = 500

FILE_NAME = "bach.ts"


def s(text):
    return (text, "str")


def p(text):
    return (text, "punc")


def prop(name):
    return (f"  {name}", "prop")


def array(*items):
    tokens = [p("[")]
    for i, item in enumerate(items):
        tokens += [s(f'"{item}"')] + ([p(", ")] if i < len(items) - 1 else [])
    return tokens + [p("],")]


CODE = [
    [("// Finland", "comment")],
    [],
    [("export ", "kw"), ("const ", "kw"), ("bach", "var"), p(" = {")],
    [prop("name"), p(": "), s('"Bach Phung Quang"'), p(",")],
    [prop("role"), p(": "), s('"Full-stack developer"'), p(",")],
    [prop("company"), p(": "), s('"Seaber"'), p(","), ("  // planning software for shipping", "comment")],
    [prop("stack"), p(": ")] + array("TypeScript", "React", "Next.js", "Node.js", "PostgreSQL"),
    [prop("infra"), p(": ")] + array("Docker", "Kubernetes", "AWS CDK"),
    [prop("building"), p(": "), s('"a RAG travel assistant on AWS"'), p(",")],
    [prop("learning"), p(": "), s('"DevOps with Kubernetes"'), p(",")],
    [prop("motto"), p(": "), s('"Every failure is a lesson learned"'), p(",")],
    [p("} "), ("satisfies ", "kw"), ("Developer", "type"), p(";")],
]

HEIGHT = TAB_BAR_H + PAD_Y * 2 + LINE_H * len(CODE) + STATUS_BAR_H

THEMES = {
    "night": {
        "window": "#0C1326",
        "chrome": "#070B17",
        "border": "#223052",
        "gutter": "#4A5675",
        "text": "#EEF2FA",
        "punc": "#8A96B4",
        "kw": "#FF7A90",
        "var": "#EEF2FA",
        "prop": "#22D3EE",
        "str": "#3DF5A7",
        "type": "#A78BFA",
        "comment": "#5D6A8A",
        "cursor": "#3DF5A7",
        "muted": "#8A96B4",
    },
}


def escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def line_text(tokens):
    return "".join(text for text, _ in tokens)


def typing_schedule():
    """Start time and duration (ms) for each line; empty lines take no time."""
    schedule, clock = [], START_DELAY_MS
    for tokens in CODE:
        duration = len(line_text(tokens)) * MS_PER_CHAR
        schedule.append((clock, duration))
        clock += duration + (MS_BETWEEN_LINES if duration else 0)
    return schedule


def embedded_font(font_dir, file_name, text):
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = []
    options.drop_tables += ["meta"]
    font = TTFont(Path(font_dir) / file_name)
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=text)
    subsetter.subset(font)
    buffer = io.BytesIO()
    font.flavor = "woff2"
    font.save(buffer)
    return base64.b64encode(buffer.getvalue()).decode()


def style_block(fonts, schedule):
    last_start, last_duration = schedule[-1]
    end_ms = last_start + last_duration
    per_line = "".join(
        f".l{i}{{animation:type {d}ms steps({len(line_text(CODE[i])) + 1},end) {start}ms forwards}}"
        f".c{i}{{animation:caret {d}ms linear {start}ms}}"
        for i, (start, d) in enumerate(schedule)
        if d
    )
    return f"""
@font-face{{font-family:Mono;src:url(data:font/woff2;base64,{fonts['regular']}) format('woff2');font-style:normal}}
@font-face{{font-family:Mono;src:url(data:font/woff2;base64,{fonts['italic']}) format('woff2');font-style:italic}}
text{{font-family:Mono,ui-monospace,'SF Mono',Menlo,monospace;font-size:{FONT_SIZE}px;white-space:pre}}
.ui{{font-size:15px}}
.comment{{font-style:italic}}
.caret{{opacity:0}}
.final{{animation:blink 1.1s step-end {end_ms}ms infinite}}
@keyframes type{{to{{transform:translateX(var(--w))}}}}
@keyframes caret{{0%,100%{{opacity:1}}}}
@keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}}}
{per_line}
@media (prefers-reduced-motion:reduce){{.cover{{display:none}}.caret{{animation:none}}.final{{animation:none;opacity:1}}}}
"""


def code_lines(theme, schedule):
    top = TAB_BAR_H + PAD_Y
    out = []
    for i, tokens in enumerate(CODE):
        baseline = top + i * LINE_H + LINE_H * 0.68
        out.append(
            f'<text class="ui" x="{CODE_X - 28}" y="{baseline:.1f}" text-anchor="end" fill="{theme["gutter"]}">{i + 1}</text>'
        )
        if not tokens:
            continue
        spans = "".join(
            f'<tspan class="{kind}" fill="{theme[kind]}">{escape(text)}</tspan>' for text, kind in tokens
        )
        out.append(f'<text x="{CODE_X}" y="{baseline:.1f}">{spans}</text>')
        # One extra step: some renderers hold the last step short of 100% after the animation ends.
        typed_w = (len(line_text(tokens)) + 1) * CHAR_W
        row_y = top + i * LINE_H
        caret_class = "final" if i == len(CODE) - 1 else f"c{i}"
        out.append(
            f'<g class="cover l{i}" style="--w:{typed_w:.1f}px">'
            f'<rect x="{CODE_X}" y="{row_y}" width="{WIDTH}" height="{LINE_H}" fill="{theme["window"]}"/>'
            f'<rect class="caret {caret_class}" x="{CODE_X + 1}" y="{row_y + 6}" width="2.5" height="{LINE_H - 12}" fill="{theme["cursor"]}"/>'
            "</g>"
        )
    return "".join(out)


def chrome(theme):
    """Tab bar with the file tab, and a status bar; no traffic-light dots."""
    tab_w = 150
    status_y = HEIGHT - STATUS_BAR_H
    return (
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{TAB_BAR_H}" rx="12" fill="{theme["chrome"]}"/>'
        f'<rect x="0.5" y="{TAB_BAR_H - 12}" width="{WIDTH - 1}" height="12" fill="{theme["chrome"]}"/>'
        f'<rect x="{GUTTER_X - 8}" y="12" width="{tab_w}" height="{TAB_BAR_H - 12}" rx="6" fill="{theme["window"]}"/>'
        f'<rect x="{GUTTER_X - 8}" y="{TAB_BAR_H - 8}" width="{tab_w}" height="8" fill="{theme["window"]}"/>'
        f'<text class="ui" x="{GUTTER_X + 10}" y="{TAB_BAR_H - 14}" fill="{theme["text"]}">{FILE_NAME}</text>'
        f'<text class="ui" x="{WIDTH - GUTTER_X}" y="{TAB_BAR_H - 14}" text-anchor="end" fill="{theme["muted"]}">github.com/BachPhung</text>'
        f'<line x1="0" y1="{TAB_BAR_H}" x2="{WIDTH}" y2="{TAB_BAR_H}" stroke="{theme["border"]}"/>'
        f'<line x1="0" y1="{status_y}" x2="{WIDTH}" y2="{status_y}" stroke="{theme["border"]}"/>'
        f'<text class="ui" x="{GUTTER_X}" y="{HEIGHT - 12}" fill="{theme["muted"]}">TypeScript</text>'
        f'<text class="ui" x="{WIDTH - GUTTER_X}" y="{HEIGHT - 12}" text-anchor="end" fill="{theme["muted"]}">'
        f"Ln {len(CODE)}, Col {len(line_text(CODE[-1])) + 1}</text>"
    )


def render(theme_name, fonts, schedule):
    t = THEMES[theme_name]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Bach Phung Quang, full-stack developer at Seaber in Finland. Stack: TypeScript, React, Next.js, Node.js, PostgreSQL.">
<style>{style_block(fonts, schedule)}</style>
<defs><clipPath id="window"><rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12"/></clipPath></defs>
<g clip-path="url(#window)">
<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" fill="{t['window']}"/>
{chrome(t)}
{code_lines(t, schedule)}
</g>
<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" fill="none" stroke="{t['border']}"/>
</svg>
"""


def main(font_dir, out_dir):
    schedule = typing_schedule()
    all_text = "".join(line_text(tokens) for tokens in CODE) + FILE_NAME + "github.com/BachPhung TypeScript Ln Col 0123456789"
    fonts = {
        "regular": embedded_font(font_dir, "FragmentMono.ttf", all_text),
        "italic": embedded_font(font_dir, "FragmentMonoI.ttf", all_text),
    }
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for theme_name in THEMES:
        svg = render(theme_name, fonts, schedule)
        out = Path(out_dir) / "editor.svg"
        out.write_text(svg)
        print(f"{out}  {WIDTH}x{HEIGHT}  {len(svg) / 1024:.0f} KB  typing ends at {schedule[-1][0] + schedule[-1][1]} ms")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
