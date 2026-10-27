"""Render the hero: the name rising into a northern-lights sky, with a rotating "I build ..." line.

Usage:
    python tools/build_hero.py <font_dir> <out_dir>
"""

import random
import sys
from pathlib import Path

from svgkit import DISPLAY_FONT, MONO_FONT, PALETTE as C, advances, escape, font_face

WIDTH, HEIGHT = 1200, 440
NAME = "Bach Phung Quang"
NAME_SIZE = 92
NAME_X, NAME_Y = 64, 236
LOCATION = "Finland"
BUILD_PREFIX = "I build"
PHRASES = [
    "planning software for shipping",
    "RAG agents on AWS",
    "voice assistants in Vietnamese",
    "microservices on Kubernetes",
]
PHRASE_SECONDS = 3.2
CHIPS = ["TypeScript", "React", "Next.js", "Node.js", "PostgreSQL", "Kubernetes", "AWS"]
INTRO_SECONDS = 1.4


def stars(seed=7, count=90):
    rng = random.Random(seed)
    out = []
    for i in range(count):
        x, y = rng.uniform(0, WIDTH), rng.uniform(0, HEIGHT)
        r, opacity = rng.uniform(0.5, 1.5), rng.uniform(0.25, 0.85)
        twinkle = f' class="twinkle" style="animation-delay:{rng.uniform(0, 5):.2f}s"' if i % 6 == 0 else ""
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="#fff" opacity="{opacity:.2f}"{twinkle}/>')
    return "".join(out)


def aurora():
    """Three soft curtains over the right half; each sways on its own period."""
    curtains = [
        ("auroraViolet", "M560,-40 C700,60 820,10 940,90 C1060,170 1150,80 1260,140 L1260,-40 Z", 17, 0.55),
        ("auroraBlue", "M620,-40 C760,120 880,40 1000,150 C1100,240 1180,140 1260,210 L1260,-40 Z", 13, 0.45),
        ("aurora", "M700,-40 C820,170 930,80 1040,210 C1130,310 1200,200 1260,280 L1260,-40 Z", 11, 0.6),
    ]
    glow = "".join(
        f'<path class="curtain" d="{d}" fill="url(#g-{key})" opacity="{opacity}" filter="url(#blur)" '
        f'style="animation-duration:{period}s;animation-delay:-{i * 3}s"/>'
        for i, (key, d, period, opacity) in enumerate(curtains)
    )
    # The same curtains, sharper and cut into vertical rays, give the glow its streaked texture.
    rays = "".join(
        f'<path class="curtain" d="{d}" fill="url(#g-{key})" filter="url(#soft)" '
        f'style="animation-duration:{period}s;animation-delay:-{i * 3}s"/>'
        for i, (key, d, period, _) in enumerate(curtains)
    )
    return f'{glow}<g mask="url(#rays)" opacity=".75">{rays}</g>'


def ray_mask(seed=3):
    rng = random.Random(seed)
    stripes, x = [], 520.0
    while x < WIDTH + 40:
        width = rng.uniform(2, 9)
        stripes.append(
            f'<rect x="{x:.1f}" y="0" width="{width:.1f}" height="{HEIGHT}" fill="url(#ray-fade)" opacity="{rng.uniform(0.25, 1):.2f}"/>'
        )
        x += width + rng.uniform(3, 14)
    return (
        '<linearGradient id="ray-fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/>'
        '<stop offset=".8" stop-color="#fff" stop-opacity=".2"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        f'<mask id="rays" maskUnits="userSpaceOnUse" x="0" y="0" width="{WIDTH}" height="{HEIGHT}">'
        f'<g class="shimmer">{"".join(stripes)}</g></mask>'
        '<filter id="soft" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="6"/></filter>'
    )


def gradients():
    def vertical(key):
        return (
            f'<linearGradient id="g-{key}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{C[key]}" stop-opacity="0"/>'
            f'<stop offset=".55" stop-color="{C[key]}" stop-opacity=".9"/>'
            f'<stop offset="1" stop-color="{C[key]}" stop-opacity="0"/></linearGradient>'
        )

    return (
        f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["sky"]}"/>'
        f'<stop offset="1" stop-color="{C["skyHigh"]}"/></linearGradient>'
        f'<linearGradient id="phrase" gradientUnits="userSpaceOnUse" x1="180" y1="0" x2="730" y2="0">'
        f'<stop offset="0" stop-color="{C["aurora"]}"/><stop offset=".5" stop-color="{C["auroraBlue"]}"/>'
        f'<stop offset="1" stop-color="{C["auroraViolet"]}"/></linearGradient>'
        + "".join(vertical(k) for k in ("aurora", "auroraBlue", "auroraViolet"))
        + '<filter id="blur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="28"/></filter>'
        + f'<clipPath id="frame"><rect width="{WIDTH}" height="{HEIGHT}" rx="24"/></clipPath>'
        + f'<clipPath id="phrase-window"><rect x="176" y="262" width="900" height="60"/></clipPath>'
    )


def name_letters(font_dir):
    widths = advances(font_dir, DISPLAY_FONT, NAME, NAME_SIZE, weight=800)
    x, out = NAME_X, []
    for i, (ch, w) in enumerate(zip(NAME, widths)):
        if ch != " ":
            out.append(
                f'<text class="name letter" x="{x:.1f}" y="{NAME_Y}" style="animation-delay:{0.25 + i * 0.045:.3f}s">{ch}</text>'
            )
        x += w
    return "".join(out)


