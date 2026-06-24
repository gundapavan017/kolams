"""
Kolam Image Analyzer  —  Improved v2
=====================================
Pipeline:
  1. Preprocessing   — denoise, normalize, handle any background color
  2. Dot Detection   — multi-strategy: blob + adaptive contour + Hough circles
  3. Grid Estimation — cluster dots into rows/columns, estimate NxM grid
  4. Symmetry        — rotational (90/180) + bilateral (H/V flip) via NCC
  5. Loop Counting   — closed-contour graph analysis
  6. Classification  — rule-based pattern type from detected features
"""

import cv2
import numpy as np


class KolamAnalyzer:

    def analyze(self, img: np.ndarray) -> dict:
        gray        = self._preprocess(img)
        dots, grid_size, dot_count = self._detect_dots(gray, img)
        sym_type, sym_fold         = self._detect_symmetry(gray)
        loop_count                 = self._count_loops(gray)
        stroke_type                = self._detect_stroke(gray)
        pattern_type               = self._classify(dot_count, sym_fold, loop_count, grid_size, dots)

        return {
            "grid_size":    grid_size,
            "dot_count":    dot_count,
            "symmetry_type": sym_type,
            "symmetry_fold": sym_fold,
            "loop_count":   loop_count,
            "pattern_type": pattern_type,
            "stroke_type":  stroke_type,
            "dots":         dots,
        }

    # ── Step 1: Preprocessing ─────────────────────────────────────────────────

    def _preprocess(self, img: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Denoise
        gray = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)

        # CLAHE — improves local contrast (helps with textured/floor backgrounds)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        gray  = clahe.apply(gray)

        return gray

    # ── Step 2: Dot Detection (multi-strategy) ────────────────────────────────

    def _detect_dots(self, gray, color_img):
        h, w = gray.shape

        # ── Strategy 1: Strict large-circle detection (real Pulli dots) ──
        strict = self._strict_circle_dots(gray)

        # ── Strategy 2: Blob + adaptive + Hough + color (catches smaller dots) ──
        loose = []
        loose += self._blob_detect(gray)
        loose += self._blob_detect(cv2.bitwise_not(gray))
        loose += self._adaptive_contour(gray)
        loose += self._hough_circles(gray)
        loose += self._color_dot_detect(color_img)

        # Use strict dots if they form a plausible set; otherwise fall back to loose
        strict_merged = self._merge_nearby(strict, min_dist=15)
        loose_merged  = self._merge_nearby(loose,  min_dist=15)

        # Strict dots (area≥150) = actual Pulli dots; use only when clearly found
        dots = strict_merged if len(strict_merged) >= 4 else loose_merged

        dot_count = len(dots)
        grid_size = self._estimate_grid(dots)
        return [[int(x), int(y)] for x, y in dots], grid_size, dot_count

    def _strict_circle_dots(self, gray):
        """Find only LARGE (area≥150), highly circular filled regions.
        Pulli dots (markersize=10) pass; smaller decorative dots do not."""
        h, w = gray.shape
        _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        dots = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 150 or area > h * w * 0.02:
                continue
            perimeter = cv2.arcLength(cnt, True)
            if perimeter < 1:
                continue
            circularity = 4 * np.pi * area / (perimeter ** 2)
            if circularity > 0.60:
                M = cv2.moments(cnt)
                if M['m00']:
                    dots.append([int(M['m10']/M['m00']), int(M['m01']/M['m00'])])
        return dots

    def _blob_detect(self, gray):
        params = cv2.SimpleBlobDetector_Params()
        params.filterByArea        = True
        params.minArea             = 8
        params.maxArea             = 8000
        params.filterByCircularity = True
        params.minCircularity      = 0.30
        params.filterByConvexity   = False
        params.filterByInertia     = True
        params.minInertiaRatio     = 0.3
        detector = cv2.SimpleBlobDetector_create(params)
        return [[int(kp.pt[0]), int(kp.pt[1])] for kp in detector.detect(gray)]

    def _adaptive_contour(self, gray):
        # Adaptive threshold — handles shadows and non-uniform backgrounds
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            blockSize=25, C=8
        )
        # Morphological close to fill small gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        dots = []
        h, w = gray.shape
        img_area = h * w

        for thresh_src in [thresh, cv2.bitwise_not(thresh)]:
            contours, _ = cv2.findContours(thresh_src, cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < 8 or area > img_area * 0.04:
                    continue
                perimeter = cv2.arcLength(cnt, True)
                if perimeter < 1:
                    continue
                circularity = 4 * np.pi * area / (perimeter ** 2)
                if circularity > 0.28:
                    M = cv2.moments(cnt)
                    if M['m00'] != 0:
                        cx = int(M['m10'] / M['m00'])
                        cy = int(M['m01'] / M['m00'])
                        dots.append([cx, cy])
        return dots

    def _hough_circles(self, gray):
        blurred = cv2.GaussianBlur(gray, (7, 7), 1.5)
        h, w    = gray.shape
        min_r   = max(4,  int(min(h, w) * 0.008))
        max_r   = min(60, int(min(h, w) * 0.08))

        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=int(min(h, w) * 0.04),
            param1=60,
            param2=22,
            minRadius=min_r,
            maxRadius=max_r,
        )
        if circles is None:
            return []
        return [[int(c[0]), int(c[1])] for c in circles[0]]

    def _color_dot_detect(self, img):
        """Detect bright white or dark black circular regions in color image."""
        dots = []
        h, w = img.shape[:2]
        img_area = h * w

        for mask_fn in [
            lambda i: cv2.inRange(i, np.array([200,200,200]), np.array([255,255,255])),  # white dots
            lambda i: cv2.inRange(i, np.array([0,0,0]),       np.array([50,50,50])),      # black dots
        ]:
            mask    = mask_fn(img)
            kernel  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            cleaned = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < 10 or area > img_area * 0.03:
                    continue
                perimeter = cv2.arcLength(cnt, True)
                if perimeter < 1:
                    continue
                circularity = 4 * np.pi * area / (perimeter ** 2)
                if circularity > 0.30:
                    M = cv2.moments(cnt)
                    if M['m00'] != 0:
                        dots.append([int(M['m10']/M['m00']), int(M['m01']/M['m00'])])
        return dots

    def _merge_nearby(self, dots, min_dist=15):
        """Deduplicate dots within min_dist pixels using a greedy merge."""
        if not dots:
            return []
        pts = np.array(dots, dtype=float)
        used = [False] * len(pts)
        merged = []
        for i in range(len(pts)):
            if used[i]:
                continue
            cluster = [pts[i]]
            for j in range(i+1, len(pts)):
                if not used[j]:
                    if np.linalg.norm(pts[i] - pts[j]) < min_dist:
                        cluster.append(pts[j])
                        used[j] = True
            merged.append(np.mean(cluster, axis=0))
            used[i] = True
        return merged

    # ── Step 3: Grid Estimation ───────────────────────────────────────────────

    def _estimate_grid(self, dots):
        if len(dots) < 4:
            return f"{len(dots)} dots"

        pts = np.array(dots)

        # Find consistent row/column spacing
        xs = sorted(set(round(p[0] / 10) * 10 for p in pts))
        ys = sorted(set(round(p[1] / 10) * 10 for p in pts))
        cols = len(xs)
        rows = len(ys)

        if rows == cols:
            return f"{rows}x{cols}"
        if abs(rows - cols) <= 2:
            return f"{min(rows,cols)}x{max(rows,cols)}"

        # Square root guess
        n = round(np.sqrt(len(dots)))
        return f"{n}x{n}" if abs(n*n - len(dots)) <= 2 else f"~{len(dots)} dots"

    # ── Step 4: Symmetry Detection ────────────────────────────────────────────

    def _detect_symmetry(self, gray):
        h, w = gray.shape
        scores = {}

        for angle in [90, 180]:
            M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
            rotated = cv2.warpAffine(gray, M, (w, h))
            scores[angle] = self._ncc(gray, rotated)

        scores['flip_h'] = self._ncc(gray, cv2.flip(gray, 1))
        scores['flip_v'] = self._ncc(gray, cv2.flip(gray, 0))

        # Diagonal symmetry — only valid for square images
        if h == w:
            scores['diag'] = self._ncc(gray, cv2.transpose(gray))
        else:
            sq = min(h, w)
            gray_sq = gray[:sq, :sq]
            scores['diag'] = self._ncc(gray_sq, cv2.transpose(gray_sq))

        THR = 0.55   # relaxed threshold for real photos

        if scores[90] > THR and (scores['flip_h'] > THR or scores['flip_v'] > THR):
            return "Rotational + Bilateral", 4
        elif scores[90] > THR:
            return "4-fold Rotational", 4
        elif scores[180] > THR:
            return "2-fold Rotational", 2
        elif scores['flip_h'] > THR and scores['flip_v'] > THR:
            return "Bilateral (H + V)", 2
        elif scores['flip_h'] > THR:
            return "Bilateral (Horizontal)", 1
        elif scores['flip_v'] > THR:
            return "Bilateral (Vertical)", 1
        elif scores['diag'] > THR:
            return "Diagonal Symmetry", 1
        else:
            return "Complex / Asymmetric", 0

    def _ncc(self, a, b):
        """Normalized cross-correlation — range [-1, 1]."""
        a = a.astype(float) - a.mean()
        b = b.astype(float) - b.mean()
        denom = np.sqrt(np.sum(a**2) * np.sum(b**2))
        return float(np.sum(a*b) / (denom + 1e-10))

    # ── Step 5: Loop Counting ─────────────────────────────────────────────────

    def _count_loops(self, gray):
        # Multi-scale edge detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 1)
        edges   = cv2.Canny(blurred, 20, 80)

        # Connect broken edges
        kernel  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        closed  = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)

        contours, hierarchy = cv2.findContours(closed, cv2.RETR_CCOMP,
                                                cv2.CHAIN_APPROX_SIMPLE)
        if hierarchy is None:
            return 1

        h_arr = hierarchy[0]
        min_area = gray.shape[0] * gray.shape[1] * 0.001   # at least 0.1% of image

        # Count top-level closed contours with significant area
        loops = sum(
            1 for i, cnt in enumerate(contours)
            if h_arr[i][3] == -1 and cv2.contourArea(cnt) > min_area
        )
        return max(1, loops)

    # ── Step 6: Stroke Type ───────────────────────────────────────────────────

    def _detect_stroke(self, gray):
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        significant = [c for c in contours if cv2.contourArea(c) > 200]
        return "Single-stroke (Sikku)" if len(significant) <= 2 else "Multi-stroke"

    # ── Step 7: Pattern Classifier ────────────────────────────────────────────

    def _cluster_1d(self, values, tol=25):
        """Cluster sorted 1-D values within tol distance; return cluster centres."""
        vals = sorted(values)
        clusters, current = [], [vals[0]]
        for v in vals[1:]:
            if v - current[-1] < tol:
                current.append(v)
            else:
                clusters.append(float(np.mean(current)))
                current = [v]
        clusters.append(float(np.mean(current)))
        return clusters

    def _grid_regularity(self, dots) -> float:
        """Score 0-1: how well dots fit a regular rectangular grid.
        Uses unique column/row positions (not raw sorted coords)."""
        if len(dots) < 4:
            return 0.5
        pts = np.array(dots, dtype=float)

        # Cluster x and y positions separately to find unique columns/rows
        unique_xs = self._cluster_1d(pts[:, 0])
        unique_ys = self._cluster_1d(pts[:, 1])

        if len(unique_xs) < 2 or len(unique_ys) < 2:
            return 0.0

        dx = np.diff(sorted(unique_xs))
        dy = np.diff(sorted(unique_ys))

        cv_x = np.std(dx) / (np.mean(dx) + 1e-9)
        cv_y = np.std(dy) / (np.mean(dy) + 1e-9)
        return float(1 / (1 + cv_x + cv_y))

    def _ring_score(self, dots) -> float:
        """Score 0-1: how well dots lie on concentric rings from centroid."""
        if len(dots) < 4:
            return 0.0
        pts    = np.array(dots, dtype=float)
        center = pts.mean(axis=0)
        dists  = np.linalg.norm(pts - center, axis=1)
        cv     = np.std(dists) / (np.mean(dists) + 1e-9)
        return float(1 / (1 + cv * 3))

    def _classify(self, dot_count, sym_fold, loop_count, grid_size, dots=None):
        """
        Calibrated on synthetic dataset feature ranges:
          Pulli   : grid 0.98-1.00  (most distinctive feature)
          Rangoli : dots 78-84
          Lotus   : dots 70-75
          Star    : dots  1-6
          Sikku   : dots 22-27, ring 0.51-0.52
          Flower  : dots  7-66, ring 0.40-0.49  (default)
        """
        ring_score = self._ring_score(dots) if dots else 0.5
        grid_score = self._grid_regularity(dots) if dots else 0.5

        # High dot counts first (Lotus can have grid=1.00 — must beat Pulli check)
        if dot_count >= 76:
            return "Rangoli Kolam"
        if dot_count >= 68:
            return "Lotus Kolam"

        # Pulli: extremely regular square grid AND low dot count
        if grid_score >= 0.95 and dot_count <= 36:
            return "Pulli Kolam"

        # Very low dot count = Star polygon vertices
        if dot_count <= 7:
            return "Star Kolam"

        # Sikku: diamond grid in 20-30 range with slightly higher ring score
        if 20 <= dot_count <= 30 and ring_score > 0.50:
            return "Sikku Kolam"
        if ring_score > 0.40:
            return "Flower Kolam"

        return "Flower Kolam"
