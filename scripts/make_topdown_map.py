import numpy as np
import matplotlib.pyplot as plt


PLY_PATH = "data/mid360s_test_01.ply"
OUT_PATH = "outputs/topdown_map.png"

# grid resolution in meters
RESOLUTION = 0.05

# height filter, adjust later
Z_MIN = -2.0
Z_MAX = 2.0


def load_ascii_ply(path):
    with open(path, "r") as f:
        lines = f.readlines()

    end_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "end_header":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError("Invalid PLY: no end_header found")

    data = []
    for line in lines[end_idx + 1:]:
        parts = line.strip().split()
        if len(parts) >= 4:
            data.append([float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3])])

    return np.array(data, dtype=np.float32)


def main():
    print(f"Loading {PLY_PATH} ...")
    points = load_ascii_ply(PLY_PATH)
    print(f"Loaded points: {points.shape[0]}")

    # remove all-zero points
    nonzero = np.linalg.norm(points[:, :3], axis=1) > 0.05
    points = points[nonzero]

    # height filter
    z_filter = (points[:, 2] > Z_MIN) & (points[:, 2] < Z_MAX)
    points = points[z_filter]

    print(f"After filtering: {points.shape[0]}")

    x = points[:, 0]
    y = points[:, 1]

    x_min, x_max = np.min(x), np.max(x)
    y_min, y_max = np.min(y), np.max(y)

    width = int(np.ceil((x_max - x_min) / RESOLUTION)) + 1
    height = int(np.ceil((y_max - y_min) / RESOLUTION)) + 1

    grid = np.zeros((height, width), dtype=np.uint16)

    ix = ((x - x_min) / RESOLUTION).astype(np.int32)
    iy = ((y - y_min) / RESOLUTION).astype(np.int32)

    valid = (ix >= 0) & (ix < width) & (iy >= 0) & (iy < height)
    ix = ix[valid]
    iy = iy[valid]

    for gx, gy in zip(ix, iy):
        grid[gy, gx] += 1

    # log scale for visibility
    grid_log = np.log1p(grid)

    plt.figure(figsize=(10, 10))
    plt.imshow(grid_log, origin="lower")
    plt.title("Mid-360S Top-Down Occupancy Map")
    plt.xlabel("X grid")
    plt.ylabel("Y grid")
    plt.colorbar(label="log(point count)")
    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=200)
    print(f"Saved map to {OUT_PATH}")


if __name__ == "__main__":
    main()