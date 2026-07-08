import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches

##################################################
# Here are the File Path one is input .ply file and one is output location
# PLY_PATH = "data/mid360s_test_01.ply" # The file that currently read in.
PLY_PATH = r"G:\MID360S_AI_MAPPING\data\mid360s_test_01.ply"
# OUT_PATH = "outputs/height_risk_map.png"
OUT_PATH = r"G:\MID360S_AI_MAPPING\outputs\height_risk_map.png"

DENSITY_DEBUG_PATH = "outputs/debug_density_map.png"
HEIGHT_DEBUG_PATH = "outputs/debug_height_range_map.png"
##################################################

# Each grid cell represents 5 cm x 5cm
RESOLUTION = 0.05 # Each little grid cell represent real word 0.05 meter which is 5 cm
# For Example: in the real world x = 1 m and y = 2 m than the grid_x = 1 / 0.05 = 20 and grid_y = 2 /0.05 = 40
# Since the point cloud is using x & y but map is using grid cell we need to defend the size of the grid
# If decrease the Resolution = 0.02 than the map will be more thin and calculation will be more also increase the noise
# If increase the Resolution = 0.1 than the map will be more rough but more stabilize.
# In this case we will use 5 cm since it is in between.
# (In the future we will test it out to see which range will be better this is a point we can put into the report.)


# Height filter in meters
# We will only include the points from -2m to 2m from z direction.
# This will change later when we analyze under different situation
# (In the future we will test it out to see which range will be better this is a point we can put into the report.)
Z_MIN = -1.0
Z_MAX = 1.0


# Risk thresholds
# This we use to check if the points in a grid is less than 3 we will avoid it.
MIN_POINTS_PER_CELL = 3

# If the difference of the height in a grid is larger than 15 cm mark it as yellow.
CAUTION_HEIGHT_RANGE = 0.15

# If the difference of the height in a grid is larger than 35 cm mark it as red.
DANGER_HEIGHT_RANGE = 0.35

# If the density of a grid is very large we also mark it as danger.
DANGER_DENSITY = 100

