# Visual-Inertial-Odometry

Stereo Visual-Inertial Odometry (VIO) pipeline using **ZED 2i**, **Kalibr**, **Allan Variance**, and **OpenVINS** for real-time pose estimation and trajectory tracking in both aerial and underwater environments.

This repository provides:

* ZED 2i ROS 2 integration
* Stereo + IMU synchronization
* Camera and IMU calibration workflow
* Allan variance-based IMU intrinsic estimation
* OpenVINS MSCKF-based VIO


---

# System Overview

The VIO framework fuses:

* Stereo grayscale images
* High-frequency IMU measurements

to estimate:

* Real-time pose
* Sensor trajectory
* Motion tracking

## Pipeline Workflow

```text
ZED 2i Camera + IMU
        │
        ▼
ROS2 ZED Wrapper
        │
        ▼
Stereo + IMU Synchronization
        │
        ▼
Calibration
(Camera Intrinsics + IMU Intrinsics + Camera-IMU Extrinsics)
        │
        ▼
OpenVINS (MSCKF)
        │
        ▼
Pose + Trajectory Estimation
```

---

# Features

* Stereo Visual-Inertial Odometry
* MSCKF-based state estimation
* Camera intrinsic calibration
* Camera–IMU extrinsic calibration
* Allan variance IMU analysis
* ROS 2 integration
* Dockerized deployment
* OpenVINS integration
* Underwater VIO evaluation
* Feature masking for drift reduction

---

# Requirements
* ZED 2i Stereo Camera
* Integrated IMU
* NVIDIA Jetson Xavier
* Docker

---

# Software Requirements

| Component      | Version                 |
| ---------------|-------------------------|
| Host system    | Ubuntu 20.04            |
| CUDA           | Compatible with ZED SDK |
| Docker         | Latest stable           |
| Python         | 3.8+                    |

---


# Install ZED SDK

Download the correct SDK version from Stereolabs based on your CUDA and Ubuntu version.

---

# Step 1 — ZED ROS2 Wrapper Setup

Create ROS 2 workspace:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
```

Clone wrapper:

```bash
git clone https://github.com/stereolabs/zed-ros2-wrapper.git
```

Build workspace:

```bash
cd ~/ros2_ws

colcon build

source install/setup.bash
```

Launch ZED node:

```bash
ros2 launch zed_wrapper zed_camera.launch.py \
camera_model:=zed2i \
sensors.publish_imu:=true \
sensors.sensors_image_sync:=true \
sensors.sensors_pub_rate:=200.0 \
publish_tf:=false \
publish_map_tf:=false \
pos_tracking.pos_tracking_enabled:=false
```

---

# Topics Used

| Topic                                         | Purpose     |
| --------------------------------------------- | ----------- |
| `/zed/zed_node/left_raw_gray/image_raw_gray`  | Left image  |
| `/zed/zed_node/right_raw_gray/image_raw_gray` | Right image |
| `/zed/zed_node/imu/data_raw`                  | IMU data    |

These synchronized topics are required for calibration and OpenVINS.

---

# Step 2 — Camera–IMU Calibration (Kalibr)

Kalibr is used for:

* Stereo camera intrinsics
* Stereo extrinsics
* Camera–IMU extrinsics

## Prerequisites

Required:

* AprilGrid target
* ROS bag with stereo + IMU data
* IMU intrinsic parameters
* ROS1 environment

---

## Prepare AprilGrid

Example configuration:

```yaml
target_type: 'aprilgrid'
tagCols: 6
tagRows: 6
tagSize: 0.095
tagSpacing: 0.3
```
These values can be adjusted based on the AprilGrid 
---

## Convert ROS2 Bag to ROS1 (If Needed)

```bash
pip install rosbags
```

Convert:

```bash
rosbags-convert \
--src <path_to_ros2_bag> \
--dst <output_ros1_bag>
```

---

## Run Kalibr Docker

```bash
xhost +local:root

