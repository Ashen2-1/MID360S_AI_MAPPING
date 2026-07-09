import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


IMU_STATUS_CSV = "outputs/imu_status.csv"
LIDAR_FRAMES_CSV = "G:\MID360S_AI_MAPPING\data/test01_lidar_frames.csv"

OUT_CSV = "outputs/lidar_frame_confidence.csv"
OUT_PNG = "outputs/lidar_frame_confidence.png"


def nearest_status_for_frames(lidar_times, imu_times, imu_status):
    """
    For each LiDAR frame, find the nearest IMU status by timestamp.
    """

    matched_status = []

    imu_index = 0
    imu_count = len(imu_times)

    for t in lidar_times:
        while imu_index + 1 < imu_count and abs(imu_times[imu_index + 1] - t) < abs(imu_times[imu_index] - t):
            imu_index += 1

        matched_status.append(imu_status[imu_index])

    return np.array(matched_status)


def status_to_confidence(status):
    if status == 0:
        return "high"
    if status == 1:
        return "medium"
    return "low"


def main():
    os.makedirs("outputs", exist_ok=True)

    imu_df = pd.read_csv(IMU_STATUS_CSV)
    lidar_df = pd.read_csv(LIDAR_FRAMES_CSV)

    imu_times = imu_df["time_sec"].to_numpy()
    imu_status = imu_df["status"].to_numpy()

    lidar_times = lidar_df["time_sec"].to_numpy()

    matched_status = nearest_status_for_frames(lidar_times, imu_times, imu_status)

    lidar_df["imu_status"] = matched_status
    lidar_df["imu_status_label"] = lidar_df["imu_status"].map({
        0: "stable",
        1: "moving",
        2: "unstable"
    })

    lidar_df["mapping_confidence"] = lidar_df["imu_status"].apply(status_to_confidence)

    lidar_df.to_csv(OUT_CSV, index=False)

    high = (lidar_df["mapping_confidence"] == "high").sum()
    medium = (lidar_df["mapping_confidence"] == "medium").sum()
    low = (lidar_df["mapping_confidence"] == "low").sum()
    total = len(lidar_df)

    print(f"LiDAR frames: {total}")
    print(f"High confidence: {high} ({high / total * 100:.1f}%)")
    print(f"Medium confidence: {medium} ({medium / total * 100:.1f}%)")
    print(f"Low confidence: {low} ({low / total * 100:.1f}%)")
    print(f"Saved frame confidence CSV to: {OUT_CSV}")

    plt.figure(figsize=(14, 5))
    plt.plot(lidar_df["time_sec"], lidar_df["imu_status"])
    plt.yticks([0, 1, 2], ["high/stable", "medium/moving", "low/unstable"])
    plt.xlabel("time (s)")
    plt.ylabel("LiDAR frame confidence")
    plt.title("LiDAR Frame Confidence Based on IMU Motion")
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=200)
    plt.show()

    print(f"Saved plot to: {OUT_PNG}")


if __name__ == "__main__":
    main()