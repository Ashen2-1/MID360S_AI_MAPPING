## LiDAR–IMU SLAM

The next stage of the project focuses on combining LiDAR geometry with IMU motion information for localization and mapping.

The intended pipeline is:

```text
IMU Motion Estimate
        +
LiDAR Scan Matching
        ↓
Pose Estimation
        ↓
Local Mapping
        ↓
Global 3D Map

Key topics being developed include:

LiDAR scan matching
IMU motion compensation
Coordinate-frame transformations
Sensor calibration
Drift reduction
Pose estimation
Loop closure
ROS 2 TF integration
UAV Integration

A parallel 5-inch FPV UAV platform has been assembled to build practical experience with real flight hardware, including:

F4 flight controller
45A ESC
Brushless motors
FPV camera and video transmitter
Radio hardware
Power wiring and soldering
Mechanical assembly and component integration

The long-term goal is to integrate a lightweight version of the LiDAR–IMU perception stack with an aerial platform.

Target architecture:

LiDAR / IMU / Camera
        ↓
Companion Computer
        ↓
ROS 2 Perception
        ↓
SLAM / Localization
        ↓
Obstacle Map
        ↓
Flight Controller
        ↓
Autonomous Navigation
Results So Far

Current validated outputs include:

Real-time LiDAR point-cloud acquisition
Approximately 200 Hz IMU streaming
ROS 2 sensor publishing
Point-cloud recording and playback
PLY export
Confidence filtering
Voxel-based point-cloud compression
Occupancy mapping
Density-based analysis
Height-aware risk-map generation
Testing and Validation

Testing currently focuses on validating the full sensing pipeline from hardware acquisition to offline 3D processing.

Indoor / Bench Testing

Validated components include:

LiDAR communication over Ethernet
ROS 2 point-cloud publishing
IMU data acquisition
Headless recording
SSD-based data storage
PLY export
Point-cloud filtering and compression
Occupancy and risk-map generation
Portable System Testing

The handheld system is designed to validate:

Portable power operation
Reliable headless startup
Continuous LiDAR / IMU recording
Data storage without a connected laptop
Mechanical stability of the sensing stack
Field-ready cable and power management
Field Testing

Field testing will evaluate:

Sensor reliability during continuous movement
Point-cloud quality in larger environments
IMU behavior during motion
Mapping consistency
Portable power endurance
Data integrity during extended recordings
Performance in GPS-limited and low-visibility environments
Demo and Visual Results
Hardware

Add a photo of the completed handheld LiDAR–IMU system here.

![Portable LiDAR–IMU System](docs/images/lidar_handheld.jpg)
Real-Time LiDAR Visualization

Add a screenshot from RViz or another point-cloud visualization tool.

![Real-Time LiDAR Point Cloud](docs/images/rviz_pointcloud.png)
Processed Point Cloud

Add an example showing the filtered / voxel-downsampled output.

![Processed Point Cloud](docs/images/processed_pointcloud.png)
Environment / Risk Map

Add an occupancy, density, or height-aware map.

![Environment Risk Map](docs/images/risk_map.png)
Field-Test Demo

For a short demo video, use either:

a GitHub-hosted short video / GIF
a YouTube link
a portfolio website link

Example:

[Watch the field-test demo](https://your-demo-link-here.com)
Project Status

Active development — 2026

Current focus:

Portable field-data acquisition
LiDAR–IMU motion compensation
SLAM and localization
Improved 3D reconstruction
Camera–LiDAR integration
UAV perception integration
Autonomous obstacle-aware navigation
Repository Structure
MID360S_AI_MAPPING/
├── data/
│   ├── raw/
│   ├── segments/
│   └── processed/
├── scripts/
│   ├── batch/
│   ├── mapping/
│   └── visualization/
├── ros2/
│   └── sensor interface / bridge code
├── docs/
│   └── images/
├── README.md
└── requirements.txt

Repository structure may evolve as the SLAM and UAV integration components are added.

Future Development

Planned development includes:

LiDAR–IMU SLAM
Improved LiDAR / IMU synchronization
IMU-based motion compensation
Scan matching and pose estimation
Camera–LiDAR calibration
Colorized 3D reconstruction
Obstacle detection
Safe-route planning
Real-time local mapping
ROS 2 TF integration
PX4 / flight-controller integration
UAV simulation and testing
Real-time visualization
Field deployment in GPS-denied environments
Engineering Goals

The project is intended to evolve from a portable sensing and mapping platform into a more complete autonomous perception stack.

The long-term system goal is:

Sensors
   ↓
Perception
   ↓
Localization
   ↓
Mapping
   ↓
Obstacle Understanding
   ↓
Path Planning
   ↓
Autonomous Navigation

The focus is not only on individual algorithms, but also on the integration required to make the complete system work reliably on real hardware.

Author

Tom Li
Computer Engineering — University of Waterloo

Areas of interest:

Robotics
Autonomous Systems
LiDAR
SLAM
Sensor Fusion
Embedded Systems
UAVs
AI / Computer Vision
