import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches


INPUT_FILES = [
    {
        "name": "voxel_5cm",
        "ply_path": r"G:\MID360S_AI_MAPPING\data\compressed\test01_voxel_5cm.ply",
    },
    {
        "name": "voxel_10cm",
        "ply_path": r"G:\MID360S_AI_MAPPING\data\compressed\test01_voxel_10cm.ply",
    },
    {
        "name": "voxel_20cm",
        "ply_path": r"G:\MID360S_AI_MAPPING\data\compressed\test01_voxel_20cm.ply",
    },
]

OUT_DIR = r"G:\MID360S_AI_MAPPING\outputs\compression_maps"

RESOLUTION = 0.05

Z_MIN = -1.0
Z_MAX = 1.0

MIN_POINTS_PER_CELL = 1
CAUTION_HEIGHT_RANGE = 0.15
DANGER_HEIGHT_RANGE = 0.35
DANGER_DENSITY = 20


def load_ascii_ply(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"PLY file not found: {path}")

    with open(path, "r") as f:
        lines = f.readlines()

    end_header_idx = None

    for i, line in enumerate(lines):
        if line.strip() == "end_header":
            end_header_idx = i
            break

    if end_header_idx is None:
        raise ValueError("Invalid PLY file: missing end_header")

    points = []

    for line in lines[end_header_idx + 1:]:
        parts = line.strip().split()

        if len(parts) < 4:
            continue

        x, y, z, intensity = map(float, parts[:4])
        points.append((x, y, z, intensity))

    return np.array(points, dtype=np.float32)


def filter_points(points):
    distance = np.linalg.norm(points[:, :3], axis=1)
    points = points[distance > 0.05]

    z = points[:, 2]
    points = points[(z > Z_MIN) & (z < Z_MAX)]

    return points


def create_grids(points):
    x = points[:, 0]
    y = points[:, 1]
    z = points[:, 2]

    x_min, x_max = np.min(x), np.max(x)
    y_min, y_max = np.min(y), np.max(y)

    width = int(np.ceil((x_max - x_min) / RESOLUTION)) + 1
    height = int(np.ceil((y_max - y_min) / RESOLUTION)) + 1

    count_grid = np.zeros((height, width), dtype=np.uint16)

    min_z_grid = np.full((height, width), np.inf, dtype=np.float32)
    max_z_grid = np.full((height, width), -np.inf, dtype=np.float32)

    ix = ((x - x_min) / RESOLUTION).astype(np.int32)
    iy = ((y - y_min) / RESOLUTION).astype(np.int32)

    valid = (
        (ix >= 0) & (ix < width) &
        (iy >= 0) & (iy < height)
    )

    ix = ix[valid]
    iy = iy[valid]
    z = z[valid]

    np.add.at(count_grid, (iy, ix), 1)
    np.minimum.at(min_z_grid, (iy, ix), z)
    np.maximum.at(max_z_grid, (iy, ix), z)

    height_range_grid = max_z_grid - min_z_grid

    height_range_grid[count_grid == 0] = 0.0
    min_z_grid[count_grid == 0] = 0.0
    max_z_grid[count_grid == 0] = 0.0

    return count_grid, height_range_grid


def create_risk_grid(count_grid, height_range_grid):
    risk_grid = np.zeros_like(count_grid, dtype=np.uint8)

    low_risk_mask = (
        (count_grid >= MIN_POINTS_PER_CELL) &
        (height_range_grid < CAUTION_HEIGHT_RANGE)
    )

    caution_mask = (
        (count_grid >= MIN_POINTS_PER_CELL) &
        (height_range_grid >= CAUTION_HEIGHT_RANGE) &
        (height_range_grid < DANGER_HEIGHT_RANGE)
    )

    danger_height_mask = (
        (count_grid >= MIN_POINTS_PER_CELL) &
        (height_range_grid >= DANGER_HEIGHT_RANGE)
    )

    danger_density_mask = count_grid >= DANGER_DENSITY

    risk_grid[low_risk_mask] = 1
    risk_grid[caution_mask] = 2
    risk_grid[danger_height_mask] = 3
    risk_grid[danger_density_mask] = 3

    return risk_grid


