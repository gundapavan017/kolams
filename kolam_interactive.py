#!/usr/bin/env python3
"""
Interactive Kolam Generator
============================
Run this script, choose a kolam type and customize parameters,
and it saves a PNG of your chosen kolam.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, Arc, PathPatch, Polygon
from matplotlib.path import Path


#  helpers (same as kolam_generator.py) 

def rot(x, y, deg, cx=0.0, cy=0.0):
    a = np.radians(deg)
    x -= cx; y -= cy
    return x * np.cos(a) - y * np.sin(a) + cx, \
           x * np.sin(a) + y * np.cos(a) + cy


def bezier_petal(ax, base, tip, width, color, lw=2.0, alpha=0.9, fill_alpha=0.0):
    bx, by = base; tx, ty = tip
    mx, my = (bx + tx) / 2, (by + ty) / 2
    perp = np.array([-(ty - by), tx - bx])
    perp /= (np.linalg.norm(perp) + 1e-9)
    c1x, c1y = mx + perp[0] * width, my + perp[1] * width
    c2x, c2y = mx - perp[0] * width, my - perp[1] * width

    for cpx, cpy in [(c1x, c1y), (c2x, c2y)]:
        verts = [(bx, by), (cpx, cpy), (cpx, cpy), (tx, ty)]
        codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
        ax.add_patch(PathPatch(Path(verts, codes), fill=False,
                               edgecolor=color, linewidth=lw, alpha=alpha, zorder=4))
    if fill_alpha > 0:
        verts_f = [(bx, by), (c1x, c1y), (c1x, c1y), (tx, ty),
                   (c2x, c2y), (c2x, c2y), (bx, by)]
        codes_f = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
                   Path.CURVE4, Path.CURVE4, Path.CURVE4]
        ax.add_patch(PathPatch(Path(verts_f, codes_f),
                               facecolor=color, edgecolor='none',
                               alpha=fill_alpha, zorder=3))


def place_dots(ax, positions, dot_color='white', edge='#FFD700', size=6):
    for x, y in positions:
        ax.plot(x, y, 'o', color=dot_color, markersize=size, zorder=12,
                markeredgecolor=edge, markeredgewidth=0.8)


def style_ax(ax, title, size, cx=0, cy=0, pad=1.35):
    ax.set_xlim(cx - size * pad, cx + size * pad)
    ax.set_ylim(cy - size * pad, cy + size * pad)
    ax.set_aspect('equal'); ax.axis('off'); ax.set_facecolor('#1a0a00')
    ax.set_title(title, color='white', fontsize=13, pad=10, fontweight='bold')


#  kolam functions 

def draw_flower(ax, n_petals=6, color='#FF6B35', size=3):
    cx = cy = 0
    r = size * 0.55; d = r * 0.65
    for k in range(n_petals):
        px, py = rot(cx + d, cy, 360 * k / n_petals, cx, cy)
        ax.add_patch(Circle((px, py), r, fill=True, facecolor=color,
                             edgecolor=color, linewidth=1.8, alpha=0.12, zorder=2))
        ax.add_patch(Circle((px, py), r, fill=False, edgecolor=color,
                             linewidth=1.8, alpha=0.85, zorder=3))
    ax.add_patch(Circle((cx, cy), size * 1.02, fill=False, edgecolor=color,
                         linewidth=1.2, alpha=0.35, zorder=2))
    ax.add_patch(Circle((cx, cy), r * 0.42, fill=True, facecolor='#FFD700',
                         edgecolor='white', linewidth=1.5, zorder=6))
    tips = [rot(cx + size * 0.92, cy, 360 * k / n_petals, cx, cy) for k in range(n_petals)]
    xs = [p[0] for p in tips] + [tips[0][0]]
    ys = [p[1] for p in tips] + [tips[0][1]]
    ax.plot(xs, ys, color=color, linewidth=1.2, alpha=0.45, linestyle='--', zorder=2)
    dots = [(cx, cy)] + [rot(cx + d, cy, 360 * k / n_petals, cx, cy) for k in range(n_petals)]
    place_dots(ax, dots)
    style_ax(ax, f'Flower Kolam  ({n_petals}-petal  |  {n_petals}-fold symmetry)', size)
    print(f'  Principle: {n_petals} overlapping circles (Vesica Piscis). Each pair of')
    print(f'  adjacent circles forms one lens-shaped petal. {n_petals}-fold symmetry.')


def draw_lotus(ax, layers=4, color='#FF6B9D', size=3):
    cx = cy = 0
    palette = ['#FFD700', '#FF6B35', color, '#4ECDC4', '#98FB98']
    counts = [4 * (2 ** i) for i in range(layers)]        # 4,8,16,32,...
    ring_size = 1.0 / layers
    for i, n_petals in enumerate(counts):
        r_in  = i * ring_size
        r_out = (i + 1) * ring_size
        col   = palette[i % len(palette)]
        for k in range(n_petals):
            ang  = 360 * k / n_petals
            base = rot(cx + size * r_in,  cy, ang, cx, cy)
            tip  = rot(cx + size * r_out, cy, ang, cx, cy)
            w    = size * ring_size * 0.18
            bezier_petal(ax, base, tip, w, col, lw=1.6, alpha=0.88, fill_alpha=0.12)
        for rf in [r_in, r_out]:
            ax.add_patch(Circle((cx, cy), size * rf, fill=False,
                                 edgecolor='white', linewidth=0.4, alpha=0.15, zorder=1))
    ax.add_patch(Circle((cx, cy), size * 0.07, fill=True, facecolor='#FFD700',
                         edgecolor='white', linewidth=1.5, zorder=8))
    style_ax(ax, f'Lotus Mandala  ({layers} rings  |  {counts[-1]}-fold outer symmetry)', size)
    print(f'  Principle: {layers} concentric rings, each doubling petal count.')
    print(f'  Inner-to-outer: {counts}. Bezier curves shape each petal.')


def draw_pulli(ax, grid_n=3, color='#98FB98', size=3):
    cx = cy = 0
    s = size / (grid_n + 0.5)
    offset = (grid_n - 1) / 2
    dots = [(cx + (j - offset) * s, cy + (i - offset) * s)
            for i in range(grid_n) for j in range(grid_n)]
    place_dots(ax, dots, size=8)

    t = np.linspace(0, 2 * np.pi, 600)
    A = s * (grid_n // 2 + 0.5)
    for angle, col, lw, al in [(0,  color,    2.8, 0.92),
                                (90, '#FF6B35', 2.8, 0.88)]:
        lx = cx + A * np.sin(t)
        ly = cy + A * np.sin(2 * t) / 2
        if angle == 90:
            lx, ly = ly + cx, lx + cy
            lx = lx - cx; ly = ly - cy; lx += cx; ly += cy
        ax.plot(lx, ly, color=col, linewidth=lw, alpha=al, zorder=5)

    for ang in [45, 135, 225, 315]:
        ax.add_patch(Arc((cx + A * np.cos(np.radians(ang)),
                          cy + A * np.sin(np.radians(ang))),
                         s * 1.2, s * 1.2,
                         theta1=ang + 105, theta2=ang + 255,
                         color='#FF6B9D', linewidth=2.2, alpha=0.85, zorder=6))

    style_ax(ax, f'Pulli Kolam  ({grid_n}x{grid_n} dot grid  |  Lissajous enclosure)', size)
    print(f'  Principle: {grid_n}x{grid_n} = {grid_n*grid_n} dots. Lissajous figure-8')
    print(f'  loops enclose every dot. Corner arcs complete the enclosure.')


def draw_star(ax, n_polygons=2, polygon_sides=4, color='#4ECDC4', size=3):
    cx = cy = 0
    palette = [color, '#FFD700', '#FF6B35', '#FF6B9D']
    for i in range(n_polygons):
        offset = 180 * i / (n_polygons * polygon_sides)
        col = palette[i % len(palette)]
        verts = [rot(cx + size * 0.88, cy, 360 * k / polygon_sides + offset, cx, cy)
                 for k in range(polygon_sides)]
        arr = np.array(verts)
        ax.add_patch(Polygon(arr, closed=True, fill=True, facecolor=col,
                              edgecolor='none', alpha=0.15, zorder=2))
        xs = list(arr[:, 0]) + [arr[0, 0]]
        ys = list(arr[:, 1]) + [arr[0, 1]]
        ax.plot(xs, ys, color=col, linewidth=2.2, alpha=0.90, zorder=4)

    ax.add_patch(Circle((cx, cy), size * 0.07, fill=True, facecolor='white',
                         edgecolor='#FFD700', linewidth=1.5, zorder=8))

    dots = {(cx, cy)}
    for i in range(n_polygons):
        offset = 180 * i / (n_polygons * polygon_sides)
        for k in range(polygon_sides):
            x, y = rot(cx + size * 0.88, cy, 360 * k / polygon_sides + offset, cx, cy)
            dots.add((round(x, 3), round(y, 3)))
    place_dots(ax, list(dots), size=5)

    total_pts = polygon_sides * n_polygons
    style_ax(ax, f'Star Kolam  ({n_polygons} x {polygon_sides}-gon  |  {total_pts}-pointed star)', size)
    print(f'  Principle: {n_polygons} regular {polygon_sides}-gons, each rotated')
    print(f'  by {180//polygon_sides}deg. Creates a {total_pts}-pointed star polygon.')


#  colour presets 

COLOURS = {
    '1': ('#FF6B35', 'Saffron orange'),
    '2': ('#FF6B9D', 'Pink'),
    '3': ('#4ECDC4', 'Teal'),
    '4': ('#98FB98', 'Pale green'),
    '5': ('#FFD700', 'Gold'),
    '6': ('#c084fc', 'Lavender'),
}


#  menu helpers 

def choose(prompt, options, default):
    print(f'\n{prompt}')
    for k, v in options.items():
        marker = ' (default)' if k == default else ''
        label = v if isinstance(v, str) else v[1]
        print(f'  {k}. {label}{marker}')
    raw = input('Your choice: ').strip() or default
    return raw if raw in options else default


def get_int(prompt, lo, hi, default):
    raw = input(f'{prompt} [{lo}-{hi}, default {default}]: ').strip()
    try:
        v = int(raw)
        return v if lo <= v <= hi else default
    except ValueError:
        return default


#  main interactive loop 

def main():
    print('=' * 55)
    print('  KOLAM GENERATOR -- Interactive Mode')
    print('=' * 55)

    KOLAMS = {
        '1': 'Flower Kolam   (Vesica Piscis circles)',
        '2': 'Lotus Mandala  (Concentric Bezier rings)',
        '3': 'Pulli Kolam    (Dot grid + Lissajous loops)',
        '4': 'Star Kolam     (Superimposed polygons)',
    }

    choice = choose('Choose a Kolam type:', KOLAMS, '1')
    colour_key = choose('Choose a colour:', COLOURS, '1')
    color, color_name = COLOURS[colour_key]
    size = get_int('Enter size (complexity scale)', 2, 6, 3)

    BG = '#0d0500'
    fig, ax = plt.subplots(figsize=(8, 8), facecolor=BG)
    ax.set_facecolor(BG)

    print('\n  Design Principles Applied:')
    print('  ' + '-' * 52)

    if choice == '1':
        n = get_int('  Number of petals', 3, 12, 6)
        draw_flower(ax, n_petals=n, color=color, size=size)
    elif choice == '2':
        n = get_int('  Number of rings', 2, 6, 4)
        draw_lotus(ax, layers=n, color=color, size=size)
    elif choice == '3':
        n = get_int('  Dot grid size (NxN)', 2, 7, 3)
        draw_pulli(ax, grid_n=n, color=color, size=size)
    elif choice == '4':
        sides = get_int('  Polygon sides (3=triangle, 4=square, 6=hexagon)', 3, 8, 4)
        count = get_int('  Number of overlapping polygons', 2, 6, 2)
        draw_star(ax, n_polygons=count, polygon_sides=sides, color=color, size=size)

    print('\n  Common to all kolams:')
    print('    - Dot grid (pulli) marks anchor points')
    print('    - Rotational symmetry enforced throughout')
    print('    - Closed curves / loops (no open ends)')

    names = {'1': 'flower', '2': 'lotus', '3': 'pulli', '4': 'star'}
    fname = f'kolam_{names[choice]}_{color_name.replace(" ", "_")}.png'

    fig.suptitle(f'Kolam  --  {color_name}', color='#FFD700', fontsize=14,
                 fontweight='bold', y=0.97)
    plt.tight_layout()
    plt.savefig(fname, dpi=150, bbox_inches='tight', facecolor=BG)
    print(f'\n  Saved: {fname}')
    print('=' * 55)


if __name__ == '__main__':
    main()