def load_ascii_ply(path: str) -> np.ndarray:
    """
    Load an ASCII PLY file with x, y, z, intensity fields.

    Returns:
        NumPy array with shape (N, 4)
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"PLY file not found: {path}")

    with open(path, "r") as file:
        lines = file.readlines()

    end_header_index = None

    for i, line in enumerate(lines):
        if line.strip() == "end_header":
            end_header_index = i
            break

    if end_header_index is None:
        raise ValueError("Invalid PLY file: missing end_header")

    points = []

    for line in lines[end_header_index + 1:]:
        parts = line.split()

        if len(parts) < 4:
            continue

        x, y, z, intensity = map(float, parts[:4])
        points.append((x, y, z, intensity))

    return np.array(points, dtype=np.float32)


def filter_points(points: np.ndarray) -> np.ndarray:
    """
    Remove invalid points and filter by height.
    """

    # Remove points near the origin, usually invalid or zero points.
    # Here we pick the first 3 points which are x, y, z; We don't take in the intensity here.
    # Then we try to find the distance from the current point to the origin.
    # The formular: distance = sqrt(x^2 + y^2 + z^2)
    # Euclidean norm, magnitude, or length of the vector ||P||
    distance = np.linalg.norm(points[:, :3], axis=1)
    # Then we will check the points in the list if the distance is larger than 0.05m which is 5cm we will take in the points
    # If the distance is less than 5 cm we will avoid.
    points = points[distance > 0.05]

    # Height filter
    # Here we filter out only the z points.
    z = points[:, 2]
    # Then we will filter out the points which in the range of z:[-2,2].
    points = points[(z > Z_MIN) & (z < Z_MAX)]

    return points


def create_height_grids(points: np.ndarray):
    """
    Project 3D points onto the XY plane and compute grid-level statistics.

    For each grid cell, this function calculates:
        - point count
        - minimum z value
        - maximum z value
        - height range = max_z - min_z

    Returns:
        count_grid, min_z_grid, max_z_grid, height_range_grid
    """

    x = points[:, 0]
    y = points[:, 1]
    z = points[:, 2]

    x_min, x_max = np.min(x), np.max(x)
    y_min, y_max = np.min(y), np.max(y)

    # This will tell us how big (how many of grid cell) is the map
    width = int(np.ceil((x_max - x_min) / RESOLUTION)) + 1
    height = int(np.ceil((y_max - y_min) / RESOLUTION)) + 1

    # Here we will build a 2D matrix all the grid start with 0 with size of above "width and height"
    count_grid = np.zeros((height, width), dtype=np.uint16)

    min_z_grid = np.full((height, width), np.inf, dtype=np.float32)
    max_z_grid = np.full((height, width), -np.inf, dtype=np.float32)

    # Here we need to find the grid location of each x and y
    # We do - x_min or y_min because we need to shift every point to start from origin
    ix = ((x - x_min) / RESOLUTION).astype(np.int32)
    iy = ((y - y_min) / RESOLUTION).astype(np.int32)

    # Here we will check for the valid points make sure the points are positive and not passing the boundry
    valid = (
            (ix >= 0) & (ix < width) & (iy >= 0) & (iy < height)
    )

    ix = ix[valid]
    iy = iy[valid]
    z = z[valid]

    for grid_x, grid_y, point_z in zip(ix, iy, z):
        count_grid[grid_y, grid_x] += 1

        if point_z < min_z_grid[grid_y, grid_x]:
            min_z_grid[grid_y, grid_x] = point_z

        if point_z > max_z_grid[grid_y, grid_x]:
            max_z_grid[grid_y, grid_x] = point_z

    height_range_grid = max_z_grid - min_z_grid

    height_range_grid[count_grid == 0] = 0.0
    min_z_grid[count_grid == 0] = 0.0
    max_z_grid[count_grid == 0] = 0.0

    return count_grid, min_z_grid, max_z_grid, height_range_grid


def create_height_risk_grid(
    count_grid: np.ndarray,
    height_range_grid: np.ndarray
) -> np.ndarray:
    """
    Convert density and height variation into a risk map.

    Risk labels:
        0 = unknown / empty
        1 = low risk / likely flat surface
        2 = caution / uneven or uncertain area
        3 = danger / obstacle or large height variation
    """

    risk_grid = np.zeros_like(count_grid, dtype=np.uint8)

    # If a cell has enough points and low height variation, treat it as low risk.
    low_risk_mask = (
        (count_grid >= MIN_POINTS_PER_CELL) &
        (height_range_grid < CAUTION_HEIGHT_RANGE)
    )
    risk_grid[low_risk_mask] = 1

    # If height variation is medium, mark as caution.
    caution_mask = (
        (count_grid >= MIN_POINTS_PER_CELL) &
        (height_range_grid >= CAUTION_HEIGHT_RANGE) &
        (height_range_grid < DANGER_HEIGHT_RANGE)
    )
    risk_grid[caution_mask] = 2

    # If height variation is large, mark as danger.
    danger_height_mask = (
        (count_grid >= MIN_POINTS_PER_CELL) &
        (height_range_grid >= DANGER_HEIGHT_RANGE)
    )
    risk_grid[danger_height_mask] = 3

    # If density is extremely high, also mark as danger.
    danger_density_mask = count_grid >= DANGER_DENSITY
    risk_grid[danger_density_mask] = 3

    return risk_grid

def save_density_debug_map(count_grid: np.ndarray, output_path: str):
    # The brighter it is means the more points there are.
    """
    Save a debug image showing point density per grid cell.
    This helps us see which areas have many LiDAR points.
    """

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    density_log = np.log1p(count_grid)

    plt.figure(figsize=(10, 10))
    plt.imshow(density_log, origin="lower")
    plt.title("Debug: Point Density Map")
    plt.xlabel("X grid")
    plt.ylabel("Y grid")
    plt.colorbar(label="log(point count)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

def save_height_range_debug_map(height_range_grid: np.ndarray, output_path: str):
    # This will show the height difference (z axis)
    """
    Save a debug image showing height variation per grid cell.
    This helps us see which areas have large vertical changes.
    """

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.figure(figsize=(10, 10))
    plt.imshow(height_range_grid, origin="lower")
    plt.title("Debug: Height Range Map")
    plt.xlabel("X grid")
    plt.ylabel("Y grid")
    plt.colorbar(label="height range (m)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

def save_height_risk_map(risk_grid: np.ndarray, output_path: str):
    """
    Save height-aware risk grid as a colored PNG image.
    """

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmap = ListedColormap([
        "black",    # unknown
        "green",    # low risk
        "yellow",   # caution
        "red"       # danger
    ])

    plt.figure(figsize=(10, 10))
    plt.imshow(risk_grid, origin="lower", cmap=cmap, vmin=0, vmax=3)

    plt.title("Mid-360S Height-Aware Risk Map")
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
    plt.savefig(output_path, dpi=200)
    plt.close()

def main():
    print(f"Loading point cloud: {PLY_PATH}")

    points = load_ascii_ply(PLY_PATH)
    print(f"Raw points: {len(points)}")

    points = filter_points(points)
    print(f"Filtered points: {len(points)}")

    count_grid, min_z_grid, max_z_grid, height_range_grid = create_height_grids(points)

    print(f"Count grid shape: {count_grid.shape}")
    print(f"Min z: {np.min(min_z_grid):.3f}")
    print(f"Max z: {np.max(max_z_grid):.3f}")
    print(f"Max height range: {np.max(height_range_grid):.3f}")

    risk_grid = create_height_risk_grid(count_grid, height_range_grid)
    save_density_debug_map(count_grid, DENSITY_DEBUG_PATH)
    save_height_range_debug_map(height_range_grid, HEIGHT_DEBUG_PATH)

    print(f"Unknown cells: {np.sum(risk_grid == 0)}")
    print(f"Low-risk cells: {np.sum(risk_grid == 1)}")
    print(f"Caution cells: {np.sum(risk_grid == 2)}")
    print(f"Danger cells: {np.sum(risk_grid == 3)}")

    save_height_risk_map(risk_grid, OUT_PATH)

    print(f"Height-aware risk map saved to: {OUT_PATH}")
    print(f"Density debug map saved to: {DENSITY_DEBUG_PATH}")
    print(f"Height range debug map saved to: {HEIGHT_DEBUG_PATH}")

if __name__ == "__main__":
    main()