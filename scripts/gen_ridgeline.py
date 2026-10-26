"""Generate a Joy Division-style ridgeline SVG for the broadleyspeaking.co.nz hero.

Lines run the full width, rising slightly left to right like the original
artwork, with a mountain mass right of centre. Each line is filled with the
page background so nearer lines hide the ones behind them. One line is drawn
in brand cyan.
"""
import math
import random
import sys

W, H = 1600, 900
LINES = 46
STEP = 8
TOP, BOTTOM = 330, 880          # baseline of the back and front lines at x=0
RISE = 210                      # how far lines climb from left edge to right edge
HIGHLIGHT = 35                  # index of the cyan line, counted from the back

STROKE = "#D0D9E2"
ACCENT = "#00B3FF"
FILL = "#FFFFFF"

# (x centre 0-1, depth centre 0-1, x spread, depth spread, height px)
PEAKS = [
    (0.78, 0.42, 0.065, 0.20, 150),
    (0.87, 0.30, 0.045, 0.14, 120),
    (0.72, 0.62, 0.055, 0.16, 110),
    (0.94, 0.58, 0.040, 0.18, 105),
    (0.82, 0.75, 0.070, 0.14, 90),
    (0.68, 0.35, 0.045, 0.12, 70),
    (0.97, 0.25, 0.035, 0.12, 80),
    (0.60, 0.70, 0.045, 0.12, 40),
]


_detail = random.Random(7)
# Smaller, sharper peaks scattered over the range for the jagged ridge texture.
PEAKS += [
    (_detail.uniform(0.58, 0.99), _detail.uniform(0.08, 0.92), _detail.uniform(0.012, 0.03),
     _detail.uniform(0.04, 0.09), _detail.uniform(18, 65))
    for _ in range(70)
]


def height(x, d, phases):
    """Peak height at horizontal position x (0-1) on a line at depth d (0-1)."""
    h = 0.0
    for cx, cd, sx, sd, amp in PEAKS:
        h += amp * math.exp(-((x - cx) ** 2) / (2 * sx * sx) - ((d - cd) ** 2) / (2 * sd * sd))
    # Mountain-shaped envelope keeps the far left calm but alive.
    envelope = 0.12 + 0.88 * (1 / (1 + math.exp(-(x - 0.62) * 14)))
    ripple = sum(a * math.sin(f * x * math.tau + p) for a, f, p in phases)
    ripple = abs(ripple) * envelope
    return h * (0.85 + 0.3 * abs(math.sin(x * 31 + d * 7))) + ripple


def main(out_path):
    rng = random.Random(20261026)
    paths = []
    for i in range(LINES):
        d = i / (LINES - 1)
        base = TOP + (BOTTOM - TOP) * d
        phases = [(rng.uniform(4, 9), rng.uniform(5, 9), rng.uniform(0, math.tau)),
                  (rng.uniform(2, 5), rng.uniform(12, 19), rng.uniform(0, math.tau)),
                  (rng.uniform(1, 3), rng.uniform(25, 40), rng.uniform(0, math.tau))]
        pts = []
        for px in range(0, W + STEP, STEP):
            x = px / W
            y = base - RISE * x - height(x, d, phases)
            pts.append((px, y))
        cmds = [f"M0 {pts[0][1]:.1f}"]
        prev = pts[0]
        for p in pts[1:]:
            cmds.append(f"l{p[0] - prev[0]} {p[1] - prev[1]:.1f}")
            prev = p
        line = "".join(cmds)
        stroke = ACCENT if i == HIGHLIGHT else STROKE
        width = 2 if i == HIGHLIGHT else 1
        paths.append(
            f'<path d="{line}V{H}H0Z" fill="{FILL}"/>'
            f'<path d="{line}" fill="none" stroke="{stroke}" stroke-width="{width}" '
            f'vector-effect="non-scaling-stroke" stroke-linejoin="round"/>'
        )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'preserveAspectRatio="xMidYMax slice">' + "".join(paths) + "</svg>\n"
    )
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"wrote {out_path} ({len(svg)} bytes)")


if __name__ == "__main__":
    main(sys.argv[1])
