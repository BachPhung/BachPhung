"""The four app demos shown inside the project cards. Each one replays a real use of the project."""

import base64
from pathlib import Path

from PIL import Image

from svgkit import DISPLAY_FONT, MONO_FONT, PALETTE as C, advances, escape

MONO_SIZE = 13.5
MONO_LINE = 22


def mono(x, y, text, fill, cls="", extra=""):
    return f'<text class="mono {cls}" x="{x:.1f}" y="{y:.1f}" fill="{fill}"{extra}>{escape(text)}</text>'


def mono_width(font_dir, text):
    return sum(advances(font_dir, MONO_FONT, text, MONO_SIZE))


def wave_bars(x, y, count, color, cls, gap=7, height=16):
    return "".join(
        f'<rect class="bar {cls}" x="{x + i * gap:.1f}" y="{y - height / 2:.1f}" width="3.5" height="{height}" rx="1.75" fill="{color}" '
        f'style="animation-delay:{(i * 0.11) % 0.7:.2f}s;transform-origin:{x + i * gap + 1.75:.1f}px {y:.1f}px"/>'
        for i in range(count)
    )


def wrap(font_dir, text, size, max_width):
    """Greedy word wrap; returns lines as lists of (word, x_offset)."""
    space = advances(font_dir, DISPLAY_FONT, " ", size)[0]
    lines, line, width = [], [], 0.0
    for word in text.split():
        w = sum(advances(font_dir, DISPLAY_FONT, word, size))
        if line and width + space + w > max_width:
            lines.append(line)
            line, width = [], 0.0
        line.append((word, width + (space if line else 0)))
        width += (space if len(line) > 1 else 0) + w
    return lines + [line]


# travel-assistant: the chat UI answering from the Tampere guide, with its source.
CHAT_QUESTION = "What's special about saunas in Tampere?"
CHAT_ANSWER = (
    "Tampere calls itself the Sauna Capital of the World. Try Rajaportti in Pispala, "
    "Finland's oldest public sauna still in use, wood-heated since 1906."
)
CHAT_SOURCE = "finland_tampere.md#saunas"
# The guide's own photo of Pispala (kallerna, CC BY-SA 4.0), as the app shows it inline.
CHAT_PHOTO = "pispala.jpg"
PHOTO_W, PHOTO_H = 150, 112


