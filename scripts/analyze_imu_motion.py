import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# This program is for analysis the imu motion to see and check if the motion has being detacted.
CSV_PATH = "G:\MID360S_AI_MAPPING\data/test01_imu.csv"
OUT_PATH = "outputs/imu_motion_summary.png"


def classify_motion(gyro_mag, acc_delta):

    """
    Simple rule-based IMU motion feedback.

    0 = stable
    1 = moving
    2 = unstable / high vibration
    """
    ############################################################################
    # Here we set up the threshold for each stable gyro,acc and moving gyro,acc
    # Values below the stable thresholds mean the IMU is static.
    # Values above the stable thresholds but below moving mean it is mid-range movement.
    # Values above the moving thresholds mean aggressive movement or heavy vibration.
    stable_gyro_th = 0.08
    moving_gyro_th = 0.35

    stable_acc_th = 0.60
    moving_acc_th = 1.20
    ############################################################################

    # Create an output array called "status" filled entirely with 0 (stable).
    # np.zeros_like(gyro_mag) ensures that if you pass in 1,000 rows of sensor data, it creates an output list of exactly 1,000 zeros.
    status = np.zeros_like(gyro_mag, dtype=np.int32)

    # Create a list of True and False and call it "moving"
    # If either the gyroscope magnitude is past 0.08 OR the accelerometer change is past 0.60, that time step is marked True
    moving = (gyro_mag > stable_gyro_th) | (acc_delta > stable_acc_th)
    # Create a list of True and False and call it "unstable"
    unstable = (gyro_mag > moving_gyro_th) | (acc_delta > moving_acc_th)

    # Everywhere moving was True, the 0 changes to 1. Right after, everywhere unstable was True, the value gets overwritten to 2.
    status[moving] = 1
    status[unstable] = 2



    # Return the list "status"
    return status


def main():
    # Check if the file exist on this path
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Cannot find CSV file: {CSV_PATH}")

    # Creates a folder named outputs in your directory to store your final plot. exist_ok=True prevents errors if the folder already exists.
    os.makedirs("outputs", exist_ok=True)

    print(f"Loading IMU CSV: {CSV_PATH}")

    # Reads your entire CSV file into memory as a Pandas DataFrame.
    df = pd.read_csv(CSV_PATH)

    #############################################################################
    # Extracts the specific column data and converts it into a raw NumPy array.
    # This strips away Pandas overhead and lets you do fast mathematical operations on thousands of data points at once.
    t = df["time_sec"].to_numpy()

    gx = df["gyro_x"].to_numpy()
    gy = df["gyro_y"].to_numpy()
    gz = df["gyro_z"].to_numpy()

    ax = df["acc_x"].to_numpy()
    ay = df["acc_y"].to_numpy()
    az = df["acc_z"].to_numpy()
    #############################################################################

    # Calculates the Euclidean magnitude (3D length vector) of the rotational speed using the Pythagorean theorem
    # Ignoring which direction it is spinning.
    gyro_mag = np.sqrt(gx ** 2 + gy ** 2 + gz ** 2)
    acc_mag = np.sqrt(ax ** 2 + ay ** 2 + az ** 2)

    # Gravity is included in IMU acceleration.
    # Subtracts standard Earth gravity (9.80665 m/s^2\) from your total acceleration, and takes the absolute (np.abs) value so it is always positive.
    # When an IMU sits perfectly flat and still on a table, its accelerometer reads (9.81 m/s^2) pointing straight up.
    # By subtracting gravity, acc_delta becomes 0 when perfectly stationary, and only rises if the device experiences actual, physical human movement or shaking.
    acc_delta = np.abs(acc_mag - 9.80665)

    # Get the "status" list from the function "classify_motion"
    status = classify_motion(gyro_mag, acc_delta)

    # Combines processed NumPy arrays back into a structured table (Pandas DataFrame).
    # Each array becomes a column, aligned perfectly row-by-row by timestamp.
    status_df = pd.DataFrame({
        "time_sec": t,
        "gyro_mag": gyro_mag,
        "acc_mag": acc_mag,
        "acc_delta": acc_delta,
        "status": status
    })

    # Uses .map() to look at the numerical status column (0, 1, 2) and generate a new column with human-readable text labels ("stable", "moving", "unstable").
    # This makes the output much easier for someone else to read.
    status_df["status_label"] = status_df["status"].map({
        0: "stable",
        1: "moving",
        2: "unstable"
    })

    # Saves your newly labeled table into a physical file inside your outputs/ folder.
    # index=False prevents Pandas from adding an extra, unneeded row-number column to your CSV file.
    status_csv_path = "outputs/imu_status.csv"
    status_df.to_csv(status_csv_path, index=False)

    print(f"Saved IMU status CSV to: {status_csv_path}")


    # Counts how many total timestamps fell into each motion state.
    # e.g: status == 0 generates an array of True/False states, and np.sum() treats True as 1 and False as 0 to count them up.
    stable_count = np.sum(status == 0)
    moving_count = np.sum(status == 1)
    unstable_count = np.sum(status == 2)

    total = len(status)

    # Calculates what percentage of the total recording time was spent in each motion state.
    stable_pct = stable_count / total * 100
    moving_pct = moving_count / total * 100
    unstable_pct = unstable_count / total * 100

    summary_path = "outputs/mapping_confidence_summary.txt"

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("IMU-Based Mapping Confidence Summary\n")
        f.write("====================================\n\n")
        f.write(f"Dataset: {CSV_PATH}\n")
        f.write(f"Duration: {t[-1]:.2f} seconds\n")
        f.write(f"Total IMU samples: {total}\n\n")

        f.write("Motion Classification:\n")
        f.write(f"- Stable: {stable_count} samples ({stable_pct:.1f}%)\n")
        f.write(f"- Moving: {moving_count} samples ({moving_pct:.1f}%)\n")
        f.write(f"- Unstable: {unstable_count} samples ({unstable_pct:.1f}%)\n\n")

        f.write("Mapping Interpretation:\n")
        f.write("- Stable segments are high-confidence for mapping.\n")
        f.write("- Moving segments may cause point-cloud distortion.\n")
        f.write("- Unstable segments should be treated as low-confidence or excluded from static mapping.\n")

    print(f"Saved mapping confidence summary to: {summary_path}")


    print(f"IMU samples: {total}")
    # t[-1] looks at the very last element of your timestamp array to instantly print the total runtime duration of your data file.
    print(f"Duration: {t[-1]:.2f} seconds")
    print(f"Gyro magnitude min/max: {gyro_mag.min():.4f} / {gyro_mag.max():.4f}")
    print(f"Acceleration magnitude min/max: {acc_mag.min():.4f} / {acc_mag.max():.4f}")
    print(f"Acceleration delta min/max: {acc_delta.min():.4f} / {acc_delta.max():.4f}")
    # The :.1f}% syntax formats the mathematical percentages cleanly to exactly one decimal place.
    print(f"Stable samples: {stable_count} ({stable_count / total * 100:.1f}%)")
    print(f"Moving samples: {moving_count} ({moving_count / total * 100:.1f}%)")
    print(f"Unstable samples: {unstable_count} ({unstable_count / total * 100:.1f}%)")

    plt.figure(figsize=(14, 9))

    # Divides canvas window into a grid of 4 rows and 1 column. The final number (1) activates the first (top) panel.
    # It plots time on the X-axis and total gyroscope rotation speed on the Y-axis.
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