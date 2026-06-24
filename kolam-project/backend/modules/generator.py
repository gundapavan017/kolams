"""
Kolam Generator
===============
Recreates a Kolam from extracted rules and generates new Kolam variations.
Uses matplotlib with Bezier curves, Lissajous figures, and polar geometry.
"""

import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arc, PathPatch, Polygon
from matplotlib.path import Path


BG = '#0d0500'
PALETTE = ['#FF6B35', '#4ECDC4', '#FF6B9D', '#98FB98', '#FFD700', '#c084fc']


def _rot(x, y, deg, cx=0.0, cy=0.0):
    a = np.radians(deg)
    x -= cx; y -= cy
    return x * np.cos(a) - y * np.sin(a) + cx, \
           x * np.sin(a) + y * np.cos(a) + cy


def _dots(ax, positions):
    for x, y in positions:
        ax.plot(x, y, 'o', color='white', markersize=5, zorder=12,
                markeredgecolor='#FFD700', markeredgewidth=0.8)


def _style(ax, size, pad=1.3):
    ax.set_xlim(-size * pad, size * pad)
    ax.set_ylim(-size * pad, size * pad)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor(BG)


def _bezier_petal(ax, base, tip, width, color, lw=1.6, alpha=0.88, fill_alpha=0.10):
    bx, by = base; tx, ty = tip
    mx, my = (bx + tx) / 2, (by + ty) / 2
    perp = np.array([-(ty - by), tx - bx])
    perp /= np.linalg.norm(perp) + 1e-9
    c1 = (mx + perp[0] * width, my + perp[1] * width)
    c2 = (mx - perp[0] * width, my - perp[1] * width)
    for cp in [c1, c2]:
        verts = [(bx, by), cp, cp, (tx, ty)]
        codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
        ax.add_patch(PathPatch(Path(verts, codes), fill=False,
                               edgecolor=color, linewidth=lw, alpha=alpha, zorder=4))
    if fill_alpha > 0:
        verts_f = [(bx,by), c1, c1, (tx,ty), c2, c2, (bx,by)]
        codes_f = [Path.MOVETO,Path.CURVE4,Path.CURVE4,Path.CURVE4,
                   Path.CURVE4,Path.CURVE4,Path.CURVE4]
        ax.add_patch(PathPatch(Path(verts_f, codes_f),
                               facecolor=color, edgecolor='none',
                               alpha=fill_alpha, zorder=3))


# â”€â”€ Individual Kolam Drawers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def draw_flower(ax, size=3, color='#FF6B35', n=6):
    r = size * 0.55; d = r * 0.65
    for k in range(n):
        px, py = _rot(d, 0, 360 * k / n)
        ax.add_patch(Circle((px, py), r, fill=True, facecolor=color,
                             edgecolor=color, linewidth=1.8, alpha=0.12, zorder=2))
        ax.add_patch(Circle((px, py), r, fill=False, edgecolor=color,
                             linewidth=1.8, alpha=0.85, zorder=3))
    ax.add_patch(Circle((0,0), size*1.02, fill=False, edgecolor=color,
                         linewidth=1.2, alpha=0.35, zorder=2))
    ax.add_patch(Circle((0,0), r*0.42, fill=True, facecolor='#FFD700',
                         edgecolor='white', linewidth=1.5, zorder=6))
    tips = [_rot(size * 0.92, 0, 360 * k / n) for k in range(n)]
    xs = [p[0] for p in tips] + [tips[0][0]]
    ys = [p[1] for p in tips] + [tips[0][1]]
    ax.plot(xs, ys, color=color, linewidth=1.2, alpha=0.45, linestyle='--', zorder=2)
    _dots(ax, [(0,0)] + [_rot(d, 0, 360*k/n) for k in range(n)])
    _style(ax, size)