docker run -it \
-e "DISPLAY" \
-e "QT_X11_NO_MITSHM=1" \
-v "/tmp/.X11-unix:/tmp/.X11-unix:rw" \
-v "$FOLDER:/data" \
kalibr
```

Inside container:

```bash
source devel/setup.bash
```

---

## Camera Calibration

```bash
rosrun kalibr kalibr_calibrate_cameras \
--bag /data/<bag_name> \
--target /data/april_6x6.yaml \
--models pinhole-radtan pinhole-radtan \
--topics <left_camera_topic> <right_camera_topic>
```

---

## Camera–IMU Calibration

```bash
rosrun kalibr kalibr_calibrate_imu_camera \
--bag /data/<bag_name> \
--cam /data/zed-camchain.yaml \
--imu /data/kalibr_imu_chain.yaml \
--target /data/april_6x6.yaml
```

The IMU intrinsic used for calibration of camera-imu is calculated using Allan variance which is described below:
---

# Calibration Outputs

Generated files:

| File                       | Purpose                  |
| -------------------------- | ------------------------ |
| `kalibr_imu_chain.yaml`    | IMU intrinsic parameters |
| `kalibr_imucam_chain.yaml` | Camera–IMU extrinsics    |

These files are required for OpenVINS integration.

---

# Step 3 — IMU Intrinsic Calibration (Allan Variance)

Used for estimating:

* Gyroscope noise density
* Accelerometer noise density
* Bias instability

## Clone and Build

```bash
cd ~/catkin_ws/src

git clone https://github.com/ori-drs/allan_variance_ros.git

cd ..

catkin_make

source devel/setup.bash
```

---

## Cook the ROS Bag

```bash
rosrun allan_variance_ros cookbag.py \
--input original_rosbag.bag \
--output cooked_rosbag.bag
```

---

## Generate Allan Variance Data

```bash
rosrun allan_variance_ros allan_variance \
/path/to/folder_containing_bag \
/path/to/config.yaml
```

---

## Analyze Results

```bash
rosrun allan_variance_ros analysis.py \
--data allan_variance.csv
```

---

# Important Note

The estimated IMU noise values are often optimistic.

It is recommended to inflate the estimated values by:

```text
10x – 20x
```

to account for unmodeled real-world sensor errors.

---

# Step 4 — OpenVINS Setup

## Clone OpenVINS

```bash
git clone https://github.com/rpng/open_vins.git
```

---

## Build Docker Image

```bash
cd open_vins

docker build \
-f Dockerfile_ros2_20_04 \
-t openvins_ros2 .
```

---

## Run Container

```bash
xhost +local:docker

docker run -it \
--net=host \
--privileged \
-e DISPLAY=$DISPLAY \
-v /tmp/.X11-unix:/tmp/.X11-unix \
-v ~/openvins:/root/openvins \
openvins_ros2 bash
```

---

## Setup Environment

Inside container:

```bash
cd ~/openvins/

source /opt/ros/<distro>/setup.bash

source install/setup.bash
```

---

# Step 5 — Run VIO

Launch OpenVINS:

```bash
ros2 launch ov_msckf subscribe.launch.py rviz_enable:=true
```

---

# Step 6 — Play Dataset

In a separate terminal:

```bash
source /opt/ros/<distro>/setup.bash

ros2 bag play <bag_file>
```

---

# Optional Preprocessing Utilities

Additional helper scripts are provided for preprocessing image topics before running OpenVINS.

```bash
camera_masking.py
```
Applies masks to camera images to remove unwanted regions and reduce feature tracking errors or drift in challenging environments (e.g., underwater scenes, reflections, frame boundaries).

Example use cases:

* Removing distorted image boundaries
* Ignoring vehicle structures or propellers
* Reducing dynamic noise regions

```bash
republish_compressed_images.py
```
Republishes compressed ZED image topics as standard ROS image topics for OpenVINS compatibility.

This is useful when the ZED wrapper publishes:

```bash
/compressed
```
image streams instead of raw image topics expected by OpenVINS.

These scripts are located in:

```bash
utils/
```

and can be modified based on the required topic names or masking regions.

# Outputs

| Topic               | Description          |
| ------------------- | -------------------- |
| `/ov_msckf/poseimu` | Estimated pose       |
| `/ov_msckf/pathimu` | Estimated trajectory |

RViz provides real-time trajectory visualization.

---

# References

* [OpenVINS](https://github.com/rpng/open_vins)
* [Kalibr](https://github.com/ethz-asl/kalibr)
* [Allan Variance ROS](https://github.com/ori-drs/allan_variance_ros)
* [Stereolabs ZED SDK](https://www.stereolabs.com/en-in/developers/release)


---

