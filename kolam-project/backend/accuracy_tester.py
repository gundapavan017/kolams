"""
Kolam Analyzer - Accuracy Tester
==================================
Tests the analyzer on the collected dataset and prints a full report.

Run:  python accuracy_tester.py
"""

import os
import json
import time
import numpy as np
import cv2
from modules.analyzer import KolamAnalyzer

SYNTH_DIR  = "dataset/synthetic"
REAL_DIR   = "dataset/kolam_images"
META_FILE  = "dataset/metadata.json"

analyzer = KolamAnalyzer()


def test_image(filepath, expected_label=None):
    img = cv2.imread(filepath)
    if img is None:
        return None

    start = time.time()
    result = analyzer.analyze(img)
    elapsed = time.time() - start

    result["_time_ms"] = round(elapsed * 1000, 1)
    result["_file"]    = os.path.basename(filepath)
    result["_expected"] = expected_label
    result["_correct"]  = (expected_label is None) or \
                           (result["pattern_type"] == expected_label)
    return result


def run_synthetic_tests():
    print("\n" + "="*60)
    print("  SYNTHETIC DATASET ACCURACY TEST")
    print("="*60)

    if not os.path.exists(META_FILE):
        print("  [!] No metadata found. Run dataset_collector.py first.")
        return {}

    with open(META_FILE) as f:
        meta = json.load(f)

    synth_images = meta.get("synthetic_images", [])
    if not synth_images:
        print("  [!] No synthetic images found.")
        return {}

    results_by_label = {}
    total = 0
    correct = 0

    for item in synth_images:
        filepath = os.path.join(SYNTH_DIR, item["file"])
        if not os.path.exists(filepath):
            continue

        label  = item["label"]
        result = test_image(filepath, expected_label=label)
        if result is None:
            continue

        total  += 1
        is_ok   = result["_correct"]
        correct += int(is_ok)

        if label not in results_by_label:
            results_by_label[label] = {"total": 0, "correct": 0, "details": []}
        results_by_label[label]["total"]   += 1
        results_by_label[label]["correct"] += int(is_ok)
        results_by_label[label]["details"].append(result)

        status = "PASS" if is_ok else "FAIL"
        print(f"  [{status}] {item['file']:<45} "
              f"dots={result['dot_count']:>2}  "
              f"grid={result['grid_size']:<8} "
              f"predicted={result['pattern_type']:<16} "
              f"({result['_time_ms']}ms)")

    print("\n  -- Per-Type Accuracy --")
    print(f"  {'Pattern':<20} {'Correct':>7}  {'Total':>5}  {'Accuracy':>8}")
    print("  " + "-"*45)
    for label, r in sorted(results_by_label.items()):
        acc = r["correct"] / r["total"] * 100 if r["total"] else 0
        bar = "#" * int(acc / 5)
        print(f"  {label:<20} {r['correct']:>7}  {r['total']:>5}  {acc:>7.1f}%  {bar}")

    overall = correct / total * 100 if total else 0
    print(f"\n  OVERALL ACCURACY: {correct}/{total}  ({overall:.1f}%)")
    return results_by_label


def run_real_tests():
    print("\n" + "="*60)
    print("  REAL IMAGE DATASET TEST")
    print("="*60)

    if not os.path.exists(REAL_DIR):
        print("  [!] No real images found. Run dataset_collector.py first.")
        return

    files = [f for f in os.listdir(REAL_DIR)
             if f.lower().endswith(('.jpg','.jpeg','.png'))]

    if not files:
        print("  [!] real image folder is empty.")
        return

    print(f"  Testing {len(files)} real images (no ground-truth labels)\n")
    pattern_counts = {}

    for fname in sorted(files):
        filepath = os.path.join(REAL_DIR, fname)
        result   = test_image(filepath)
        if result is None:
            print(f"  [SKIP] {fname} — could not read")
            continue

        pt = result["pattern_type"]
        pattern_counts[pt] = pattern_counts.get(pt, 0) + 1

        print(f"  {fname:<45} "
              f"dots={result['dot_count']:>2}  "
              f"grid={result['grid_size']:<8} "
              f"sym={result['symmetry_fold']}-fold  "
              f"→ {pt}  ({result['_time_ms']}ms)")

    print("\n  -- Classification Distribution --")
    for pt, cnt in sorted(pattern_counts.items(), key=lambda x: -x[1]):
        bar = "#" * cnt
        print(f"  {pt:<20} : {cnt:>3}  {bar}")


def run_dot_detection_test():
    print("\n" + "="*60)
    print("  DOT DETECTION ACCURACY TEST")
    print("="*60)

    # Create synthetic dot grids with known counts and test detection
    test_cases = [
        (3, 3,  9),
        (4, 4, 16),
        (5, 5, 25),
        (3, 5, 15),
        (2, 2,  4),
    ]

    total = 0; correct = 0

    for rows, cols, expected in test_cases:
        # Generate a clean image with dots
        img = np.zeros((400, 400, 3), dtype=np.uint8)
        spacing = 80
        start_x = (400 - (cols-1)*spacing) // 2
        start_y = (400 - (rows-1)*spacing) // 2
        actual_dots = 0

        for r in range(rows):
            for c in range(cols):
                cx = start_x + c * spacing
                cy = start_y + r * spacing
                cv2.circle(img, (cx, cy), 12, (255, 255, 255), -1)
                actual_dots += 1

        result = test_image_array(img)
        detected = result["dot_count"]
        exact = (detected == expected)
        close = abs(detected - expected) <= 2

        total  += 1
        correct += int(exact)

        status = "EXACT" if exact else ("CLOSE" if close else "WRONG")
        print(f"  [{status}] Grid {rows}x{cols} — "
              f"expected={expected}  detected={detected}  "
              f"grid_size={result['grid_size']}")

    print(f"\n  Dot detection exact accuracy: {correct}/{total} ({correct/total*100:.0f}%)")


def test_image_array(img):
    return analyzer.analyze(img)


def print_final_report(synth_results):
    print("\n" + "="*60)
    print("  FINAL REPORT")
    print("="*60)
    if not synth_results:
        print("  Run dataset_collector.py first to get full accuracy numbers.")
        return

    total   = sum(r["total"]   for r in synth_results.values())
    correct = sum(r["correct"] for r in synth_results.values())
    acc     = correct / total * 100 if total else 0

    print(f"""
  Dataset
  -------
  Synthetic images tested : {total}
  Correctly classified    : {correct}
  Overall accuracy        : {acc:.1f}%

  Analyzer Features
  -----------------
  Dot Detection    : 4 strategies (Blob, Adaptive Contour, Hough Circles, Color)
  Symmetry         : NCC-based (90deg, 180deg, flip-H, flip-V, diagonal)
  Loop Counting    : Canny edges + morphological close + contour hierarchy
  Classification   : Rule-based from dot count, symmetry fold, loop count

  Pattern Types Supported
  -----------------------
  Flower Kolam, Star Kolam, Pulli Kolam,
  Lotus Kolam, Sikku Kolam, Rangoli Kolam
    """)


if __name__ == "__main__":
    print("\nKolam Analyzer - Accuracy Tester")

    # 1. Dot detection accuracy on synthetic grids
    run_dot_detection_test()

    # 2. Full synthetic dataset test
    synth_results = run_synthetic_tests()

    # 3. Real image test (if available)
    run_real_tests()

    # 4. Final summary
    print_final_report(synth_results)