def draw_star(ax, size=3, color='#4ECDC4'):
    palette = [color, '#FFD700', '#FF6B35', '#FF6B9D']
    for i, (n, off, col) in enumerate([(3,0,palette[0]),(3,60,palette[1]),
                                         (4,0,palette[2]),(4,45,palette[3])]):
        verts = [_rot(size*0.88, 0, 360*k/n+off) for k in range(n)]
        arr = np.array(verts)
        ax.add_patch(Polygon(arr, closed=True, fill=True, facecolor=col,
                              edgecolor='none', alpha=0.15, zorder=2))
        xs = list(arr[:,0]) + [arr[0,0]]
        ys = list(arr[:,1]) + [arr[0,1]]
        ax.plot(xs, ys, color=col, linewidth=2.2, alpha=0.90, zorder=4)
    ax.add_patch(Circle((0,0), size*0.07, fill=True, facecolor='white',
                         edgecolor='#FFD700', linewidth=1.5, zorder=8))
    dots = set()
    for n_p in [3, 4]:
        for off in [0, 180/n_p]:
            for k in range(n_p):
                x, y = _rot(size*0.88, 0, 360*k/n_p+off)
                dots.add((round(x,3), round(y,3)))
    _dots(ax, list(dots))
    _style(ax, size)


def draw_pulli(ax, size=3, color='#98FB98', grid_n=3):
    s = size / (grid_n + 0.5)
    off = (grid_n - 1) / 2
    dots = [((j-off)*s, (i-off)*s) for i in range(grid_n) for j in range(grid_n)]
    _dots(ax, dots)
    t = np.linspace(0, 2*np.pi, 600)
    A = s * (grid_n // 2 + 0.5)
    for angle, col, lw, al in [(0, color, 2.8, 0.92), (90, '#FF6B35', 2.8, 0.88)]:
        lx = A * np.sin(t)
        ly = A * np.sin(2*t) / 2
        if angle == 90:
            lx, ly = ly, lx
        ax.plot(lx, ly, color=col, linewidth=lw, alpha=al, zorder=5)
    for ang in [45, 135, 225, 315]:
        ax.add_patch(Arc((A*np.cos(np.radians(ang)), A*np.sin(np.radians(ang))),
                         s*1.1, s*1.1, theta1=ang+105, theta2=ang+255,
                         color='#FF6B9D', linewidth=2.2, alpha=0.85, zorder=6))
    _style(ax, size)


def draw_lotus(ax, size=3, color='#FF6B9D', layers=5):
    palette = ['#FFD700', '#FF6B35', color, '#4ECDC4', '#98FB98']
    ring_specs = [
        (4,  0.00, 0.22, palette[0], 0.20),
        (8,  0.22, 0.42, palette[1], 0.16),
        (8,  0.42, 0.65, palette[2], 0.14),
        (16, 0.65, 0.88, palette[3], 0.10),
        (16, 0.85, 1.04, palette[4], 0.08),
    ]
    for n_petals, r_in, r_out, col, fw in ring_specs[:layers]:
        for k in range(n_petals):
            ang = 360 * k / n_petals
            base = _rot(size * r_in, 0, ang)
            tip  = _rot(size * r_out, 0, ang)
            w    = size * (r_out - r_in) * fw
            _bezier_petal(ax, base, tip, w, col)
        ax.add_patch(Circle((0,0), size*r_in, fill=False, edgecolor='white',
                             linewidth=0.4, alpha=0.15, zorder=1))
    ax.add_patch(Circle((0,0), size*0.07, fill=True, facecolor='#FFD700',
                         edgecolor='white', linewidth=1.5, zorder=8))
    _style(ax, size)


def draw_sikku(ax, size=3, color='#4ECDC4'):
    s = size / 3.8
    widths = [1, 2, 3, 2, 1]
    grid = []
    for row, w in enumerate(widths):
        for col in range(w):
            x = (col - (w-1)/2) * s
            y = (row - 2) * s
            grid.append((x, y))
    _dots(ax, grid)
    theta = np.linspace(0, 2*np.pi, 600)
    R = size * 0.72
    for phase, col, lw, al in [
        (0,            color,     2.6, 0.92),
        (np.pi/2,      '#FF6B35', 2.6, 0.88),
        (np.pi/4,      '#FFD700', 1.8, 0.70),
        (3*np.pi/4,    '#FF6B9D', 1.8, 0.70),
    ]:
        r_t = R * (0.78 + 0.22 * np.cos(4*theta + phase))
        x = r_t * np.cos(theta + phase*0.15)
        y = r_t * np.sin(theta + phase*0.15)
        ax.plot(x, y, color=col, linewidth=lw, alpha=al, zorder=5)
    inner_R = size * 0.38
    for phase, col in [(0, '#98FB98'), (np.pi/2, '#FFD700')]:
        x = inner_R * np.sin(theta + phase)
        y = inner_R * np.sin(2*theta + phase) / 2
        ax.plot(x, y, color=col, linewidth=2.0, alpha=0.80, zorder=6)
    _style(ax, size)


def draw_rangoli(ax, size=3):
    zones = [
        (8,  0.00, 0.32, '#FFD700',  0.80),
        (8,  0.32, 0.58, '#FF6B35',  0.75),
        (16, 0.55, 0.80, '#FF6B9D',  0.70),
        (16, 0.78, 1.00, '#4ECDC4',  0.65),
        (8,  0.95, 1.20, '#98FB98',  0.60),
    ]
    for n_petals, r_in, r_out, col, alpha in zones:
        for k in range(n_petals):
            ang  = 360 * k / n_petals + (22.5 if n_petals == 16 else 0)
            base = _rot(size * r_in, 0, ang)
            tip  = _rot(size * r_out, 0, ang)
            w    = size * (r_out - r_in) * 0.30
            _bezier_petal(ax, base, tip, w, col, lw=1.2, alpha=0.9, fill_alpha=alpha)
    ax.add_patch(Circle((0,0), size*0.12, fill=True, facecolor='#FFD700',
                         edgecolor='white', linewidth=1.5, zorder=9))
    ax.add_patch(Circle((0,0), size*1.22, fill=False, edgecolor='white',
                         linewidth=1.0, alpha=0.40, zorder=2))
    _style(ax, size, pad=1.3)


# â”€â”€ Public API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

DRAWERS = {
    "Flower Kolam": draw_flower,
    "Star Kolam":   draw_star,
    "Pulli Kolam":  draw_pulli,
    "Lotus Kolam":  draw_lotus,
    "Sikku Kolam":  draw_sikku,
    "Rangoli Kolam": draw_rangoli,
}


def _fig_to_b64(fig) -> str:
    import base64
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor=BG)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    return b64