def save_occupancy_map(count_grid, output_path, title):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    grid_log = np.log1p(count_grid)

    plt.figure(figsize=(10, 10))
    plt.imshow(grid_log, origin="lower")
    plt.title(title)
    plt.xlabel("X grid")
    plt.ylabel("Y grid")
    plt.colorbar(label="log(point count)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def save_height_range_map(height_range_grid, output_path, title):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.figure(figsize=(10, 10))
    plt.imshow(height_range_grid, origin="lower")
    plt.title(title)
    plt.xlabel("X grid")
    plt.ylabel("Y grid")
    plt.colorbar(label="height range (m)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def save_risk_map(risk_grid, output_path, title):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmap = ListedColormap([
        "black",
        "green",
        "yellow",
        "red"
    ])

    plt.figure(figsize=(10, 10))
    plt.imshow(risk_grid, origin="lower", cmap=cmap, vmin=0, vmax=3)

    plt.title(title)
    plt.xlabel("X grid")
    plt.ylabel("Y grid")

    legend_items = [
        mpatches.Patch(color="black", label="Unknown / Empty"),
        mpatches.Patch(color="green", label="Low Risk / Flat"),
        mpatches.Patch(color="yellow", label="Caution / Uneven"),
        mpatches.Patch(color="red", label="Danger / Obstacle"),
    ]

    plt.legend(handles=legend_items, loc="upper right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    summary_rows = []

    for item in INPUT_FILES:
        name = item["name"]
        ply_path = item["ply_path"]

        print("=" * 70)
        print(f"Processing: {name}")
        print(f"PLY: {ply_path}")

        points = load_ascii_ply(ply_path)
        raw_count = len(points)
        print(f"Loaded points: {raw_count}")

        points = filter_points(points)
        filtered_count = len(points)
        print(f"Filtered points: {filtered_count}")

        count_grid, height_range_grid = create_grids(points)
        risk_grid = create_risk_grid(count_grid, height_range_grid)

        occupied_cells = np.sum(count_grid > 0)
        unknown_cells = np.sum(risk_grid == 0)
        low_cells = np.sum(risk_grid == 1)
        caution_cells = np.sum(risk_grid == 2)
        danger_cells = np.sum(risk_grid == 3)

        max_height_range = np.max(height_range_grid)
        max_density = np.max(count_grid)

        print(f"Grid shape: {count_grid.shape}")
        print(f"Occupied cells: {occupied_cells}")
        print(f"Max density: {max_density}")
        print(f"Max height range: {max_height_range:.3f}")
        print(f"Low-risk cells: {low_cells}")
        print(f"Caution cells: {caution_cells}")
        print(f"Danger cells: {danger_cells}")

        occupancy_path = os.path.join(OUT_DIR, f"occupancy_{name}.png")
        height_path = os.path.join(OUT_DIR, f"height_range_{name}.png")
        risk_path = os.path.join(OUT_DIR, f"risk_{name}.png")

        save_occupancy_map(
            count_grid,
            occupancy_path,
            f"Occupancy Map - {name}"
        )

        save_height_range_map(
            height_range_grid,
            height_path,
            f"Height Range Map - {name}"
        )

        save_risk_map(
            risk_grid,
            risk_path,
            f"Height-Aware Risk Map - {name}"
        )

        summary_rows.append([
            name,
            raw_count,
            filtered_count,
            count_grid.shape[0],
            count_grid.shape[1],
            occupied_cells,
            max_density,
            max_height_range,
            low_cells,
            caution_cells,
            danger_cells,
            occupancy_path,
            height_path,
            risk_path
        ])

    summary_path = os.path.join(OUT_DIR, "compressed_map_quality_summary.csv")

    with open(summary_path, "w") as f:
        f.write(
            "name,raw_points,filtered_points,grid_height,grid_width,"
            "occupied_cells,max_density,max_height_range,"
            "low_risk_cells,caution_cells,danger_cells,"
            "occupancy_path,height_range_path,risk_path\n"
        )

        for row in summary_rows:
            f.write(",".join(map(str, row)) + "\n")

    print("=" * 70)
    print(f"Saved summary: {summary_path}")


if __name__ == "__main__":
    main()