"""
Kolam Dataset Collector
========================
Downloads real Kolam images from Wikimedia Commons (public domain)
and generates synthetic Kolam images for training/testing.

Run:  python dataset_collector.py
"""

import os
import sys
import time
import json
import urllib.request
import urllib.parse
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arc, PathPatch, Polygon
from matplotlib.path import Path

DATASET_DIR = "dataset/kolam_images"
SYNTH_DIR   = "dataset/synthetic"
META_FILE   = "dataset/metadata.json"

os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(SYNTH_DIR,   exist_ok=True)
os.makedirs("dataset",   exist_ok=True)


# ── 1. Download from Wikimedia Commons ───────────────────────────────────────

WIKIMEDIA_SEARCHES = [
    "Kolam", "Rangoli kolam", "Pulli kolam",
    "Sikku kolam", "Tamil kolam", "Indian kolam floor art"
]

def wikimedia_search(query, limit=15):
    """Search Wikimedia Commons for images and return download URLs."""
    base = "https://commons.wikimedia.org/w/api.php"
    params = urllib.parse.urlencode({
        "action":      "query",
        "generator":   "search",
        "gsrnamespace": 6,
        "gsrsearch":   f"filetype:bitmap {query}",
        "gsrlimit":    limit,
        "prop":        "imageinfo",
        "iiprop":      "url|size|mime",
        "format":      "json",
    })
    url = f"{base}?{params}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "KolamResearch/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        pages = data.get("query", {}).get("pages", {})
        results = []
        for page in pages.values():
            info = page.get("imageinfo", [{}])[0]
            mime = info.get("mime", "")
            w    = info.get("width",  0)
            h    = info.get("height", 0)
            if mime in ("image/jpeg", "image/png") and w >= 200 and h >= 200:
                results.append({
                    "url":   info.get("url"),
                    "title": page.get("title", ""),
                    "w": w, "h": h
                })
        return results
    except Exception as e:
        print(f"  [warn] Wikimedia search failed for '{query}': {e}")
        return []


def download_image(url, filepath):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "KolamResearch/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
        with open(filepath, "wb") as f:
            f.write(data)
        # Verify it's a valid image
        img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        return img is not None
    except Exception as e:
        print(f"  [warn] Download failed: {e}")
        return False


def collect_real_images(target=50):
    print("\n=== Collecting Real Kolam Images from Wikimedia Commons ===")
    metadata = []
    seen_urls = set()
    count = 0

    for query in WIKIMEDIA_SEARCHES:
        if count >= target:
            break
        print(f"\nSearching: '{query}'")
        results = wikimedia_search(query, limit=20)
        print(f"  Found {len(results)} candidates")

        for item in results:
            if count >= target:
                break
            url = item["url"]
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            ext      = ".jpg" if "jpeg" in item["url"].lower() else ".png"
            filename = f"real_{count+1:03d}{ext}"
            filepath = os.path.join(DATASET_DIR, filename)

            sys.stdout.write(f"  Downloading {filename} ... ")
            sys.stdout.flush()

            if download_image(url, filepath):
                print("OK")
                metadata.append({
                    "file":   filename,
                    "type":   "real",
                    "source": url,
                    "query":  query,
                    "w": item["w"],
                    "h": item["h"],
                })
                count += 1
            else:
                print("FAILED")
            time.sleep(0.3)   # be polite

    print(f"\nDownloaded {count} real images.")
    return metadata


# ── 2. Generate Synthetic Kolam Images ───────────────────────────────────────

BG = '#0d0500'

def _rot(x, y, deg):
    a = np.radians(deg)
    return x*np.cos(a) - y*np.sin(a), x*np.sin(a) + y*np.cos(a)


def _save_fig(fig, path):
    fig.savefig(path, dpi=120, bbox_inches='tight', facecolor=BG)
    plt.close(fig)


