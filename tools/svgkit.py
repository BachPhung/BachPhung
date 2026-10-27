"""Shared pieces for the profile SVGs: palette, font embedding and text measuring."""

import base64
import io
from functools import lru_cache
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

# Night over Tampere: a dark sky, northern-light greens, and one gold accent for the Vietnamese star.
PALETTE = {
    "sky": "#070B17",
    "skyHigh": "#0E1631",
    "panel": "#0C1326",
    "panelRaised": "#121B33",
    "border": "#223052",
    "text": "#EEF2FA",
    "muted": "#8A96B4",
    "faint": "#4A5675",
    "aurora": "#3DF5A7",
    "auroraBlue": "#22D3EE",
    "auroraViolet": "#A78BFA",
    "gold": "#FFCD3C",
    "rose": "#FF7A90",
}

DISPLAY_FONT = "Bricolage.ttf"
# JetBrains Mono covers Vietnamese (ộ, ế); Fragment Mono, used by the editor, does not.
MONO_FONT = "JetBrainsMono.ttf"


def escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


@lru_cache(maxsize=None)
def load_font(font_dir, file_name, weight=None):
    font = TTFont(Path(font_dir) / file_name)
    if "fvar" in font and weight is not None:
        defaults = {"wght": weight, "wdth": 100, "opsz": 96}
        axes = {a.axisTag: defaults[a.axisTag] for a in font["fvar"].axes if a.axisTag in defaults}
        font = instancer.instantiateVariableFont(font, axes)
    return font


def font_face(font_dir, file_name, family, text, weight=None, italic=False):
    """A @font-face rule with the font subset to `text` and inlined as woff2."""
    weight = weight or (400 if "fvar" in load_font(font_dir, file_name) else None)
    font = TTFont(io.BytesIO(_to_bytes(load_font(font_dir, file_name, weight))))
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["kern"]
    options.drop_tables += ["meta", "STAT"]
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=text + " ")
    subsetter.subset(font)
    font.flavor = "woff2"
    data = base64.b64encode(_to_bytes(font)).decode()
    style = "italic" if italic else "normal"
    css_weight = weight or 400
    return (
        f"@font-face{{font-family:{family};font-style:{style};font-weight:{css_weight};"
        f"src:url(data:font/woff2;base64,{data}) format('woff2')}}"
    )


def advances(font_dir, file_name, text, size, weight=None):
    """Per-character advance widths in px, without kerning (pages set font-kerning:none)."""
    weight = weight or (400 if "fvar" in load_font(font_dir, file_name) else None)
    font = load_font(font_dir, file_name, weight)
    cmap, hmtx = font.getBestCmap(), font["hmtx"]
    units = font["head"].unitsPerEm
    return [hmtx[cmap[ord(ch)]][0] * size / units for ch in text]


def _to_bytes(font):
    buffer = io.BytesIO()
    font.save(buffer)
    return buffer.getvalue()
