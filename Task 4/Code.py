


import os
import sys
import heapq
import numpy as np
import cv2

INPUT_IMAGE = r"C:\Users\Dell\Desktop\Soumye Chauhan 26-B3-39\Task 4\Input\1.jpeg"         
OUTPUT_IMAGE = r"C:\Users\Dell\Desktop\Soumye Chauhan 26-B3-39\Task 4\Output\track_path.png"    




def segment_road(img):
    """
    The road is a smooth, low-noise grey band; the background is a similarly
    coloured but visibly noisier/grainier texture.  We exploit this using a
    local standard-deviation filter: low local std -> road, higher -> background.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)

    k = 15
    mean = cv2.blur(gray, (k, k))
    sq_mean = cv2.blur(gray * gray, (k, k))
    var = np.maximum(sq_mean - mean * mean, 0)
    std = np.sqrt(var)

    smooth_mask = (std < 2.0).astype(np.uint8) * 255
    kernel = np.ones((5, 5), np.uint8)
    smooth_mask = cv2.morphologyEx(smooth_mask, cv2.MORPH_OPEN, kernel)
    smooth_mask = cv2.morphologyEx(smooth_mask, cv2.MORPH_CLOSE, kernel)

    
    n, labels, stats, _ = cv2.connectedComponentsWithStats(smooth_mask, 8)
    areas = stats[:, cv2.CC_STAT_AREA].copy()
    areas[0] = 0
    largest = int(np.argmax(areas))
    road_mask = (labels == largest).astype(np.uint8) * 255

    road_mask = cv2.morphologyEx(road_mask, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    return road_mask



def segment_obstacles(img):
   
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    S, V = hsv[:, :, 1], hsv[:, :, 2]

    raw = ((S > 40) | (V > 115) | (V < 58)).astype(np.uint8) * 255

    b, g, r = img[:, :, 0].astype(int), img[:, :, 1].astype(int), img[:, :, 2].astype(int)
    pure_white = ((b > 240) & (g > 240) & (r > 240)).astype(np.uint8) * 255
    pure_white = cv2.dilate(pure_white, np.ones((5, 5), np.uint8))

    obstacle_mask = cv2.bitwise_and(raw, cv2.bitwise_not(pure_white))
    obstacle_mask = cv2.morphologyEx(obstacle_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

    return obstacle_mask, pure_white


def find_start_point(pure_white_mask):
    
    n, labels, stats, centroids = cv2.connectedComponentsWithStats(pure_white_mask, 8)
    best_label, best_score = None, -1
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if area < 30:
            continue
        elongation = max(w, h) / max(1, min(w, h))
      
        score = elongation * (h if h > w else w)
        if h > w and elongation > best_score:
            best_score = elongation
            best_label = i

    if best_label is None:
        
        best_label = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))

    ys, xs = np.where(labels == best_label)
    tip_y = ys.max()
    tip_x = int(xs[ys == tip_y].mean())
    # step a few pixels further along the arrow direction onto the road
    top_y = ys.min()
    top_x = int(xs[ys == top_y].mean())
    dx, dy = tip_x - top_x, tip_y - top_y
    norm = max(1.0, (dx ** 2 + dy ** 2) ** 0.5)
    ext = 10
    start_x = int(tip_x + ext * dx / norm)
    start_y = int(tip_y + ext * dy / norm)
    return start_x, start_y



def build_safe_mask(road_mask, obstacle_mask, safety_margin=14):
    .
    near_road = cv2.dilate(road_mask, np.ones((41, 41), np.uint8))
    fill = cv2.bitwise_and(obstacle_mask, near_road)
    road_full = cv2.bitwise_or(road_mask, fill)
    road_full = cv2.morphologyEx(road_full, cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8))

    obstacle_dilated = cv2.dilate(obstacle_mask, np.ones((safety_margin * 2 + 1,) * 2, np.uint8))
    safe_mask = cv2.bitwise_and(road_full, cv2.bitwise_not(obstacle_dilated))
    safe_mask = cv2.morphologyEx(safe_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return road_full, safe_mask



def hole_centroid(road_full_mask):
    """Centroid of the enclosed hole inside the road loop."""
    contours, hierarchy = cv2.findContours(road_full_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    hierarchy = hierarchy[0]
    best = None
    best_area = 0
    for i, h in enumerate(hierarchy):
        if h[3] != -1:  # has a parent -> it's a hole contour
            area = cv2.contourArea(contours[i])
            if area > best_area:
                best_area = area
                best = contours[i]
    M = cv2.moments(best)
    cx = M["m10"] / M["m00"]
    cy = M["m01"] / M["m00"]
    return cx, cy


def radial_waypoints(safe_mask, cx, cy, n_angles=720):

    h, w = safe_mask.shape
    max_r = int(np.hypot(w, h))
    waypoints = [None] * n_angles

    for i in range(n_angles):
        theta = 2 * np.pi * i / n_angles
        dx, dy = np.cos(theta), np.sin(theta)

        runs = []
        in_run = False
        run_start = 0
        for r in range(0, max_r, 2):
            x = int(round(cx + r * dx))
            y = int(round(cy + r * dy))
            if not (0 <= x < w and 0 <= y < h):
                val = 0
            else:
                val = safe_mask[y, x]
            if val > 0 and not in_run:
                in_run = True
                run_start = r
            elif val == 0 and in_run:
                in_run = False
                runs.append((run_start, r))
        if in_run:
            runs.append((run_start, max_r))

        if not runs:
            waypoints[i] = None
            continue

       
        run_start, run_end = max(runs, key=lambda t: t[1] - t[0])
        r_mid = 0.5 * (run_start + run_end)
        wx = cx + r_mid * dx
        wy = cy + r_mid * dy
        waypoints[i] = (wx, wy)

    return waypoints


def order_from_start(waypoints, cx, cy, start_xy):
    n = len(waypoints)
    sx, sy = start_xy
    start_theta = np.arctan2(sy - cy, sx - cx) % (2 * np.pi)
    start_idx = int(round(start_theta / (2 * np.pi) * n)) % n

    ordered = []
    for k in range(n + 1):  # +1 to close the loop back to the starting angle
        idx = (start_idx + k) % n
        if waypoints[idx] is not None:
            ordered.append(waypoints[idx])
    return ordered



def segment_is_safe(safe_mask, p1, p2, samples=25):
    h, w = safe_mask.shape
    for t in np.linspace(0, 1, samples):
        x = int(round(p1[0] + t * (p2[0] - p1[0])))
        y = int(round(p1[1] + t * (p2[1] - p1[1])))
        if not (0 <= x < w and 0 <= y < h) or safe_mask[y, x] == 0:
            return False
    return True


def astar_repair(safe_mask, p1, p2, cell=4):
   
    h, w = safe_mask.shape

    def to_cell(pt):
        return (int(pt[1] // cell), int(pt[0] // cell))

    def to_xy(c):
        return (c[1] * cell + cell // 2, c[0] * cell + cell // 2)

    small = cv2.resize(safe_mask, (w // cell, h // cell), interpolation=cv2.INTER_NEAREST)
    H, W = small.shape

    start = to_cell(p1)
    goal = to_cell(p2)
    start = (min(max(start[0], 0), H - 1), min(max(start[1], 0), W - 1))
    goal = (min(max(goal[0], 0), H - 1), min(max(goal[1], 0), W - 1))

    def passable(c):
        r, cc = c
        return 0 <= r < H and 0 <= cc < W and small[r, cc] > 0

    neighbours = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def h_cost(a, b):
        return np.hypot(a[0] - b[0], a[1] - b[1])

    openq = [(0, start)]
    came, gscore = {}, {start: 0}
    visited = set()
    while openq:
        _, cur = heapq.heappop(openq)
        if cur in visited:
            continue
        visited.add(cur)
        if cur == goal:
            break
        for drc, dcc in neighbours:
            nb = (cur[0] + drc, cur[1] + dcc)
            if not passable(nb):
                continue
            step = np.hypot(drc, dcc)
            ng = gscore[cur] + step
            if ng < gscore.get(nb, 1e18):
                gscore[nb] = ng
                came[nb] = cur
                heapq.heappush(openq, (ng + h_cost(nb, goal), nb))

    if goal not in came and goal != start:
        return [p1, p2]  # give up, caller will just keep the straight segment

    path = [goal]
    while path[-1] != start:
        path.append(came[path[-1]])
    path.reverse()
    return [to_xy(c) for c in path]


def make_path_safe(safe_mask, waypoints):
    
    safe_path = [waypoints[0]]
    for p in waypoints[1:]:
        prev = safe_path[-1]
        if segment_is_safe(safe_mask, prev, p):
            safe_path.append(p)
        else:
            detour = astar_repair(safe_mask, prev, p)
            safe_path.extend(detour[1:])
    return safe_path


def smooth_path(path, window=9):
    pts = np.array(path, dtype=np.float32)
    n = len(pts)
    if n < window:
        return path
    kernel = np.ones(window) / window
    pad = window // 2
    xs = np.pad(pts[:, 0], (pad, pad), mode="wrap")
    ys = np.pad(pts[:, 1], (pad, pad), mode="wrap")
    xs_s = np.convolve(xs, kernel, mode="valid")
    ys_s = np.convolve(ys, kernel, mode="valid")
    return list(zip(xs_s.tolist(), ys_s.tolist()))



def draw_path(img, path, start_xy):
    out = img.copy()
    n = len(path)
    for i in range(n - 1):
        t = i / max(1, n - 2)
        color = (
            int(60 + 120 * t),        # B
            int(60 + 140 * (1 - t)),  # G
            int(230 - 60 * t),        # R
        )
        p1 = tuple(np.round(path[i]).astype(int))
        p2 = tuple(np.round(path[i + 1]).astype(int))
        cv2.line(out, p1, p2, color, 6, cv2.LINE_AA)

    cv2.circle(out, (int(start_xy[0]), int(start_xy[1])), 12, (0, 255, 0), -1)
    cv2.circle(out, (int(start_xy[0]), int(start_xy[1])), 12, (0, 0, 0), 2)
    cv2.putText(out, "START/FINISH", (int(start_xy[0]) + 16, int(start_xy[1])),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(out, "START/FINISH", (int(start_xy[0]) + 16, int(start_xy[1])),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1, cv2.LINE_AA)
    return out


def plan_track_path(image_path, output_path, safety_margin=14, n_angles=720):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    road_mask = segment_road(img)
    obstacle_mask, pure_white = segment_obstacles(img)
    road_full, safe_mask = build_safe_mask(road_mask, obstacle_mask, safety_margin)

    start_xy = find_start_point(pure_white)

    cx, cy = hole_centroid(road_full)
    raw_waypoints = radial_waypoints(safe_mask, cx, cy, n_angles=n_angles)
    ordered = order_from_start(raw_waypoints, cx, cy, start_xy)

  
    ordered = [start_xy] + ordered + [start_xy]

    safe_ordered = make_path_safe(safe_mask, ordered)
    final_path = smooth_path(safe_ordered, window=11)
    final_path = make_path_safe(safe_mask, final_path)  # re-validate after smoothing
    final_path[0] = start_xy
    final_path[-1] = start_xy

    result_img = draw_path(img, final_path, start_xy)

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    cv2.imwrite(output_path, result_img)

    debug = {
        "road_mask": road_mask,
        "obstacle_mask": obstacle_mask,
        "safe_mask": safe_mask,
        "road_full": road_full,
    }
    return result_img, final_path, start_xy, debug


# --------------------------------------------------------------------------- #
if __name__ == "__main__":

    if len(sys.argv) >= 2:
        in_path = sys.argv[1]
        out_path = sys.argv[2] if len(sys.argv) >= 3 else "track_path.png"
    else:
        in_path = INPUT_IMAGE
        out_path = OUTPUT_IMAGE

    print(f"Processing {in_path} -> {out_path}")
    _, path, start_xy, _ = plan_track_path(in_path, out_path)
    print(f"Done. start={start_xy}  path points={len(path)}")