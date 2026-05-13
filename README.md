# MID360S AI Mapping

This project is an early-stage MVP for AI-assisted 3D terrain and hazard mapping using a Livox Mid-360S LiDAR sensor.

The goal is to turn raw LiDAR point cloud data into useful safety information, including top-down maps, risk maps, obstacle regions, and eventually safe-route recommendations for small robots operating in indoor, underground, or GPS-denied environments.

## Project Vision

Many dangerous environments, such as caves, tunnels, mines, collapsed buildings, and disaster-response areas, are unsafe for humans to enter directly. This project explores how LiDAR and AI can help a small robot scan these environments, understand the 3D structure, detect potential hazards, and recommend safer paths.

The long-term goal is to build a system that can support:

- 3D terrain scanning
- Indoor and underground mapping
- Traversability analysis
- Hazard and obstacle detection
- Collapse-risk indicators
- Safe-route planning
- VR or AR-based scene replay

## Current MVP Scope

The first MVP focuses on a small ground-based platform instead of a drone. The current system pipeline is:

```text
Mid-360S LiDAR
→ Livox SDK2
→ Custom ROS2 bridge
→ /livox/lidar PointCloud2 topic
→ rosbag recording
→ PLY point cloud export
→ Python mapping scripts
→ Top-down occupancy map
→ Risk map