import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


CSV_PATH = "G:\MID360S_AI_MAPPING\data/test01_imu.csv"
OUT_PATH = "outputs/imu_motion_summary.png"


def classify_motion(gyro_mag, acc_delta):
    """
    Simple rule-based IMU motion feedback.

    0 = stable
    1 = moving
    2 = unstable / high vibration
    """

    stable_gyro_th = 0.08
    moving_gyro_th = 0.35

    stable_acc_th = 0.60
    moving_acc_th = 1.20

    status = np.zeros_like(gyro_mag, dtype=np.int32)

    moving = (gyro_mag > stable_gyro_th) | (acc_delta > stable_acc_th)
    unstable = (gyro_mag > moving_gyro_th) | (acc_delta > moving_acc_th)

    status[moving] = 1
    status[unstable] = 2

    return status


def main():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Cannot find CSV file: {CSV_PATH}")

    os.makedirs("outputs", exist_ok=True)

    print(f"Loading IMU CSV: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    t = df["time_sec"].to_numpy()

    gx = df["gyro_x"].to_numpy()
    gy = df["gyro_y"].to_numpy()
    gz = df["gyro_z"].to_numpy()

    ax = df["acc_x"].to_numpy()
    ay = df["acc_y"].to_numpy()
    az = df["acc_z"].to_numpy()

    gyro_mag = np.sqrt(gx ** 2 + gy ** 2 + gz ** 2)
    acc_mag = np.sqrt(ax ** 2 + ay ** 2 + az ** 2)

    # Gravity is included in IMU acceleration.
    acc_delta = np.abs(acc_mag - 9.80665)

    status = classify_motion(gyro_mag, acc_delta)

    stable_count = np.sum(status == 0)
    moving_count = np.sum(status == 1)
    unstable_count = np.sum(status == 2)
    total = len(status)

    print(f"IMU samples: {total}")
    print(f"Duration: {t[-1]:.2f} seconds")
    print(f"Gyro magnitude min/max: {gyro_mag.min():.4f} / {gyro_mag.max():.4f}")
    print(f"Acceleration magnitude min/max: {acc_mag.min():.4f} / {acc_mag.max():.4f}")
    print(f"Acceleration delta min/max: {acc_delta.min():.4f} / {acc_delta.max():.4f}")
    print(f"Stable samples: {stable_count} ({stable_count / total * 100:.1f}%)")
    print(f"Moving samples: {moving_count} ({moving_count / total * 100:.1f}%)")
    print(f"Unstable samples: {unstable_count} ({unstable_count / total * 100:.1f}%)")

    plt.figure(figsize=(14, 9))

    plt.subplot(4, 1, 1)
    plt.plot(t, gyro_mag)
    plt.ylabel("gyro |w|")
    plt.title("IMU Motion Feedback")

    plt.subplot(4, 1, 2)
    plt.plot(t, acc_mag)
    plt.axhline(9.80665, linestyle="--")
    plt.ylabel("acc |a| m/s²")

    plt.subplot(4, 1, 3)
    plt.plot(t, acc_delta)
    plt.ylabel("|acc - g|")

    plt.subplot(4, 1, 4)
    plt.plot(t, status)
    plt.yticks([0, 1, 2], ["stable", "moving", "unstable"])
    plt.xlabel("time (s)")
    plt.ylabel("status")

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=200)
    plt.show()

    print(f"Saved plot to: {OUT_PATH}")


if __name__ == "__main__":
    main()