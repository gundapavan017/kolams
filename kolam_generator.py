#!/usr/bin/env python3
"""
Kolam Design Analyzer and Generator
=====================================
Kolams are traditional South Indian geometric art forms drawn on floors,
doorways, and courtyards using rice flour, chalk, or coloured powder.

DESIGN PRINCIPLES IDENTIFIED:
  1. PULLI (Dot Grid)   - Patterns anchor to a symmetric grid of dots
  2. SYMMETRY           - n-fold rotational + bilateral reflective symmetry
  3. CONTINUOUS LOOPS   - Curves form closed paths (Eulerian circuits)
  4. DOT ENCLOSURE      - Every dot must be surrounded/enclosed by lines
  5. MODULAR UNITS      - Complex kolams built by repeating simple cells
  6. MATHEMATICAL BASIS - Lissajous curves, vesica piscis, star polygons

Usage:
  python kolam_generator.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, Arc, PathPatch, Polygon
from matplotlib.path import Path
from matplotlib.gridspec import GridSpec
import os


# helpers

def rot(x, y, deg, cx=0.0, cy=0.0):
    a = np.radians(deg)
    x -= cx; y -= cy
    return x * np.cos(a) - y * np.sin(a) + cx, \
           x * np.sin(a) + y * np.cos(a) + cy


def bezier_petal(ax, base, tip, width, color, lw=2.0, alpha=0.9, fill_alpha=0.0):
    bx, by = base
    tx, ty = tip
    mx, my = (bx + tx) / 2, (by + ty) / 2
    perp = np.array([-(ty - by), tx - bx])
    perp /= (np.linalg.norm(perp) + 1e-9)
    c1x, c1y = mx + perp[0] * width, my + perp[1] * width
    c2x, c2y = mx - perp[0] * width, my - perp[1] * width

    for cx_, cy_ in [(c1x, c1y), (c2x, c2y)]:
        verts = [(bx, by), (cx_, cy_), (cx_, cy_), (tx, ty)]
        codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
        patch = PathPatch(Path(verts, codes), fill=False,
                          edgecolor=color, linewidth=lw, alpha=alpha, zorder=4)
        ax.add_patch(patch)

    if fill_alpha > 0:
        verts_fill = [(bx, by),
                      (c1x, c1y), (c1x, c1y), (tx, ty),
                      (c2x, c2y), (c2x, c2y), (bx, by)]
        codes_fill = [Path.MOVETO,
                      Path.CURVE4, Path.CURVE4, Path.CURVE4,
                      Path.CURVE4, Path.CURVE4, Path.CURVE4]
        ax.add_patch(PathPatch(Path(verts_fill, codes_fill),
                               facecolor=color, edgecolor='none',
                               alpha=fill_alpha, zorder=3))


def place_dots(ax, positions, dot_color='white', edge='#FFD700', size=6):
    for x, y in positions:
        ax.plot(x, y, 'o', color=dot_color, markersize=size, zorder=12,
                markeredgecolor=edge, markeredgewidth=0.8)


def style_ax(ax, title, size, cx=0, cy=0, pad=1.25):
    ax.set_xlim(cx - size * pad, cx + size * pad)
    ax.set_ylim(cy - size * pad, cy + size * pad)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor('#1a0a00')
    ax.set_title(title, color='white', fontsize=11, pad=8, fontweight='bold')


# KOLAM 1 : Flower (Vesica Piscis)

def flower_kolam(ax, cx=0, cy=0, size=3, n=6, color='#FF6B35'):
    r = size * 0.55
    d = r * 0.65
    for k in range(n):
        px, py = rot(cx + d, cy, 360 * k / n, cx, cy)
        ax.add_patch(Circle((px, py), r, fill=True, facecolor=color,
                             edgecolor=color, linewidth=1.8, alpha=0.12, zorder=2))
        ax.add_patch(Circle((px, py), r, fill=False, edgecolor=color,
                             linewidth=1.8, alpha=0.85, zorder=3))
    ax.add_patch(Circle((cx, cy), size * 1.02, fill=False, edgecolor=color,
                         linewidth=1.2, alpha=0.35, zorder=2))
    ax.add_patch(Circle((cx, cy), r * 0.42, fill=True, facecolor='#FFD700',
                         edgecolor='white', linewidth=1.5, zorder=6))
    tips = [rot(cx + size * 0.92, cy, 360 * k / n, cx, cy) for k in range(n)]
    xs = [p[0] for p in tips] + [tips[0][0]]
    ys = [p[1] for p in tips] + [tips[0][1]]
    ax.plot(xs, ys, color=color, linewidth=1.2, alpha=0.45, linestyle='--', zorder=2)
    dots = [(cx, cy)] + [rot(cx + d, cy, 360 * k / n, cx, cy) for k in range(n)]
    place_dots(ax, dots)
    style_ax(ax, 'Flower Kolam\n(Vesica Piscis - 6-fold symmetry)', size, cx, cy)


# KOLAM 2 : Star Kolam

def star_kolam(ax, cx=0, cy=0, size=3, color='#4ECDC4'):
    palette = [color, '#FFD700', '#FF6B35', '#FF6B9D']

    def star_polygon(n, r, offset_deg, col, lw, al, fill_al):
        verts = [rot(cx + r, cy, 360 * k / n + offset_deg, cx, cy) for k in range(n)]
        arr = np.array(verts)
        ax.add_patch(Polygon(arr, closed=True, fill=True,
                              facecolor=col, edgecolor='none', alpha=fill_al, zorder=2))
        xs = list(arr[:, 0]) + [arr[0, 0]]
        ys = list(arr[:, 1]) + [arr[0, 1]]
        ax.plot(xs, ys, color=col, linewidth=lw, alpha=al, zorder=4)

    star_polygon(3, size * 0.88, 0,  palette[0], 2.2, 0.90, 0.18)
    star_polygon(3, size * 0.88, 60, palette[1], 2.2, 0.90, 0.18)
    star_polygon(4, size * 0.90, 0,  palette[2], 2.0, 0.80, 0.14)
    star_polygon(4, size * 0.90, 45, palette[3], 2.0, 0.80, 0.14)

    inner = [rot(cx + size * 0.52, cy, 30 + 60 * k, cx, cy) for k in range(6)]
    ax.add_patch(Polygon(np.array(inner), closed=True, fill=True,
                          facecolor='#1a0a00', edgecolor=palette[0],
                          linewidth=1.5, alpha=0.9, zorder=5))
    ax.add_patch(Circle((cx, cy), size * 0.07, fill=True, facecolor='white',
                         edgecolor='#FFD700', linewidth=1.5, zorder=8))

    dots = set()
    for n_poly in [3, 4]:
        for off in [0, 180 / n_poly]:
            for k in range(n_poly):
                x, y = rot(cx + size * 0.90, cy, 360 * k / n_poly + off, cx, cy)
                dots.add((round(x, 4), round(y, 4)))
    dots.add((cx, cy))
    place_dots(ax, list(dots), size=5)
    style_ax(ax, 'Star Kolam\n(Hexagram + Octagram - 12-fold symmetry)', size, cx, cy)


# KOLAM 3 : Pulli (3x3 dot grid)

def pulli_kolam(ax, cx=0, cy=0, size=3, color='#98FB98'):
    s = size / 2.8
    t = np.linspace(0, 2 * np.pi, 600)
    dots = [(cx + j * s, cy + i * s) for i in range(-1, 2) for j in range(-1, 2)]
    place_dots(ax, dots, size=7)

    A = s * 1.02
    for angle, col, lw, al in [(0,  color,     2.8, 0.92),
                                (90, '#FF6B35', 2.8, 0.88),
                                (0,  '#FFD700', 1.4, 0.45),
                                (90, '#FFD700', 1.4, 0.45)]:
        lx = cx + A * np.sin(t)
        ly = cy + A * np.sin(2 * t) / 2
        if angle == 90:
            lx, ly = ly + cx, lx + cy
            lx = lx - cx; ly = ly - cy
            lx += cx; ly += cy
        ax.plot(lx, ly, color=col, linewidth=lw, alpha=al, zorder=5)

    for ang in [45, 135, 225, 315]:
        arc = Arc((cx + A * np.cos(np.radians(ang)),
                   cy + A * np.sin(np.radians(ang))),
                  s * 1.1, s * 1.1,
                  theta1=ang + 105, theta2=ang + 255,
                  color='#FF6B9D', linewidth=2.2, alpha=0.85, zorder=6)
        ax.add_patch(arc)

    border = plt.Polygon(
        [(cx - s * 1.55, cy - s * 1.55), (cx + s * 1.55, cy - s * 1.55),
         (cx + s * 1.55, cy + s * 1.55), (cx - s * 1.55, cy + s * 1.55)],
        closed=True, fill=False, edgecolor='white', linewidth=0.8,
        alpha=0.25, linestyle='--', zorder=2)
    ax.add_patch(border)
    style_ax(ax, 'Pulli Kolam (3x3 dot grid)\n(Lissajous loops - dot-enclosure arcs)', size, cx, cy)


# KOLAM 4 : Lotus Mandala

def lotus_kolam(ax, cx=0, cy=0, size=3, color='#FF6B9D'):
    palette = ['#FFD700', '#FF6B35', color, '#4ECDC4', '#98FB98']
    ring_specs = [
        (4,  0.00, 0.22, palette[0], 0.20),
        (8,  0.22, 0.42, palette[1], 0.16),
        (8,  0.42, 0.65, palette[2], 0.14),
        (16, 0.65, 0.88, palette[3], 0.10),
        (16, 0.85, 1.04, palette[4], 0.08),
    ]
    for n_petals, r_in, r_out, col, fw in ring_specs:
        for k in range(n_petals):
            ang  = 360 * k / n_petals
            base = rot(cx + size * r_in,  cy, ang, cx, cy)
            tip  = rot(cx + size * r_out, cy, ang, cx, cy)
            w    = size * (r_out - r_in) * fw
            bezier_petal(ax, base, tip, w, col, lw=1.6, alpha=0.88, fill_alpha=0.10)

    for rf in [0.22, 0.42, 0.65, 0.88, 1.04]:
        ax.add_patch(Circle((cx, cy), size * rf, fill=False, edgecolor='white',
                             linewidth=0.4, alpha=0.15, zorder=1))
    ax.add_patch(Circle((cx, cy), size * 0.07, fill=True, facecolor='#FFD700',
                         edgecolor='white', linewidth=1.5, zorder=8))

    dots = [(cx, cy)]
    for n_petals, r_in, _, _, _ in ring_specs:
        r = size * r_in
        dots += [rot(cx + r, cy, 360 * k / n_petals, cx, cy) for k in range(n_petals)]
    place_dots(ax, dots, size=3)
    style_ax(ax, 'Lotus Mandala Kolam\n(Bezier petals - 4/8/16-fold nesting)', size, cx, cy)


# KOLAM 5 : Sikku Kolam

def sikku_kolam(ax, cx=0, cy=0, size=3, color='#4ECDC4'):
    s = size / 3.8
    widths = [1, 2, 3, 2, 1]
    grid = []
    for row, w in enumerate(widths):
        for col in range(w):
            x = cx + (col - (w - 1) / 2) * s
            y = cy + (row - 2) * s
            grid.append((x, y))
    place_dots(ax, grid, size=6)

    theta = np.linspace(0, 2 * np.pi, 600)
    R = size * 0.72
    for phase, col, lw, al in [
        (0,             color,     2.6, 0.92),
        (np.pi / 2,    '#FF6B35', 2.6, 0.88),
        (np.pi / 4,    '#FFD700', 1.8, 0.70),
        (3*np.pi / 4,  '#FF6B9D', 1.8, 0.70),
    ]:
        r_t = R * (0.78 + 0.22 * np.cos(4 * theta + phase))
        x = cx + r_t * np.cos(theta + phase * 0.15)
        y = cy + r_t * np.sin(theta + phase * 0.15)
        ax.plot(x, y, color=col, linewidth=lw, alpha=al, zorder=5)

    inner_R = size * 0.38
    for phase, col in [(0, '#98FB98'), (np.pi/2, '#FFD700')]:
        x = cx + inner_R * np.sin(theta + phase)
        y = cy + inner_R * np.sin(2 * theta + phase) / 2
        ax.plot(x, y, color=col, linewidth=2.0, alpha=0.80, zorder=6)

    for ang in range(0, 360, 45):
        ax.add_patch(Arc((cx + size * 0.72 * np.cos(np.radians(ang)),
                          cy + size * 0.72 * np.sin(np.radians(ang))),
                         s * 1.1, s * 1.1,
                         theta1=ang + 110, theta2=ang + 250,
                         color=color, linewidth=2.0, alpha=0.75, zorder=6))
    style_ax(ax, 'Sikku Kolam (single-stroke)\n(Diagonal deflections - boundary loops)', size, cx, cy)


# KOLAM 6 : Rangoli filled

def rangoli_kolam(ax, cx=0, cy=0, size=3, base_color='#FF6B35'):
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
            base = rot(cx + size * r_in,  cy, ang, cx, cy)
            tip  = rot(cx + size * r_out, cy, ang, cx, cy)
            w    = size * (r_out - r_in) * 0.30
            bezier_petal(ax, base, tip, w, col, lw=1.2, alpha=0.9, fill_alpha=alpha)

    for n_petals, r_in, r_out, col, _ in zones:
        for k in range(n_petals):
            ang = 360 * k / n_petals
            x1, y1 = rot(cx + size * r_in,  cy, ang, cx, cy)
            x2, y2 = rot(cx + size * r_out, cy, ang, cx, cy)
            ax.plot([x1, x2], [y1, y2], color='white', linewidth=0.6, alpha=0.30, zorder=6)

    ax.add_patch(Circle((cx, cy), size * 0.12, fill=True, facecolor='#FFD700',
                         edgecolor='white', linewidth=1.5, zorder=9))
    ax.add_patch(Circle((cx, cy), size * 1.22, fill=False, edgecolor='white',
                         linewidth=1.0, alpha=0.40, zorder=2))
    style_ax(ax, 'Rangoli Kolam (colour-filled)\n(Zone colouring - 8/16-fold symmetry)', size, cx, cy, pad=1.30)


# main

def main():
    BG = '#0d0500'
    fig = plt.figure(figsize=(20, 14), facecolor=BG)
    fig.suptitle('Kolam Design Principles & Recreations',
                 color='#FFD700', fontsize=18, fontweight='bold', y=0.98)

    subtitle = ('Principles:  1. Pulli (dot grid)  -  2. Rotational and reflective symmetry  -  3. Continuous closed loops  -  4. Dot enclosure  -  5. Modular construction')
    fig.text(0.5, 0.945, subtitle, ha='center', color='#cccccc', fontsize=9)

    gs = GridSpec(2, 3, figure=fig, hspace=0.38, wspace=0.12,
                  left=0.03, right=0.97, top=0.92, bottom=0.04)
    axes = [fig.add_subplot(gs[r, c]) for r in range(2) for c in range(3)]
    for ax_ in axes:
        ax_.set_facecolor(BG)

    s = 2.8
    flower_kolam (axes[0], size=s)
    star_kolam   (axes[1], size=s)
    pulli_kolam  (axes[2], size=s)
    lotus_kolam  (axes[3], size=s)
    sikku_kolam  (axes[4], size=s)
    rangoli_kolam(axes[5], size=s)

    out = 'kolam_designs.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
    print(f'Saved: {out}')



if __name__ == '__main__':
    main()