def location_pin(cx, cy):
    return (
        f'<path class="pin" d="M{cx},{cy + 10} C{cx - 7},{cy + 2} {cx - 7},{cy - 2} {cx - 7},{cy - 3} '
        f'a7,7 0 0 1 14,0 C{cx + 7},{cy - 2} {cx + 7},{cy + 2} {cx},{cy + 10} Z" fill="{C["aurora"]}"/>'
        f'<circle cx="{cx}" cy="{cy - 3}" r="2.6" fill="{C["sky"]}"/>'
    )


def build_line():
    phrases = "".join(
        f'<text class="phrase" x="180" y="304" fill="url(#phrase)" '
        f'style="animation-delay:{INTRO_SECONDS + i * PHRASE_SECONDS:.2f}s">{escape(p)}</text>'
        for i, p in enumerate(PHRASES)
    )
    return (
        f'<text class="build intro" x="{NAME_X + 4}" y="304" style="animation-delay:1s">{BUILD_PREFIX}</text>'
        f'<g clip-path="url(#phrase-window)">{phrases}</g>'
    )


def chips(font_dir):
    x, y, out = NAME_X + 4, 362, []
    for i, label in enumerate(CHIPS):
        w = sum(advances(font_dir, MONO_FONT, label, 15)) + 28
        out.append(
            f'<g class="intro" style="animation-delay:{1.3 + i * 0.08:.2f}s">'
            f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="32" rx="16" fill="{C["panelRaised"]}" stroke="{C["border"]}"/>'
            f'<text class="chip" x="{x + 14:.1f}" y="{y + 21}">{label}</text></g>'
        )
        x += w + 10
    return "".join(out)


def style_block(font_dir):
    cycle = PHRASE_SECONDS * len(PHRASES)
    share = 100 / len(PHRASES)
    faces = (
        font_face(font_dir, DISPLAY_FONT, "Display", NAME, weight=800)
        + font_face(font_dir, DISPLAY_FONT, "Display", BUILD_PREFIX, weight=500)
        + font_face(font_dir, DISPLAY_FONT, "Display", "".join(PHRASES), weight=700)
        + font_face(font_dir, MONO_FONT, "Mono", LOCATION + "".join(CHIPS))
    )
    return f"""{faces}
text{{font-kerning:none}}
.name{{font-family:Display,sans-serif;font-weight:800;font-size:{NAME_SIZE}px;fill:{C['text']};letter-spacing:-0.01em}}
.build{{font-family:Display,sans-serif;font-weight:500;font-size:40px;fill:{C['text']}}}
.phrase{{font-family:Display,sans-serif;font-weight:700;font-size:40px;opacity:0;animation:phrase {cycle}s cubic-bezier(.2,.7,.2,1) infinite backwards}}
.mono{{font-family:Mono,monospace;font-size:17px;fill:{C['muted']}}}
.chip{{font-family:Mono,monospace;font-size:15px;fill:{C['text']}}}
.letter{{opacity:0;animation:rise .8s cubic-bezier(.2,.8,.2,1) forwards}}
.intro{{opacity:0;animation:fade .7s ease-out forwards}}
.curtain{{transform-origin:900px 0;animation:sway 14s ease-in-out infinite alternate}}
.twinkle{{animation:twinkle 4.5s ease-in-out infinite}}
.shimmer{{animation:shimmer 9s ease-in-out infinite alternate}}
@keyframes shimmer{{from{{transform:translateX(-24px)}}to{{transform:translateX(24px)}}}}
.pin{{animation:drop .8s cubic-bezier(.3,1.6,.5,1) .2s backwards}}
@keyframes rise{{from{{opacity:0;transform:translateY(34px)}}to{{opacity:1;transform:none}}}}
@keyframes fade{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
@keyframes phrase{{0%{{opacity:0;transform:translateY(40px)}}{share * 0.12:.1f}%{{opacity:1;transform:none}}{share * 0.86:.1f}%{{opacity:1;transform:none}}{share:.1f}%{{opacity:0;transform:translateY(-40px)}}100%{{opacity:0;transform:translateY(-40px)}}}}
@keyframes sway{{0%{{transform:translateX(-40px) skewX(-6deg) scaleY(.9)}}100%{{transform:translateX(50px) skewX(7deg) scaleY(1.12)}}}}
@keyframes twinkle{{0%,100%{{opacity:.2}}50%{{opacity:1}}}}
@keyframes drop{{from{{transform:translateY(-16px);opacity:0}}to{{transform:none;opacity:1}}}}
@media (prefers-reduced-motion:reduce){{
.letter,.intro,.pin{{animation:none;opacity:1}}.curtain,.twinkle,.shimmer{{animation:none}}
.phrase{{animation:none}}.phrase:first-child{{opacity:1}}}}
"""


def render(font_dir):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{NAME}, {LOCATION}. I build planning software for shipping, RAG agents on AWS, voice assistants in Vietnamese and microservices on Kubernetes.">
<style>{style_block(font_dir)}</style>
<defs>{gradients()}{ray_mask()}</defs>
<g clip-path="url(#frame)">
<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#sky)"/>
{aurora()}
{stars()}
<g class="intro" style="animation-delay:.1s">{location_pin(75, 92)}<text class="mono" x="92" y="98">{LOCATION}</text></g>
{name_letters(font_dir)}
{build_line()}
{chips(font_dir)}
</g>
</svg>
"""


def main(font_dir, out_dir):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    out = Path(out_dir) / "hero.svg"
    out.write_text(render(font_dir))
    print(f"{out}  {WIDTH}x{HEIGHT}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
