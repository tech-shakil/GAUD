# 🚗 GAUD — AI-Powered Real-Time Road Safety & Collision Warning System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/Model-YOLOv8-orange.svg)](https://github.com/ultralytics/ultralytics)
[![OpenCV](https://img.shields.io/badge/Vision-OpenCV-green.svg)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

An intelligent Advanced Driver Assistance System (ADAS) prototype powered by **YOLOv8** and **OpenCV**. **GAUD** performs real-time visual tracking of vehicles, cyclists, and pedestrians, dynamically evaluates proximity and collision trajectory, and alerts the driver with visual Head-Up Displays (HUD) and audible collision alarms.

---

## 📋 Table of Contents
- [✨ Key Features](#-key-features)
- [🧠 How It Works](#-how-it-works)
- [📁 Project Structure](#-project-structure)
- [⚙️ Prerequisites & Requirements](#️-prerequisites--requirements)
- [🚀 Step-by-Step Installation Guide](#-step-by-step-installation-guide)
- [💻 Usage & Running the System](#-usage--running-the-system)
- [🛠️ Configuration & Calibration](#️-configuration--calibration)
- [❓ Troubleshooting & FAQ](#-troubleshooting--faq)
- [📄 License](#-license)

---

## ✨ Key Features

- **Real-Time Multi-Class Road Object Detection**: Detects and tracks pedestrians (`person`), cars (`car`), motorcycles (`motorcycle`), buses (`bus`), trucks (`truck`), and bicycles (`bicycle`).
- **Dynamic Danger Zone (ROI)**: Focuses risk calculation within a defined forward-looking trajectory sector to reduce false alarms from off-road objects.
- **Intelligent Risk Scoring**: Computes instantaneous risk percentage using bounding box area expansion (object scale) and bottom-screen proximity.
- **3-Tier Threat State Machine**:
  - 🟢 **SAFE (< 30% Risk)**: Far distance, normal operating conditions.
  - 🟡 **WARNING (30% - 69% Risk)**: Medium distance hazard approaching.
  - 🔴 **DANGER (≥ 70% Risk)**: Immediate collision threat with flashing banner and audio alert.
- **Audible Hazard Warning**: Real-time acoustic buzzer alarm triggered when entering high collision risk.
- **Integrated Diagnostic Tools**: Pre-built diagnostic scripts to detect camera indices, test video feeds, and verify YOLO model readiness.

---

## 🧠 How It Works

```text
[ Camera Feed ] 
       │
       ▼
[ YOLOv8 Inference ] ──▶ Filters Road Classes (person, car, truck, etc.)
       │
       ▼
[ Danger Zone Check ] ──▶ Is Object Inside Forward Collision Zone?
       │
      YES
       ▼
[ Calculate Risk Score ] ──▶ Combines Box Size & Vertical Proximity
       │
       ├─ Risk < 30%  ──▶ Status: SAFE (Green)
       ├─ Risk 30-69% ──▶ Status: WARNING (Yellow)
       └─ Risk ≥ 70%  ──▶ Status: DANGER (Red Banner + Audio Buzzer Alarm)
       │
       ▼
[ Heads-Up Display (HUD) Rendered on Video Frame ]
```

---

## 📁 Project Structure

```text
GAUD/
├── detect_live.py        # Main application: Live detection, risk scoring & HUD
├── find_camera.py        # Utility: Detects all connected camera device indices
├── camera_check.py       # Utility: Tests video feed from each detected camera
├── camera_test.py        # Utility: Single camera preview test
├── test_yolo.py          # Sanity check: Verifies YOLO model loading
├── yolov8n.pt            # YOLOv8 nano pre-trained weights
├── requirements.txt      # Python dependencies list
├── .gitignore            # Git exclusion rules
└── README.md             # Project documentation and guide
```

---

## ⚙️ Prerequisites & Requirements

- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: Version **3.8** or higher (Python 3.10 / 3.11 recommended)
- **Hardware**:
  - Webcam / USB Camera / Dashcam
  - GPU recommended for ultra-high FPS, but CPU runs smoothly on YOLOv8 nano

---

## 🚀 Step-by-Step Installation Guide

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/GAUD.git
cd GAUD
```

### 2. Set Up a Virtual Environment (Recommended)

#### On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell gives a script execution policy error, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

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

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 💻 Usage & Running the System

### Step 1: Verify Available Cameras
If you have multiple cameras (built-in webcam, external USB camera, OBS virtual cam), identify your camera index:
```bash
python find_camera.py
```
This prints the status of camera indices `0` through `9`.

### Step 2: Test the Camera Feed
Ensure your camera opens and transmits video properly:
```bash
python camera_check.py
```
Or for a specific camera index (e.g., index `0` or `2`):
```bash
python camera_test.py
```

### Step 3: Run the Live Road Safety System
Launch the main collision avoidance application:
```bash
python detect_live.py
```

- The window will open in fullscreen HUD mode.
- Press **`q`** on your keyboard at any time to safely exit the application.

---

## 🛠️ Configuration & Calibration

You can customize detection settings directly inside `detect_live.py`:

### Changing Camera Index
If your external webcam is on index `1` instead of `0`:
```python
# Line 8 in detect_live.py
cap = cv2.VideoCapture(1)  # Change 0 to 1, 2, etc.
```

### Adjusting the Danger Zone (ROI)
The collision boundary is calculated as percentages of the frame width (`w`) and height (`h`):
```python
# Lines 44-47 in detect_live.py
zone_x1 = int(w * 0.30)  # Left boundary (30% from left)
zone_x2 = int(w * 0.70)  # Right boundary (70% from left)
zone_y1 = int(h * 0.60)  # Top boundary of zone (60% down)
zone_y2 = h              # Bottom boundary (full height)
```

### Adjusting Alert Thresholds
Modify when warnings and danger alarms trigger:
```python
# Lines 114-127 in detect_live.py
if risk_score < 30:
    status = "SAFE"
elif risk_score < 70:
    status = "WARNING"
else:
    status = "DANGER"  # Triggers buzzer + COLLISION RISK banner
```

### Windowed vs Fullscreen Mode
If you prefer a resizable window instead of fullscreen:
```python
# Replace lines 14-19 in detect_live.py with:
cv2.namedWindow("GAUD - Road Safety AI", cv2.WINDOW_NORMAL)
```

---

## ❓ Troubleshooting & FAQ

### 1. `Cannot open camera`
- Make sure no other application (Zoom, Teams, Discord, Browser) is using your webcam.
- Run `python find_camera.py` to identify which index your active camera is assigned to, then update `cv2.VideoCapture(index)` in `detect_live.py`.
- On Windows, ensure camera privacy settings allow desktop apps to access the camera.

### 2. Low Frame Rate / High Latency
- By default, YOLOv8 nano (`yolov8n.pt`) is optimized for CPU speed.
- If you have an NVIDIA GPU, ensure CUDA-enabled PyTorch is installed:
  ```bash
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
  ```

### 3. Missing Audio Warning on macOS/Linux
- Audio alerts use the Windows-native `winsound` module. On macOS and Linux, the system automatically falls back to an audible terminal bell (`\a`).

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
