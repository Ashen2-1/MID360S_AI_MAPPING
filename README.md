# LiDAR–IMU Autonomous Mapping & UAV Perception Platform

A portable 3D sensing and mapping platform built around the **Livox Mid-360S LiDAR**, IMU, Raspberry Pi/Linux compute, ROS 2, C++, and Python.

The system captures real-time LiDAR and inertial data, records synchronized sensor streams, exports 3D point clouds, and processes them into environment maps for localization, terrain analysis, obstacle perception, and future autonomous navigation.

The project is being developed from a handheld / ground sensing platform toward **LiDAR–IMU SLAM and UAV perception in GPS-limited environments**.

---

## Overview

Autonomous robots and UAVs operating indoors, underground, or in degraded-visibility environments cannot always rely on GPS or conventional cameras.

This project explores a perception pipeline that allows a mobile platform to:

- capture 3D LiDAR data in real time
- acquire high-rate IMU measurements
- record sensor data headlessly on an embedded computer
- reconstruct and analyze 3D environments
- generate occupancy and terrain-risk representations
- develop LiDAR–IMU localization and SLAM
- support future UAV perception and autonomous navigation

Potential applications include:

- underground and cave mapping
- search-and-rescue
- inspection of tunnels and confined spaces
- obstacle detection
- autonomous aerial sensing
- GPS-denied navigation

---

## System Architecture

```text
Livox Mid-360S
      │
      │ Ethernet
      ▼
Livox SDK2
      │
      ▼
Custom ROS 2 Interface
      │
      ├── PointCloud2 LiDAR stream
      │
      └── ~200 Hz IMU stream
      │
      ▼
Raspberry Pi / Linux
      │
      ├── Headless recording
      ├── Sensor logging
      ├── rosbag / data storage
      └── PLY export
      │
      ▼
Point-Cloud Processing
      │
      ├── Confidence filtering
      ├── Voxel downsampling
      ├── Occupancy mapping
      ├── Density analysis
      └── Height-aware risk mapping
      │
      ▼
LiDAR–IMU SLAM / Localization
      │
      ▼
Autonomous Navigation / UAV Perception