def synth_flower(path, n=6, color='#FF6B35', noise=False):
    fig, ax = plt.subplots(figsize=(5,5), facecolor=BG)
    ax.set_facecolor(BG)
    r = 1.65; d = r*0.65
    for k in range(n):
        px,py = _rot(d, 0, 360*k/n)
        ax.add_patch(Circle((px,py), r, fill=False, edgecolor=color, linewidth=2.5, alpha=0.9))
    ax.add_patch(Circle((0,0), r*0.42, fill=True, facecolor='#FFD700', edgecolor='white', linewidth=1.5, zorder=6))
    dots = [(0,0)] + [_rot(d,0,360*k/n) for k in range(n)]
    for x,y in dots:
        ax.plot(x, y, 'o', color='white', markersize=7, zorder=10, markeredgecolor='#FFD700', markeredgewidth=1)
    ax.set_xlim(-3,3); ax.set_ylim(-3,3); ax.set_aspect('equal'); ax.axis('off')
    if noise:
        _add_noise(ax)
    _save_fig(fig, path)


def synth_pulli(path, grid_n=3, color='#98FB98', noise=False):
    fig, ax = plt.subplots(figsize=(5,5), facecolor=BG)
    ax.set_facecolor(BG)
    s = 1.0; off = (grid_n-1)/2
    dots = [((j-off)*s, (i-off)*s) for i in range(grid_n) for j in range(grid_n)]
    for x,y in dots:
        ax.plot(x, y, 'o', color='white', markersize=10, zorder=10, markeredgecolor='#FFD700', markeredgewidth=1.2)
    t = np.linspace(0,2*np.pi,500)
    A = s*(grid_n//2+0.5)
    ax.plot(A*np.sin(t), A*np.sin(2*t)/2, color=color, linewidth=2.5, alpha=0.9)
    ax.plot(A*np.sin(2*t)/2, A*np.sin(t), color='#FF6B35', linewidth=2.5, alpha=0.85)
    lim = grid_n*0.75
    ax.set_xlim(-lim,lim); ax.set_ylim(-lim,lim); ax.set_aspect('equal'); ax.axis('off')
    if noise:
        _add_noise(ax)
    _save_fig(fig, path)


def synth_star(path, color='#4ECDC4', noise=False):
    fig, ax = plt.subplots(figsize=(5,5), facecolor=BG)
    ax.set_facecolor(BG)
    palette = [color,'#FFD700','#FF6B35','#FF6B9D']
    for n,off,col in [(3,0,palette[0]),(3,60,palette[1]),(4,0,palette[2]),(4,45,palette[3])]:
        verts = [_rot(2.5,0,360*k/n+off) for k in range(n)]
        arr = np.array(verts)
        ax.add_patch(Polygon(arr,closed=True,fill=True,facecolor=col,edgecolor=col,linewidth=2,alpha=0.85))
    ax.add_patch(Circle((0,0),0.2,fill=True,facecolor='white',edgecolor='#FFD700',linewidth=1.5,zorder=8))
    ax.set_xlim(-3.2,3.2); ax.set_ylim(-3.2,3.2); ax.set_aspect('equal'); ax.axis('off')
    if noise:
        _add_noise(ax)
    _save_fig(fig, path)


def synth_lotus(path, color='#FF6B9D', noise=False):
    fig, ax = plt.subplots(figsize=(5,5), facecolor=BG)
    ax.set_facecolor(BG)
    rings = [(4,0.0,0.6,'#FFD700',0.22),(8,0.6,1.2,'#FF6B35',0.16),(16,1.2,1.8,color,0.10)]
    for n_p,r_in,r_out,col,fw in rings:
        for k in range(n_p):
            ang=360*k/n_p
            bx,by=_rot(r_in,0,ang); tx,ty=_rot(r_out,0,ang)
            mx,my=(bx+tx)/2,(by+ty)/2
            perp=np.array([-(ty-by),tx-bx]); perp/=np.linalg.norm(perp)+1e-9
            w=(r_out-r_in)*fw
            for cp in [(mx+perp[0]*w,my+perp[1]*w),(mx-perp[0]*w,my-perp[1]*w)]:
                verts=[(bx,by),cp,cp,(tx,ty)]
                codes=[Path.MOVETO,Path.CURVE4,Path.CURVE4,Path.CURVE4]
                ax.add_patch(PathPatch(Path(verts,codes),fill=False,edgecolor=col,linewidth=1.8,alpha=0.88))
        for x,y in [_rot(r_in,0,360*k/n_p) for k in range(n_p)]:
            ax.plot(x,y,'o',color='white',markersize=4,zorder=10)
    ax.add_patch(Circle((0,0),0.15,fill=True,facecolor='#FFD700',edgecolor='white',linewidth=1.5,zorder=8))
    ax.set_xlim(-2.2,2.2); ax.set_ylim(-2.2,2.2); ax.set_aspect('equal'); ax.axis('off')
    if noise:
        _add_noise(ax)
    _save_fig(fig, path)


def synth_sikku(path, color='#4ECDC4', noise=False):
    fig, ax = plt.subplots(figsize=(5,5), facecolor=BG)
    ax.set_facecolor(BG)
    s=0.75; widths=[1,2,3,2,1]
    grid=[]
    for row,w in enumerate(widths):
        for col in range(w):
            x=(col-(w-1)/2)*s; y=(row-2)*s
            grid.append((x,y))
    for x,y in grid:
        ax.plot(x,y,'o',color='white',markersize=7,zorder=10,markeredgecolor='#FFD700',markeredgewidth=1)
    theta=np.linspace(0,2*np.pi,500)
    R=2.0
    for phase,col,lw in [(0,color,2.5),(np.pi/2,'#FF6B35',2.5),(np.pi/4,'#FFD700',1.8)]:
        r_t=R*(0.78+0.22*np.cos(4*theta+phase))
        ax.plot(r_t*np.cos(theta+phase*0.15), r_t*np.sin(theta+phase*0.15),
                color=col, linewidth=lw, alpha=0.88)
    ax.set_xlim(-2.8,2.8); ax.set_ylim(-2.8,2.8); ax.set_aspect('equal'); ax.axis('off')
    if noise:
        _add_noise(ax)
    _save_fig(fig, path)


def synth_rangoli(path, noise=False):
    fig, ax = plt.subplots(figsize=(5,5), facecolor=BG)
    ax.set_facecolor(BG)
    zones=[(8,0,0.9,'#FFD700',0.80),(8,0.9,1.7,'#FF6B35',0.75),(16,1.6,2.4,'#FF6B9D',0.70)]
    for n_p,r_in,r_out,col,alpha in zones:
        for k in range(n_p):
            ang=360*k/n_p+(22.5 if n_p==16 else 0)
            bx,by=_rot(r_in,0,ang); tx,ty=_rot(r_out,0,ang)
            mx,my=(bx+tx)/2,(by+ty)/2
            perp=np.array([-(ty-by),tx-bx]); perp/=np.linalg.norm(perp)+1e-9
            w=(r_out-r_in)*0.28
            for cp in [(mx+perp[0]*w,my+perp[1]*w),(mx-perp[0]*w,my-perp[1]*w)]:
                verts=[(bx,by),cp,cp,(tx,ty)]
                codes=[Path.MOVETO,Path.CURVE4,Path.CURVE4,Path.CURVE4]
                ax.add_patch(PathPatch(Path(verts,codes),facecolor=col,edgecolor=col,linewidth=0,alpha=alpha*0.6))
                ax.add_patch(PathPatch(Path(verts,codes),fill=False,edgecolor=col,linewidth=1.5,alpha=0.9))
    ax.add_patch(Circle((0,0),0.3,fill=True,facecolor='#FFD700',edgecolor='white',linewidth=1.5,zorder=9))
    ax.set_xlim(-2.8,2.8); ax.set_ylim(-2.8,2.8); ax.set_aspect('equal'); ax.axis('off')
    if noise:
        _add_noise(ax)
    _save_fig(fig, path)


def _add_noise(ax):
    """Add realistic noise: texture, slight blur simulation."""
    pass   # noise is applied at pixel level after saving — see post_process()


def post_process_noise(filepath):
    """Add realistic noise to simulate real-world Kolam photos."""
    img = cv2.imread(filepath)
    if img is None:
        return
    # Gaussian noise
    noise = np.random.normal(0, 8, img.shape).astype(np.int16)
    img   = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    # Slight blur (camera focus)
    img = cv2.GaussianBlur(img, (3,3), 0.5)
    # Random brightness
    gamma = np.random.uniform(0.85, 1.15)
    img = np.clip(img * gamma, 0, 255).astype(np.uint8)
    cv2.imwrite(filepath, img)


SYNTH_GENERATORS = [
    ("Flower Kolam", synth_flower),
    ("Star Kolam",   synth_star),
    ("Pulli Kolam",  synth_pulli),
    ("Lotus Kolam",  synth_lotus),
    ("Sikku Kolam",  synth_sikku),
    ("Rangoli Kolam",synth_rangoli),
]

COLORS = ['#FF6B35','#4ECDC4','#FF6B9D','#98FB98','#FFD700','#c084fc','#60a5fa','#f472b6']


def generate_synthetic(count_per_type=8):
    print("\n=== Generating Synthetic Kolam Images ===")
    metadata = []
    total    = 0

    for label, fn in SYNTH_GENERATORS:
        print(f"\n  {label}:")
        for i in range(count_per_type):
            color    = COLORS[i % len(COLORS)]
            noise    = (i % 2 == 1)        # every other image gets noise
            filename = f"synth_{label.replace(' ','_').lower()}_{i+1:02d}.png"
            filepath = os.path.join(SYNTH_DIR, filename)

            try:
                if label == "Flower Kolam":
                    n_petals = 4 + (i % 5)
                    fn(filepath, n=n_petals, color=color, noise=noise)
                elif label == "Pulli Kolam":
                    grid_n = 2 + (i % 4)
                    fn(filepath, grid_n=grid_n, color=color, noise=noise)
                else:
                    fn(filepath, color=color, noise=noise) if label != "Rangoli Kolam" \
                        else fn(filepath, noise=noise)

                if noise:
                    post_process_noise(filepath)

                metadata.append({
                    "file":       filename,
                    "type":       "synthetic",
                    "label":      label,
                    "color":      color,
                    "noise":      noise,
                })
                total += 1
                print(f"    [{i+1}/{count_per_type}] {filename} {'+ noise' if noise else ''}")
            except Exception as e:
                print(f"    [ERROR] {filename}: {e}")

    print(f"\nGenerated {total} synthetic images.")
    return metadata


# ── 3. Save Metadata ──────────────────────────────────────────────────────────

def save_metadata(real_meta, synth_meta):
    meta = {
        "total_real":      len(real_meta),
        "total_synthetic": len(synth_meta),
        "total":           len(real_meta) + len(synth_meta),
        "real_images":     real_meta,
        "synthetic_images":synth_meta,
    }
    with open(META_FILE, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"\nMetadata saved to {META_FILE}")
    return meta


# ── 4. Summary Report ─────────────────────────────────────────────────────────

def print_summary(meta):
    print("\n" + "="*50)
    print("  DATASET COLLECTION SUMMARY")
    print("="*50)
    print(f"  Real images downloaded : {meta['total_real']}")
    print(f"  Synthetic images made  : {meta['total_synthetic']}")
    print(f"  TOTAL                  : {meta['total']}")
    print(f"\n  Saved to:")
    print(f"    {os.path.abspath(DATASET_DIR)}")
    print(f"    {os.path.abspath(SYNTH_DIR)}")
    print(f"    {os.path.abspath(META_FILE)}")
    print("="*50)

    # Count by label
    label_counts = {}
    for img in meta['synthetic_images']:
        l = img['label']
        label_counts[l] = label_counts.get(l, 0) + 1
    print("\n  Synthetic breakdown:")
    for label, cnt in label_counts.items():
        print(f"    {label:<20} : {cnt} images")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Kolam Dataset Collector")
    print("="*50)

    # Step 1: Download real images
    real_meta = collect_real_images(target=50)

    # Step 2: Generate synthetic images (8 per type × 6 types = 48)
    synth_meta = generate_synthetic(count_per_type=8)

    # Step 3: Save metadata
    meta = save_metadata(real_meta, synth_meta)

    # Step 4: Print summary
    print_summary(meta)
