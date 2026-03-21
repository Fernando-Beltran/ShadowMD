import json
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image


IMG_PATH = r"C:\\Users\\Fernando\\.cursor\\projects\\d-Cursor-R2D2\\assets\\d__Cursor_R2D2_serial-web-console_r2d2plans.png"


@dataclass
class Blob:
    color: str
    area: int
    cx: float
    cy: float
    minx: int
    miny: int
    maxx: int
    maxy: int


def connected_components(mask: np.ndarray) -> List[Tuple[np.ndarray, int]]:
    """
    Simple 4-neighbor BFS connected components on a boolean 2D mask.
    Returns a list of (indices_array, area).
    """
    h, w = mask.shape
    visited = np.zeros((h, w), dtype=bool)
    blobs: List[Tuple[np.ndarray, int]] = []

    # Precompute neighbors
    neigh = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for y in range(h):
        row = mask[y]
        # Find first unvisited True pixel in this row
        for x in np.where(row & (~visited[y]))[0]:
            if visited[y, x] or not mask[y, x]:
                continue

            queue = [(y, x)]
            visited[y, x] = True
            coords = []

            while queue:
                cy, cx = queue.pop()
                coords.append((cy, cx))
                for dy, dx in neigh:
                    ny, nx = cy + dy, cx + dx
                    if ny < 0 or nx < 0 or ny >= h or nx >= w:
                        continue
                    if visited[ny, nx] or not mask[ny, nx]:
                        continue
                    visited[ny, nx] = True
                    queue.append((ny, nx))

            coords_np = np.array(coords, dtype=np.int32)
            blobs.append((coords_np, coords_np.shape[0]))

    return blobs


def downsample_mask(mask: np.ndarray, stride: int) -> np.ndarray:
    # keep True if any sampled point is True
    m = mask[0 : mask.shape[0] - (mask.shape[0] % stride), 0 : mask.shape[1] - (mask.shape[1] % stride)]
    m = m.reshape(m.shape[0] // stride, stride, m.shape[1] // stride, stride)
    m = m.any(axis=(1, 3))
    return m


def main() -> None:
    img = Image.open(IMG_PATH).convert("RGB")
    arr = np.array(img)
    h, w = arr.shape[:2]

    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]

    # These thresholds are tuned for the provided PNG.
    # The "red" circles are more orange in the provided reference image,
    # so we allow a wider (g) range.
    red = (r > 150) & (b < 140) & (g < 200) & (g > 40)
    # Blue circles: strong blue with limited red.
    blue = (b > 140) & (r < 140) & (g < 210) & (b > g) & (b > r)
    # Green circles: strong green.
    green = (g > 140) & (r < 190) & (b < 190) & (g > r) & (g > b)

    stride = 2  # more precise circle detection
    results: Dict[str, List[Blob]] = {"red": [], "blue": [], "green": []}

    for name, m in [("red", red), ("blue", blue), ("green", green)]:
        mds = downsample_mask(m, stride=stride)
        comps = connected_components(mds)

        # Convert component coords from ds-grid back to original pixel coords
        # Filter by area (tuned to circles)
        for coords_np, area_ds in comps:
            # Keep smaller blobs too; we will filter manually if needed.
            if area_ds < 12:
                continue
            ys = coords_np[:, 0]
            xs = coords_np[:, 1]
            cy_ds = float(ys.mean())
            cx_ds = float(xs.mean())

            minx_ds = int(xs.min())
            maxx_ds = int(xs.max())
            miny_ds = int(ys.min())
            maxy_ds = int(ys.max())

            # Map back to approximate original pixel coords
            cx = cx_ds * stride + stride / 2
            cy = cy_ds * stride + stride / 2

            blob = Blob(
                color=name,
                area=int(area_ds),
                cx=cx,
                cy=cy,
                minx=minx_ds * stride,
                miny=miny_ds * stride,
                maxx=maxx_ds * stride,
                maxy=maxy_ds * stride,
            )
            results[name].append(blob)

        # Sort left-to-right then top-to-bottom for stable output
        results[name].sort(key=lambda x: (x.cy, x.cx))

    out = {
        "img_size": {"w": w, "h": h},
        "stride": stride,
        "counts": {k: len(v) for k, v in results.items()},
        "blobs": {
            k: [
                {
                    "area": b.area,
                    "cx": round(b.cx, 2),
                    "cy": round(b.cy, 2),
                    "minx": b.minx,
                    "miny": b.miny,
                    "maxx": b.maxx,
                    "maxy": b.maxy,
                }
                for b in v
            ]
            for k, v in results.items()
        },
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

