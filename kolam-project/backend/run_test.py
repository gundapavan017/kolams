import os, json
import numpy as np, cv2
from modules.analyzer import KolamAnalyzer

analyzer = KolamAnalyzer()

# ── DOT DETECTION TEST ─────────────────────────────────────────────
print("=== DOT DETECTION TEST ===")
test_cases = [(3,3,9),(4,4,16),(5,5,25),(3,5,15),(2,2,4)]
total=0; correct=0
for rows, cols, expected in test_cases:
    img = np.zeros((400,400,3), dtype=np.uint8)
    sp=80; sx=(400-(cols-1)*sp)//2; sy=(400-(rows-1)*sp)//2
    for r in range(rows):
        for c in range(cols):
            cv2.circle(img, (sx+c*sp, sy+r*sp), 12, (255,255,255), -1)
    res = analyzer.analyze(img)
    det = res['dot_count']
    total+=1; correct+=int(det==expected)
    status = "OK" if det==expected else "FAIL"
    print("  Grid %dx%d: expected=%d  detected=%d  [%s]" % (rows,cols,expected,det,status))
print("  Dot accuracy: %d/%d (%d%%)" % (correct, total, correct/total*100))

# ── SYNTHETIC ACCURACY TEST ────────────────────────────────────────
print("")
print("=== SYNTHETIC CLASSIFICATION ACCURACY ===")
SYNTH = "dataset/synthetic"

with open("dataset/metadata.json") as f:
    meta = json.load(f)

by_label = {}; total=0; correct=0
for item in meta["synthetic_images"]:
    fp = os.path.join(SYNTH, item["file"])
    if not os.path.exists(fp):
        continue
    img   = cv2.imread(fp)
    res   = analyzer.analyze(img)
    label = item["label"]
    pred  = res["pattern_type"]
    ok    = (pred == label)
    total+=1; correct+=int(ok)
    by_label.setdefault(label, {"t":0,"c":0})
    by_label[label]["t"] += 1
    by_label[label]["c"] += int(ok)

print("  %-20s  %7s  %5s  %8s" % ("Pattern","Correct","Total","Accuracy"))
print("  " + "-"*46)
for lbl, r in sorted(by_label.items()):
    acc = r["c"]/r["t"]*100
    bar = "#" * int(acc/10)
    print("  %-20s  %7d  %5d  %7.1f%%  %s" % (lbl, r["c"], r["t"], acc, bar))

print("")
print("  OVERALL ACCURACY: %d/%d  (%.1f%%)" % (correct, total, correct/total*100))

# ── REAL IMAGE TEST ────────────────────────────────────────────────
print("")
print("=== REAL IMAGE TEST ===")
REAL = "dataset/kolam_images"
files = [f for f in os.listdir(REAL) if f.lower().endswith((".jpg",".png"))]
if not files:
    print("  No real images found.")
else:
    print("  Testing %d real images:" % len(files))
    for fname in sorted(files):
        img = cv2.imread(os.path.join(REAL, fname))
        res = analyzer.analyze(img)
        print("  %-40s  dots=%-3d  sym=%d-fold  -> %s" % (
            fname, res["dot_count"], res["symmetry_fold"], res["pattern_type"]))
