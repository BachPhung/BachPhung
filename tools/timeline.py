"""One shared clock per card, so every element of a demo appears and resets in order."""


class Timeline:
    """Hands out CSS classes that show an element from `start` to `end` seconds of a looping cycle.

    Without `end`, the element stays until the whole demo resets at the end of the cycle.
    """

    RESET_SECONDS = 0.6
    FADE_SECONDS = 0.25

    def __init__(self, cycle):
        self.cycle = cycle
        self.rules = []
        self.transient = []

    def show(self, start, end=None, rise=True):
        name = f"t{len(self.rules)}"
        stop = end if end is not None else self.cycle - self.RESET_SECONDS

        def pct(seconds):
            return f"{min(max(seconds / self.cycle * 100, 0), 100):.2f}%"

        hidden = "opacity:0;transform:translateY(6px)" if rise else "opacity:0"
        shown = "opacity:1;transform:none" if rise else "opacity:1"
        self.rules.append(
            f"@keyframes {name}{{0%,{pct(start)}{{{hidden}}}{pct(start + self.FADE_SECONDS)},{pct(stop)}{{{shown}}}"
            f"{pct(stop + self.FADE_SECONDS)},100%{{opacity:0}}}}"
            f".{name}{{opacity:0;animation:{name} {self.cycle}s linear infinite}}"
        )
        if end is not None:
            self.transient.append(name)
        return name

    def css(self):
        """Keyframes plus a reduced-motion rule that shows the final frame and hides transient states."""
        names = [f"t{i}" for i in range(len(self.rules))]
        persistent = [n for n in names if n not in self.transient]
        still = ",".join(f".{n}" for n in persistent) or ".none"
        gone = ",".join(f".{n}" for n in self.transient) or ".none"
        return (
            "".join(self.rules)
            + f"@media (prefers-reduced-motion:reduce){{{still}{{animation:none;opacity:1}}{gone}{{animation:none;opacity:0}}}}"
        )
