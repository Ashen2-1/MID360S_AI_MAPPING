import os
import time
import numpy as np


PLY_PATH = r"G:\MID360S_AI_MAPPING\data\test01_high_confidence_only.ply"
OUT_DIR = r"G:\MID360S_AI_MAPPING\data\compressed" ### Output Directory

VOXEL_SIZES = [0.05, 0.10, 0.20] ### Size of the grid (5cm, 10cm, 20cm)


def load_ascii_ply(path):
    """
    Load ASCII PLY with x, y, z, intensity.
    Returns Nx4 numpy array.
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"PLY file not found: {path}")

    ### Read all the data from the .ply and save it to the "lines"
    with open(path, "r") as f:
        lines = f.readlines()

    ### The .ply data set have a line that says "end_header" so this is loop until find that line and save tha index
    end_header_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "end_header":
            end_header_idx = i
            break

    ### If the "end_header" is not found then will return invalid ply.
    if end_header_idx is None:
        raise ValueError("Invalid PLY: missing end_header")


    points = []
    for line in lines[end_header_idx + 1:]: ### Start from the end of the "end_header" line
        parts = line.strip().split() ### Split the data by the "space" and save it to the array "parts"
        if len(parts) < 4: ### If the current line of the data have less than 4 values means the format is not right skip.
            continue
        x, y, z, intensity = map(float, parts[:4]) ### change the values to the float
        points.append((x, y, z, intensity)) ### Save it into the array "points"

    return np.array(points, dtype=np.float32) ### Return the array "points"


def write_ascii_ply(points, path):
    """
    Write Nx4 point cloud to ASCII PLY.
    """

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {len(points)}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("property float intensity\n")
        f.write("end_header\n")

        for p in points:
            f.write(f"{p[0]} {p[1]} {p[2]} {p[3]}\n")


def voxel_downsample_average(points, voxel_size):
    """
    Voxel grid downsampling by averaging all points inside each voxel.

    Each voxel keeps one representative point:
    average x, y, z, intensity.
    """

    xyz = points[:, :3]

    xyz_min = np.min(xyz, axis=0)

    voxel_indices = np.floor((xyz - xyz_min) / voxel_size).astype(np.int32)

    # Convert 3D voxel indices to a structured array so numpy can group them.
    voxel_keys = (
        voxel_indices[:, 0].astype(np.int64) * 73856093 ^
        voxel_indices[:, 1].astype(np.int64) * 19349663 ^
        voxel_indices[:, 2].astype(np.int64) * 83492791
    )

    unique_keys, inverse_indices = np.unique(voxel_keys, return_inverse=True)

    compressed_points = np.zeros((len(unique_keys), 4), dtype=np.float32)
    counts = np.zeros(len(unique_keys), dtype=np.int32)

    np.add.at(compressed_points, inverse_indices, points)
    np.add.at(counts, inverse_indices, 1)

    compressed_points = compressed_points / counts[:, None]

    return compressed_points


def estimate_size_mb(point_count):
    """
    Estimate binary size if each point stores x,y,z,intensity as float32.
    4 values * 4 bytes = 16 bytes per point.
    """

    bytes_per_point = 16
    return point_count * bytes_per_point / (1024 * 1024)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print(f"Loading PLY: {PLY_PATH}")
    start = time.time()
    points = load_ascii_ply(PLY_PATH)
    load_time = time.time() - start

    original_count = len(points)
    original_est_size = estimate_size_mb(original_count)

    print(f"Original points: {original_count}")
    print(f"Estimated binary size: {original_est_size:.2f} MB")
    print(f"Load time: {load_time:.2f} sec")
    print("-" * 60)

    summary_rows = []

    for voxel_size in VOXEL_SIZES:
        print(f"Voxel downsampling: voxel_size = {voxel_size} m")

        start = time.time()
        compressed = voxel_downsample_average(points, voxel_size)
        elapsed = time.time() - start

        compressed_count = len(compressed)
        compression_ratio = original_count / compressed_count
        compressed_est_size = estimate_size_mb(compressed_count)

        out_name = f"test01_voxel_{int(voxel_size * 100)}cm.ply"
        out_path = os.path.join(OUT_DIR, out_name)

        write_ascii_ply(compressed, out_path)

        print(f"Compressed points: {compressed_count}")
        print(f"Compression ratio: {compression_ratio:.2f}x")
        print(f"Estimated binary size: {compressed_est_size:.2f} MB")
        print(f"Processing time: {elapsed:.2f} sec")
        print(f"Saved: {out_path}")
        print("-" * 60)

        summary_rows.append([
            voxel_size,
            original_count,
            compressed_count,
            compression_ratio,
            original_est_size,
            compressed_est_size,
            elapsed,
            out_path
        ])

    summary_path = os.path.join(OUT_DIR, "voxel_compression_summary.csv")

    with open(summary_path, "w") as f:
        f.write("voxel_size_m,original_points,compressed_points,compression_ratio,original_est_size_mb,compressed_est_size_mb,processing_time_sec,output_path\n")

        for row in summary_rows:
            f.write(",".join(map(str, row)) + "\n")

    print(f"Saved summary: {summary_path}")


if __name__ == "__main__":
    main()