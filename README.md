Hardware
Livox Mid-360S LiDAR
Raspberry Pi
Integrated IMU
SSD storage
Portable battery and power-conversion system
Ethernet communication
Custom 3D-printed mechanical enclosure / mounts

The portable hardware stack was designed to support headless field data collection without requiring a laptop during operation.

Software Stack
Robotics / Embedded
ROS 2
Livox SDK2
C++
Python
Linux
Point-Cloud Processing
PLY point-cloud export
confidence filtering
voxel downsampling
occupancy mapping
density-based analysis
height-aware terrain / risk analysis
Development
Git / GitHub
GCC / Makefile
Raspberry Pi Linux environment
Current Capabilities
Real-Time Sensor Acquisition

The custom ROS 2 interface publishes:

real-time Livox Mid-360S point clouds using sensor_msgs/PointCloud2
approximately 200 Hz IMU measurements

The data can be recorded for later playback, visualization, and processing.

Portable Data Logging

The sensing stack supports:

headless startup
LiDAR and IMU recording
SSD-based data storage
PLY export for offline analysis
portable power operation
3D Point-Cloud Processing

Current processing includes:

confidence-based filtering
voxel downsampling for point-cloud compression
top-down occupancy representations
density-based environment analysis
height-aware terrain and obstacle-risk mapping

These processing stages convert raw LiDAR measurements into representations that are more useful for robotic perception and navigation.

Example Data Flow
Raw LiDAR Scan
      ↓
Confidence Filtering
      ↓
Voxel Downsampling
      ↓
3D Point Cloud
      ↓
Occupancy / Density / Height Analysis
      ↓
Environment Risk Map
LiDAR–IMU SLAM

The next stage of the project focuses on combining LiDAR geometry with IMU motion information for localization and mapping.

The intended pipeline is:

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
coordinate-frame transformations
sensor calibration
drift reduction
pose estimation
loop closure
ROS 2 TF integration
UAV Integration

A parallel 5-inch FPV UAV platform has been assembled to build experience with real flight hardware, including:

F4 flight controller
45A ESC
brushless motors
FPV camera and video transmitter
radio hardware
power wiring and soldering

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

real-time LiDAR point-cloud acquisition
approximately 200 Hz IMU streaming
ROS 2 sensor publishing
point-cloud recording and playback
PLY export
confidence filtering
voxel-based point-cloud compression
occupancy mapping
density-based analysis
height-aware risk-map generation
Project Status

Active development — 2026

Current focus:

portable field-data acquisition
LiDAR–IMU motion compensation
SLAM and localization
improved 3D reconstruction
UAV perception integration
autonomous obstacle-aware navigation
Repository Structure
MID360S_AI_MAPPING/
├── data/
│   └── recorded and processed point-cloud data
├── scripts/
│   └── Python processing and mapping scripts
├── README.md
└── requirements.txt
Future Development

Planned work includes:

LiDAR–IMU SLAM
improved sensor synchronization
camera–LiDAR calibration
colorized 3D reconstruction
obstacle detection
safe-route planning
PX4 / UAV integration
real-time visualization
field deployment in GPS-denied environments
Author

Tom Li
Computer Engineering — University of Waterloo

Interests: Robotics · Autonomous Systems · LiDAR · SLAM · Embedded Systems · AI

GitHub: Ashen2-1
