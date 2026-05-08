# OpenVINS Configuration Files

This folder contains the configuration files used for the **OpenVINS stereo Visual-Inertial Odometry (VIO)** pipeline with a **ZED stereo camera** and IMU setup.

## Folder Structure

```bash
config/
├── openvins/
│   ├── estimator_config.yaml
│   ├── kalibr_imucam_chain.yaml
│   └── kalibr_imu_chain.yaml
│
└── zed_config/
    ├── common_stereo.yaml
    └── zed2i.yaml
```

---

## OpenVINS Configuration Files

Located inside:

```bash
config/openvins/
```

### `estimator_config.yaml`

Main OpenVINS estimator configuration file.

Contains:
- MSCKF and SLAM parameters
- Feature tracking settings
- Initialization settings
- ZUPT parameters
- Camera and IMU configuration references

The parameters are tuned for:
- ZED stereo cameras
- 640×360 resolution
- Wide FOV operation
- Reduced drift during VIO

---

### `kalibr_imucam_chain.yaml`

Stereo camera and IMU calibration file generated using Kalibr.

Contains:
- Camera intrinsics
- Camera extrinsics
- Stereo baseline transform
- Camera distortion parameters
- Camera–IMU transforms
- Time synchronization offsets

> Note:  
> The right camera calibration was manually adjusted by approximately **1.5° outward tilt** to improve stereo alignment and reduce trajectory drift.

---

### `kalibr_imu_chain.yaml`

IMU intrinsic calibration file.

Contains:
- Accelerometer noise parameters
- Gyroscope noise parameters
- Random walk values
- IMU update rate
- IMU frame transforms

---

## ZED Configuration Files

Located inside:

```bash
config/zed_config/
```

### `zed2i.yaml`

ZED 2i camera configuration file used by the ZED ROS 2 wrapper.

Contains:
- Camera resolution and FPS settings
- Depth configuration
- IMU and sensor settings
- Video parameters

---

### `common_stereo.yaml`

Shared stereo camera configuration parameters for the ZED setup.

Contains:
- Stereo processing parameters
- Common camera settings
- ROS-related configuration values

---

## Notes

- The `openvins/` folder contains configurations specifically for **OpenVINS**.
- The `zed_config/` folder contains configurations for the **ZED ROS 2 wrapper**.
- Calibration values depend on the current hardware mounting setup and may require recalibration if the sensor setup changes.

---


