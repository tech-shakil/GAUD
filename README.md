# 🚗 GAUD — AI-Powered Real-Time Road Safety & Collision Warning System

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Ultralytics YOLOv8](https://img.shields.io/badge/Model-YOLOv8-FF7F00?logo=ultralytics&logoColor=white)](https://github.com/ultralytics/ultralytics)
[![OpenCV](https://img.shields.io/badge/Vision-OpenCV-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Repository](https://img.shields.io/badge/GitHub-tech--shakil%2FGAUD-181717?logo=github&logoColor=white)](https://github.com/tech-shakil/GAUD)

**GAUD** is an intelligent, real-time Advanced Driver Assistance System (ADAS) collision warning application built using **YOLOv8** deep learning object detection and **OpenCV** computer vision. 

By analyzing live video streams from a vehicle dashcam, USB webcam, or front-facing camera, GAUD dynamically tracks pedestrians, vehicles, motorcyclists, and cyclists. It projects a forward-looking **Danger Zone (ROI)** corridor, computes instantaneous mathematical collision risk scores based on object scale and proximity, and renders an augmented reality Heads-Up Display (HUD) with acoustic buzzer alarms to prevent vehicular collisions.

---

## 📋 Table of Contents

- [🌟 Executive Summary & Key Highlights](#-executive-summary--key-highlights)
- [🧠 How It Works & Architecture](#-how-it-works--architecture)
- [📐 Mathematical Risk Scoring Model](#-mathematical-risk-scoring-model)
- [📁 Project Directory Structure](#-project-directory-structure)
- [⚙️ Prerequisites & System Requirements](#️-prerequisites--system-requirements)
- [🚀 Step-by-Step Installation Guide](#-step-by-step-installation-guide)
- [💻 Running the System](#-running-the-system)
- [🛠️ Configuration & Calibration](#️-configuration--calibration)
- [❓ Troubleshooting & FAQ](#-troubleshooting--faq)
- [👥 Authors & Acknowledgments](#-authors--acknowledgments)
- [📄 License](#-license)

---

## 🌟 Executive Summary & Key Highlights

- **Multi-Class Road Hazard Detection**: Detects and tracks 6 critical road object categories simultaneously:
  - 🚶 Pedestrians (`person`)
  - 🚗 Automobiles (`car`)
  - 🏍️ Motorcycles (`motorcycle`)
  - 🚌 Buses (`bus`)
  - 🚚 Commercial Trucks (`truck`)
  - 🚲 Bicycles (`bicycle`)
- **Forward Danger Zone Corridor (ROI)**: Isolates the vehicle's forward trajectory to eliminate false positives from off-road objects, roadside trees, or parked traffic.
- **Dynamic Dual-Factor Proximity Evaluation**: Combines bounding-box surface area expansion (object getting closer/larger) with vertical ground-plane proximity (object approaching bottom bumper line).
- **3-Tier Visual Threat State Machine**:
  - 🟢 **SAFE (`< 30%` Risk)**: Far proximity, green indicators, normal operation.
  - 🟡 **WARNING (`30% - 69%` Risk)**: Approaching obstacle, amber warning indicator.
  - 🔴 **DANGER (`≥ 70%` Risk)**: Critical collision hazard, bright red HUD banner with acoustic buzzer warning.
- **Acoustic Emergency Alarm**: Real-time acoustic buzzer warning (`winsound` on Windows with cross-platform fallback) triggered at low latency during critical threat moments.
- **Built-in Diagnostic Suite**: Includes camera discovery, stream verification, and model readiness test utilities.

---

## 🧠 How It Works & Architecture

```text
┌───────────────────────┐
│ Live Camera / Dashcam │ (cv2.VideoCapture)
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│   YOLOv8 Nano Model   │ (yolov8n.pt - Ultra-fast real-time inference)
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│  Road Class Filtering │ (Filters: person, car, motorcycle, bus, truck, bicycle)
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│   Danger Zone (ROI)   │ Centroid check: zone_x1 < cx < zone_x2
│     Corridor Filter   │                 zone_y1 < cy < zone_y2
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ Mathematical Scoring  │ Size Risk = (Box Area / Frame Area) * 200
│   Proximity & Scale   │ Position Risk = (Centroid Y / Frame Height) * 100
└──────────┬────────────┘
           │
           ├─ Risk < 30%  ─────────▶ Status: SAFE (Green HUD)
           ├─ Risk 30% - 69% ──────▶ Status: WARNING (Yellow HUD)
           └─ Risk ≥ 70%  ─────────▶ Status: DANGER (Red Banner + Audio Alarm)
           │
           ▼
┌───────────────────────┐
│ Fullscreen HUD Engine │ Semi-transparent dashboard overlay + Bounding Boxes
└───────────────────────┘
```

---

## 📐 Mathematical Risk Scoring Model

The risk calculation algorithm inside [`detect_live.py`](detect_live.py) determines how imminent a collision is when an obstacle enters the forward collision corridor:

1. **Centroid Localization**:
   $$\text{cx} = \frac{x_1 + x_2}{2}, \quad \text{cy} = \frac{y_1 + y_2}{2}$$

2. **Corridor Verification**:
   $$\text{In Zone} = (0.30 \cdot W < \text{cx} < 0.70 \cdot W) \land (0.60 \cdot H < \text{cy} < H)$$

3. **Size Expansion Risk ($R_{\text{size}}$)**:
   Estimates relative vehicle proximity based on visual perspective projection:
   $$R_{\text{size}} = \min\left(100, \, \frac{\text{Width}_{\text{box}} \cdot \text{Height}_{\text{box}}}{W \cdot H} \times 200\right)$$

4. **Vertical Proximity Risk ($R_{\text{position}}$)**:
   Objects lower in the camera field of view are closer to the front bumper:
   $$R_{\text{position}} = \frac{\text{cy}}{H} \times 100$$

5. **Composite Threat Index**:
   $$R_{\text{total}} = \min\left(100, \, \left\lfloor \frac{R_{\text{size}} + R_{\text{position}}}{2} \right\rfloor\right)$$

---

## 📁 Project Directory Structure

```text
GAUD/
├── detect_live.py        # Main application: Real-time inference, risk engine & HUD
├── find_camera.py        # Diagnostic: Scans and prints all connected camera hardware indices
├── camera_check.py       # Diagnostic: Tests and displays preview window for each detected device
├── camera_test.py        # Diagnostic: Direct single-index camera feed tester
├── test_yolo.py          # Sanity check: Verifies YOLOv8 model loading and PyTorch initialization
├── yolov8n.pt            # YOLOv8 nano pre-trained weights file (fast lightweight inference)
├── requirements.txt      # Project Python dependencies specification
├── .gitignore            # Git exclusion rules for virtualenvs, caches & IDE files
├── LICENSE               # Official MIT Open Source License
└── README.md             # Comprehensive project documentation & usage guide
```

---

## ⚙️ Prerequisites & System Requirements

- **Operating System**: Windows 10/11, macOS (11+), or Linux (Ubuntu 20.04+).
- **Python**: Version **3.8** through **3.12** (Python 3.10 / 3.11 recommended).
- **Hardware**:
  - Built-in webcam, external USB camera, or dashcam feed.
  - CPU: Any modern multi-core processor (Intel Core i3/i5/i7/i9 or AMD Ryzen).
  - Optional GPU: NVIDIA GPU with CUDA for ultra-high FPS (>60 FPS).

---

## 🚀 Step-by-Step Installation Guide

### Step 1: Clone the Repository

```bash
git clone https://github.com/tech-shakil/GAUD.git
cd GAUD
```

### Step 2: Create a Virtual Environment

#### On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell shows an execution policy error, enable local script execution with: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

#### On Windows (Command Prompt):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- `ultralytics` (YOLOv8 framework)
- `opencv-python` (Computer Vision & GUI Rendering)
- `torch` & `torchvision` (PyTorch inference engine)

---

## 💻 Running the System

### 1. Model Verification Sanity Check
Confirm that PyTorch and YOLOv8 load properly:
```powershell
.\venv\Scripts\python.exe test_yolo.py
```
*Expected output: `GAUD AI Ready`*

### 2. Identify Connected Cameras
If you have multiple video devices (integrated camera, USB webcam, OBS virtual cam):
```powershell
.\venv\Scripts\python.exe find_camera.py
```
This tests indices `0` through `9` and displays which ports successfully return a camera stream.

### 3. Launch the Main Live Safety System
Run the real-time collision detection system:
```powershell
.\venv\Scripts\python.exe detect_live.py
```

### Keyboard Controls:
- Press <kbd>q</kbd> with the camera window focused to safely close the application and release the camera hardware.

---

## 🛠️ Configuration & Calibration

You can customize runtime parameters directly in [`detect_live.py`](detect_live.py):

### 1. Camera Input Selection
Change the camera device index (default is `0`):
```python
# detect_live.py - line 11
cap = cv2.VideoCapture(0)  # Change to 1, 2, etc. for secondary/USB camera
```

### 2. Danger Zone (ROI) Corridor Geometry
Adjust the boundaries of the forward trajectory corridor:
```python
# detect_live.py - lines 47-50
zone_x1 = int(w * 0.30)  # Left limit (30% of screen width)
zone_x2 = int(w * 0.70)  # Right limit (70% of screen width)
zone_y1 = int(h * 0.60)  # Upper limit (60% down from top)
zone_y2 = h              # Lower limit (bottom edge)
```

### 3. Risk Threshold Calibration
Adjust the trigger sensitivity for alerts:
```python
# detect_live.py - lines 118-131
if risk_score < 30:
    status = "SAFE"      # Normal distance
elif risk_score < 70:
    status = "WARNING"   # Obstacle approaching
else:
    status = "DANGER"    # Collision hazard (alarm + banner)
```

### 4. Window Display Mode
By default, the display runs in fullscreen mode. To run in a standard resizable window:
```python
# In detect_live.py, comment out lines 18-22:
cv2.namedWindow("GAUD - Road Safety AI", cv2.WINDOW_NORMAL)
# cv2.setWindowProperty("GAUD - Road Safety AI", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
```

---

## ❓ Troubleshooting & FAQ

### Q1: `ResourceUnavailable: Program 'python.exe' failed to run`
- **Cause**: On Windows, typing `python` often invokes the unconfigured Microsoft Store stub.
- **Solution**: Always use the explicit virtual environment path:
  ```powershell
  .\venv\Scripts\python.exe detect_live.py
  ```

### Q2: `Cannot open camera`
- **Check 1**: Close any other app currently accessing the webcam (Zoom, Microsoft Teams, Discord, Chrome).
- **Check 2**: Run `python find_camera.py` to check which index your camera is registered on, and update `cv2.VideoCapture(index)` in `detect_live.py`.
- **Check 3**: On Windows 10/11, ensure **Camera privacy settings** allow desktop applications to access your camera.

### Q3: How to boost inference speed (FPS)?
- If you have an NVIDIA GPU, install the CUDA-accelerated PyTorch build:
  ```bash
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
  ```
- YOLOv8 nano (`yolov8n.pt`) is specifically designed to maintain smooth 30+ FPS even on modern standard CPUs.

---

## 👥 Authors & Acknowledgments

- **Lead Developer**: [tech-shakil](https://github.com/tech-shakil)
- **Collaborator**: [s-aminathu-saliha](https://github.com/s-aminathu-saliha)
- Built with [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) and [OpenCV](https://opencv.org/).

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for complete details.