class KolamGenerator:

    def recreate(self, rules: dict) -> str:
        pattern = rules.get("pattern_type", "Flower Kolam")
        color   = PALETTE[0]
        fig, ax = plt.subplots(figsize=(6, 6), facecolor=BG)
        drawer  = DRAWERS.get(pattern, draw_flower)
        drawer(ax, size=3, color=color) if pattern not in ("Rangoli Kolam",) else draw_rangoli(ax)
        ax.set_title(f"Recreated: {pattern}", color='#FFD700', fontsize=12, fontweight='bold', pad=8)
        return _fig_to_b64(fig)

    def generate_variations(self, rules: dict, count: int = 3) -> list:
        pattern = rules.get("pattern_type", "Flower Kolam")
        results = []
        for i in range(count):
            color = PALETTE[i % len(PALETTE)]
            fig, ax = plt.subplots(figsize=(6, 6), facecolor=BG)
            drawer = DRAWERS.get(pattern, draw_flower)
            if pattern == "Rangoli Kolam":
                draw_rangoli(ax)
            elif pattern == "Flower Kolam":
                draw_flower(ax, size=3, color=color, n=5 + i)
            else:
                drawer(ax, size=3, color=color)
            ax.set_title(f"Variation {i+1}", color='#FFD700', fontsize=12, fontweight='bold', pad=8)
            results.append(_fig_to_b64(fig))
        return results

    def generate_from_params(self, pattern: str, color: str, size: int) -> str:
        fig, ax = plt.subplots(figsize=(6, 6), facecolor=BG)
        drawer = DRAWERS.get(pattern, draw_flower)
        if pattern == "Rangoli Kolam":
            draw_rangoli(ax, size=size)
        else:
            drawer(ax, size=size, color=color)
        ax.set_title(pattern, color='#FFD700', fontsize=12, fontweight='bold', pad=8)
        return _fig_to_b64(fig)

    def generate_all(self) -> dict:
        result = {}
        colors = ['#FF6B35', '#4ECDC4', '#FF6B9D', '#98FB98', '#FFD700', '#c084fc']
        for i, (name, drawer) in enumerate(DRAWERS.items()):
            fig, ax = plt.subplots(figsize=(6, 6), facecolor=BG)
            if name == "Rangoli Kolam":
                draw_rangoli(ax)
            else:
                drawer(ax, size=3, color=colors[i % len(colors)])
            ax.set_title(name, color='#FFD700', fontsize=12, fontweight='bold', pad=8)
            result[name] = _fig_to_b64(fig)
        return result

