import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches

##################################################
# Here are the File Path one is input .ply file and one is output location
PLY_PATH = "data/mid360s_test_01.ply" # The file that currently read in.
# PLY_PATH = r"G:\MID360S_AI_MAPPING\data\mid360s_test_01.ply"
OUT_PATH = "outputs/risk_map.png"
# OUT_PATH = r"G:\MID360S_AI_MAPPING\outputs\risk_map.png"
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
Z_MIN = -2.0
Z_MAX = 2.0

# Set up the thresholds values: Caution threshold is 20 counts & Danger threshold is 80 counts.
# If there are little many points in a grid: Low risk.
# If there are 20 points in a grid: Caution.
# If there are 80 points in a grid: It could be a wall or object we will say it is danger.
# (In the future we will test it out to see which range will be better this is a point we can put into the report.)
CAUTION_COUNT = 20
DANGER_COUNT = 80


def load_ascii_ply(path: str) -> np.ndarray: # Read from .ply file and covert it to numpy array.
    """
        Load an ASCII PLY file with x, y, z, intensity fields.

        Expected format:
            x y z intensity

        Returns:
            NumPy array with shape (N, 4)
    """

    if not os.path.exists(path): # Check if the path exists or not, if not show error
        raise FileNotFoundError(f"PLY file not found: {path}")

    with open(path, "r") as file: # This will read all the lines in the data set
        lines = file.readlines()

    ####################################################
    # Here we will find the index of the "end_header" because the real data points are after these.
    end_header_index = None
    for i, line in enumerate(lines):
        if line.strip() == "end_header":
            end_header_index = i
            break
    ####################################################

    if end_header_index is None: # Check if "end_header" exists, if not output error.
        raise ValueError("Invalid PLY file: missing end_header")

    ####################################################
    # Split the dataset and put the datas into the list "points"
    # The final return will be something like (N,4) e.g(1000032,4) N means number of rows and 4 means 4 columns
    # Each row represent one points
    points = []
    for line in lines[end_header_index + 1:]:
        parts = line.split()

        if len(parts) < 4:
            continue

        x, y, z, intensity = map(float, parts[:4])
        points.append((x, y, z, intensity))
    ####################################################

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

def create_density_grid(points: np.ndarray):
    """
    Project 3D points onto XY plane and count points per grid cell.

    Returns:
        count_grid, x_min, y_min
    """

    x = points[:, 0] # Get all the x points in the dataset
    y = points[:, 1] # Get all the y points in the dataset

    # Base on these values we can find the range of the area
    x_min, x_max = np.min(x), np.max(x) # Get the min x value and max x value
    y_min, y_max = np.min(y), np.max(y) # Get the min y value and max y value

    # This will tell us how big (how many of grid cell) is the map
    width = int(np.ceil((x_max - x_min) / RESOLUTION)) + 1
    height = int(np.ceil((y_max - y_min) / RESOLUTION)) + 1

    # Here we will build a 2D matrix all the grid start with 0 with size of above "width and height"
    count_grid = np.zeros((height, width), dtype=np.uint16)
    # 00000
    # 00000  If there is a point land in any of those boxes we will + 1
    # 00000

    # Here we need to find the grid location of each x and y
    # We do - x_min or y_min because we need to shift every point to start from origin
    ix = ((x - x_min) / RESOLUTION).astype(np.int32)
    iy = ((y - y_min) / RESOLUTION).astype(np.int32)

    # Here we will check for the valid points make sure the points are positive and not passing the boundry
    valid = (
        (ix >= 0) & (ix < width) & (iy >= 0) & (iy < height)
    )

    # Store all the valid point into the ix & iy
    ix = ix[valid]
    iy = iy[valid]

    # Here we will check all the grid locations and count it in the count_grid
    for grid_x, grid_y in zip(ix, iy):
        count_grid[grid_y, grid_x] += 1
    # The more points means we have more reflections there thus maybe a wall or an object there

    return count_grid, x_min, y_min

# Here we will change the grid points count to the risk level
def create_risk_grid(count_grid: np.ndarray) -> np.ndarray:
    """
    Convert point-density grid into a simple risk map.

    Risk labels:
        0 = unknown / empty
        1 = low density / likely free
        2 = caution
        3 = danger / high density obstacle
    """

    # Here we will build a 2D matrix where each grid of risk level are 0
    risk_grid = np.zeros_like(count_grid, dtype=np.uint8)

    # If there are some risk we set it to 1
    risk_grid[count_grid > 0] = 1

    # If there are more points than caution threshold but less than danger threshold we set it to 2
    risk_grid[count_grid >= CAUTION_COUNT] = 2

    # If there are more points than danger threshold we set it to 3
    risk_grid[count_grid >= DANGER_COUNT] = 3

    return risk_grid

def save_risk_map(risk_grid: np.ndarray, output_path: str):
    """
    Save risk grid as a colored PNG image.
    """

    # If the outputs/ folder didn't exist then we will create a new folder
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Here we defend the color of each level
    cmap = ListedColormap([
        "black", # unknown
        "green", # low risk
        "yellow", # caution
        "red" # danger
    ])

    plt.figure(figsize=(10, 10))

    # Change the 2D matrix into image
    # origin is very important it let the origin be at the bottom left
    plt.imshow(risk_grid, origin="lower", cmap=cmap, vmin=0, vmax=3)

    # Here we will add title of the image and labels
    plt.title("Mid-360S First Risk Map")
    plt.xlabel("X grid")
    plt.ylabel("Y grid")

    # This will show up on the top right tells the labels
    legend_items = [
        mpatches.Patch(color="black", label="Unknown / Empty"),
        mpatches.Patch(color="green", label="Low Risk"),
        mpatches.Patch(color="yellow", label="Caution"),
        mpatches.Patch(color="red", label="Danger / Obstacle"),
    ]

    plt.legend(handles=legend_items, loc="upper right")
    plt.tight_layout()

    # Save the image
    plt.savefig(output_path, dpi=200)
    plt.close()

def main():
    print(f"Loading point cloud: {PLY_PATH}")

    points = load_ascii_ply(PLY_PATH)
    print(f"Raw points: {len(points)}")

    # After reduce the noise and the height
    points = filter_points(points)
    print(f"Filtered points: {len(points)}")

    # Change the point cloud to 2D Map
    count_grid, x_min, y_min = create_density_grid(points)
    print(f"Grid shape: {count_grid.shape}")

    # Build the risk grid
    risk_grid = create_risk_grid(count_grid)

    # These will tell us how many region are Unknown, Low-risk, Caution, OR Danger
    print(f"Unknown cells: {np.sum(risk_grid == 0)}")
    print(f"Low-risk cells: {np.sum(risk_grid == 1)}")
    print(f"Caution cells: {np.sum(risk_grid == 2)}")
    print(f"Danger cells: {np.sum(risk_grid == 3)}")

    # Finally we will save the PNG
    save_risk_map(risk_grid, OUT_PATH)
    print(f"Risk map saved to: {OUT_PATH}")


if __name__ == "__main__":
    main()