def chat(tl, box, font_dir, accent):
    """`font_dir` is the asset folder: it also holds CHAT_PHOTO."""
    x, y, w = box["x"], box["y"], box["w"]
    size, line_h, pad = 15, 21, 12
    q_w = sum(advances(font_dir, DISPLAY_FONT, CHAT_QUESTION, size)) + pad * 2
    out = [
        f'<g class="{tl.show(0.4)}"><rect x="{x + w - 14 - q_w:.1f}" y="{y + 12}" width="{q_w:.1f}" height="34" rx="12" fill="{C[accent]}"/>'
        f'<text class="chat" x="{x + w - 14 - q_w + pad:.1f}" y="{y + 34}" fill="{C["sky"]}">{escape(CHAT_QUESTION)}</text></g>',
        f'<g class="{tl.show(1.1, 2.0)}"><rect x="{x + 14}" y="{y + 58}" width="58" height="30" rx="12" fill="{C["panelRaised"]}"/>'
        + "".join(f'<circle class="dot" cx="{x + 31 + i * 12}" cy="{y + 73}" r="3.2" fill="{C["muted"]}" style="animation-delay:{i * 0.15}s"/>' for i in range(3))
        + "</g>",
    ]
    bubble_w = w - 92
    lines = wrap(font_dir, CHAT_ANSWER, size, bubble_w - pad * 2 - PHOTO_W - 14)
    bubble_h = max(len(lines) * line_h + 18, PHOTO_H + 16)
    out.append(f'<rect class="{tl.show(2.0)}" x="{x + 14}" y="{y + 58}" width="{bubble_w}" height="{bubble_h}" rx="12" fill="{C["panelRaised"]}"/>')
    out.append(chat_photo(tl, font_dir, x + 14 + bubble_w - 8 - PHOTO_W, y + 58 + (bubble_h - PHOTO_H) / 2))
    clock = 2.1
    for row, words in enumerate(lines):
        for word, dx in words:
            out.append(
                f'<text class="chat {tl.show(clock, rise=False)}" x="{x + 14 + pad + dx:.1f}" y="{y + 81 + row * line_h}" fill="{C["text"]}">{escape(word)}</text>'
            )
            clock += 0.07
    chip_y = y + 58 + bubble_h + 10
    chip_w = mono_width(font_dir, CHAT_SOURCE) + 20
    out.append(
        f'<g class="{tl.show(clock + 0.2)}"><rect x="{x + 14}" y="{chip_y}" width="{chip_w:.1f}" height="24" rx="12" fill="none" stroke="{C[accent]}" stroke-opacity=".6"/>'
        + mono(x + 24, chip_y + 16.5, CHAT_SOURCE, C[accent])
        + "</g>"
    )
    input_y = box["y"] + box["h"] - 44
    out.append(
        f'<rect x="{x + 14}" y="{input_y}" width="{w - 28}" height="34" rx="17" fill="{C["sky"]}" stroke="{C["border"]}"/>'
        f'<text class="chat" x="{x + 32}" y="{input_y + 22}" fill="{C["faint"]}">Ask about another city</text>'
        f'<circle cx="{x + w - 31}" cy="{input_y + 17}" r="12" fill="{C[accent]}"/>'
        f'<path d="M{x + w - 36},{input_y + 17} h10 m-4,-4 l4,4 l-4,4" fill="none" stroke="{C["sky"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    return "".join(out)


def chat_photo(tl, asset_dir, px, py):
    """A loading placeholder, then the photo fading in, like an image arriving mid-stream."""
    data = base64.b64encode((Path(asset_dir) / CHAT_PHOTO).read_bytes()).decode()
    return (
        f'<clipPath id="chat-photo"><rect x="{px:.1f}" y="{py:.1f}" width="{PHOTO_W}" height="{PHOTO_H}" rx="8"/></clipPath>'
        f'<rect class="{tl.show(2.0, 3.4, rise=False)}" x="{px:.1f}" y="{py:.1f}" width="{PHOTO_W}" height="{PHOTO_H}" rx="8" fill="{C["border"]}"/>'
        f'<image class="{tl.show(3.2, rise=False)}" x="{px:.1f}" y="{py:.1f}" width="{PHOTO_W}" height="{PHOTO_H}" '
        f'preserveAspectRatio="xMidYMid slice" clip-path="url(#chat-photo)" href="data:image/jpeg;base64,{data}"/>'
    )


# voice-wake: one spoken command, from wake word to the light switching on.
def voice(tl, box, font_dir, accent):
    x, y = box["x"] + 16, box["y"] + 24
    green, muted, text = C["aurora"], C["muted"], C["text"]
    steps = [
        (0.3, [("$ ", C[accent]), ("./run.sh", text)]),
        (0.9, [("● ", muted), ("listening for “ê biết tuốt”", muted)]),
        (2.0, [("● ", green), ("wake word", green), ("  speaker verified", muted)]),
        (2.6, [("● ", C[accent]), ("recording", text)]),
        (4.3, [("STT ", C["auroraBlue"]), ("“bật đèn số một”", text)]),
        (5.1, [("MCP ", C["auroraViolet"]), ("home.lights  bulb 1 → on", text)]),
        (6.0, [("TTS ", C["gold"]), ("“Đã bật đèn số một.”", text)]),
        (8.6, [("● ", muted), ("listening for “ê biết tuốt”", muted)]),
    ]
    out = []
    for row, (start, parts) in enumerate(steps):
        dx, spans = 0.0, []
        for part, color in parts:
            spans.append(mono(x + dx, y + row * MONO_LINE * 1.1, part, color))
            dx += mono_width(font_dir, part)
        out.append(f'<g class="{tl.show(start)}">{"".join(spans)}</g>')
    out.append(f'<g class="{tl.show(2.6, 4.2, rise=False)}">{wave_bars(x + 120, y + 3 * MONO_LINE * 1.1 - 5, 18, C[accent], "live")}</g>')
    out.append(f'<g class="{tl.show(6.1, 8.2, rise=False)}">{wave_bars(x + 300, y + 6 * MONO_LINE * 1.1 - 5, 14, C["gold"], "live")}</g>')
    return "".join(out)


# ThaiDuong: the live site, scrolled the way a customer would browse it.
def browser(tl, box, font_dir, accent, screenshot):
    data = base64.b64encode(Path(screenshot).read_bytes()).decode()
    with Image.open(screenshot) as image:
        ratio = image.height / image.width
    image_w = box["w"]
    image_h = image_w * ratio
    travel = image_h - box["h"]
    return (
        f'<g clip-path="url(#demo-body)"><image class="scroll" x="{box["x"]}" y="{box["y"]}" width="{image_w}" height="{image_h:.0f}" '
        f'href="data:image/jpeg;base64,{data}" style="--travel:-{travel:.0f}px"/></g>'
    )


# Kubernetes: the project rolling out on the staging namespace, then ArgoCD reporting it healthy.
PODS = [
    ("todo-postgres-stset-0", 0.9),
    ("todo-backend-6c9f7d8b5-x2kq4", 1.5),
    ("todo-app-7b5d9c6f4-m8zrt", 2.1),
    ("todo-broadcaster-5f8c7d9b6-q4wn", 2.7),
]


def cluster(tl, box, font_dir, accent):
    x, y = box["x"] + 16, box["y"] + 24
    cols = {"name": 0, "ready": 284, "status": 336, "age": 492}
    green, amber, blue, muted, text = C["aurora"], C["gold"], C["auroraBlue"], C["muted"], C["text"]
    out = [
        f'<g class="{tl.show(0.3)}">{mono(x, y, "$ ", C[accent])}{mono(x + mono_width(font_dir, "$ "), y, "kubectl get pods -n staging -w", text)}</g>',
        f'<g class="{tl.show(0.7)}">'
        + "".join(mono(x + cols[k], y + MONO_LINE * 1.3, label, muted) for k, label in [("name", "NAME"), ("ready", "READY"), ("status", "STATUS"), ("age", "AGE")])
        + "</g>",
    ]
    for row, (name, start) in enumerate(PODS):
        ry = y + MONO_LINE * (2.4 + row * 1.15)
        running_at = start + 2.6 + row * 0.3
        out.append(f'<g class="{tl.show(start)}">{mono(x, ry, name, text)}{mono(x + cols["age"], ry, f"{4 + row * 2}s", muted)}</g>')
        out.append(f'<g class="{tl.show(start, start + 1.1, rise=False)}">{mono(x + cols["ready"], ry, "0/1", muted)}{mono(x + cols["status"], ry, "Pending", amber)}</g>')
        out.append(f'<g class="{tl.show(start + 1.1, running_at, rise=False)}">{mono(x + cols["ready"], ry, "0/1", muted)}{mono(x + cols["status"], ry, "ContainerCreating", blue)}</g>')
        out.append(f'<g class="{tl.show(running_at, rise=False)}">{mono(x + cols["ready"], ry, "1/1", text)}{mono(x + cols["status"], ry, "Running", green)}</g>')
    synced_y = y + MONO_LINE * 7.4
    out.append(
        f'<g class="{tl.show(7.2)}">{mono(x, synced_y, "argocd ", C["auroraViolet"])}'
        f'{mono(x + mono_width(font_dir, "argocd "), synced_y, "todo-staging  Synced  Healthy", green)}</g>'
    )
    return "".join(out)
