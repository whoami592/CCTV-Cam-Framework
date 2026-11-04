<div align="center">

```
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣸⣏⠛⠻⠿⣿⣶⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣿⣿⣿⣷⣦⣤⣈⠙⠛⠿⣿⣷⣶⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣶⣦⣄⣈⠙⠻⠿⣿⣷⣶⣤⣀⡀⠀⠀⠀⠀⠀⠀
⠀⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣦⣄⡉⠛⠻⢿⣿⣷⣶⣤⣀⠀⠀
⠀⠀⠀⠉⠙⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣾⢻⣍⡉⠉⣿⠇⠀
⠀⠀⠀⠀⠀⠀⠀⢹⡏⢹⣿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⣰⣿⣿⣾⠏⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠘⣿⠈⣿⠸⣯⠉⠛⠿⢿⣿⣿⣿⣿⡏⠀⠻⠿⣿⠇⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢿⡆⢻⡄⣿⡀⠀⠀⠀⠈⠙⠛⠿⠿⠿⠿⠛⠋⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⣧⠘⣇⢸⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣀⣀⣿⣴⣿⢾⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣴⡶⠾⠟⠛⠋⢹⡏⠀⢹⡇⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢠⣿⠀⠀⠀⠀⢀⣈⣿⣶⠿⠿⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢸⣿⣴⠶⠞⠛⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
```

# 🎥 CCTV Cam Framework

**A multi-camera monitoring framework with motion detection, event-triggered recording, and a built-in exposure self-audit.**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-powered-green?logo=opencv&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![Storage](https://img.shields.io/badge/Storage-SQLite-003B57?logo=sqlite&logoColor=white)

**Coded by Mr Sabaz Ali Khan | Cyber Security Engineer**

</div>

---

## 📖 Overview

**CCTV Cam Framework** is a single-file, menu-driven Python tool for monitoring and managing multiple cameras from one place. It connects to RTSP/HTTP IP cameras and USB webcams, detects motion in real time, records clips only when something happens, logs every event to a local SQLite database, and cleans up old footage automatically.

It also includes a **self-audit module** that checks your own cameras for common exposure issues (open Telnet/FTP/HTTP ports, plain-text credentials, and more) and generates a hardening report.

## ✨ Features

- **Multi-camera support**: RTSP, HTTP/MJPEG, and USB webcams, each running in its own thread
- **Motion detection**: MOG2 background subtraction with configurable sensitivity and warm-up
- **Event-triggered recording**: saves `.mp4` clips when motion starts, stops after a cooldown, with a maximum clip length
- **Automatic snapshots**: JPEG snapshot captured at the moment motion is detected
- **Live grid view**: all cameras tiled in a single window, with motion boxes, timestamps, and a REC indicator
- **Headless / server mode**: run without a display and get periodic status lines in the terminal
- **Auto-reconnect**: dropped or offline streams are retried automatically
- **SQLite event log**: `ONLINE`, `OFFLINE`, `STREAM_LOST`, `MOTION`, `REC_START`, `REC_STOP`, and `AUDIT` events
- **Retention cleanup**: automatically deletes recordings and snapshots older than N days
- **Credential masking**: passwords in stream URLs are hidden in console output and logs
- **Config protection**: `cctv_config.json` is saved with `chmod 600` where supported
- **Self-audit**: port exposure check and hardening tips, saved as a text report
- **JSON export**: export recent events as a report

## 🛠️ Requirements

- Python 3.8 or newer
- `opencv-python`
- `numpy`

## 🚀 Installation

```bash
git clone https://github.com/<your-username>/cctv-cam-framework.git
cd cctv-cam-framework
pip install opencv-python numpy
```

## ▶️ Usage

```bash
python3 cctv_framework.py
```

You will see an interactive menu:

```
[1]  Start monitoring (live grid view)
[2]  Start monitoring (headless / server mode)
[3]  List cameras
[4]  Add camera
[5]  Remove camera
[6]  Enable / disable camera
[7]  Test camera connection
[8]  View recent events
[9]  Event statistics
[10] Export events report (JSON)
[11] Camera self-audit (your own cameras)
[12] Settings
[13] Cleanup old recordings now
[0]  Exit
```

### Quick start

1. Choose **[4] Add camera** and enter a name and source.
2. Choose **[7] Test camera connection** to confirm the stream opens.
3. Choose **[1]** for the live grid, or **[2]** for headless mode.
4. Press `q` or `Esc` in the live window (or `Ctrl+C` in headless mode) to stop.

### Camera source examples

| Type | Example |
|------|---------|
| USB webcam | `0` |
| RTSP camera | `rtsp://user:pass@192.168.1.10:554/stream1` |
| HTTP / MJPEG | `http://192.168.1.20:8080/video` |

## ⚙️ Configuration

On first run, a `cctv_config.json` file is created next to the script:

```json
{
  "cameras": [
    { "name": "Gate", "source": "rtsp://user:pass@192.168.1.10:554/stream1", "enabled": true }
  ],
  "motion": { "min_area": 1500, "var_threshold": 25, "warmup_frames": 60 },
  "recording": { "cooldown_sec": 8, "max_clip_sec": 120, "fps": 15, "snapshot_on_motion": true },
  "retention_days": 14,
  "reconnect_delay_sec": 5
}
```

| Setting | Description |
|---------|-------------|
| `motion.min_area` | Minimum size of a moving object to count as motion (higher = less sensitive) |
| `motion.var_threshold` | MOG2 background-subtraction sensitivity |
| `motion.warmup_frames` | Frames used to learn the background before detection starts |
| `recording.cooldown_sec` | Seconds without motion before a clip is closed |
| `recording.max_clip_sec` | Maximum length of a single clip |
| `recording.fps` | Frame rate of saved clips |
| `recording.snapshot_on_motion` | Save a JPEG when motion begins |
| `retention_days` | Age after which recordings and snapshots are deleted |
| `reconnect_delay_sec` | Wait time before retrying a lost stream |

Motion, cooldown, clip length, and retention can also be changed from menu option **[12] Settings**.

## 📂 Output Structure

```
cctv-cam-framework/
├── cctv_framework.py
├── cctv_config.json      # camera list and settings
├── cctv_events.db        # SQLite event log
├── recordings/<camera>/  # motion-triggered .mp4 clips
├── snapshots/<camera>/   # motion snapshots (.jpg)
└── reports/              # audit reports and JSON event exports
```

## 🔍 Self-Audit Module

Menu option **[11]** performs a basic exposure check on cameras configured in the framework. It:

- Scans common camera ports (RTSP 554/8554, HTTP 80/8080, HTTPS 443, 8000, Dahua SDK 37777, Telnet 23, FTP 21, SSH 22)
- Warns about Telnet, FTP, and unencrypted HTTP services
- Flags plain-text credentials in the config and streams with no credentials
- Saves a report to `reports/audit_<timestamp>.txt` with hardening tips (change default passwords, update firmware, disable UPnP, isolate cameras on a VLAN, never port-forward RTSP to the internet)

The tool asks for explicit confirmation before running.

## ⚠️ Legal Disclaimer

This project is intended for **monitoring and security-testing cameras that you own or are explicitly authorised to access and assess**. Unauthorised access to, or scanning of, systems you do not own is illegal in most jurisdictions. Also make sure your use of video recording complies with local privacy and surveillance laws. The author accepts no responsibility for misuse.

## 🔐 Security Notes

- Camera credentials in `cctv_config.json` are stored in plain text; the file is restricted to `600` permissions where the OS allows it. Prefer a dedicated, view-only camera account.
- Passwords are masked in console output and event logs.
- Keep cameras on an isolated network and never expose RTSP directly to the internet.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to open an issue or submit a pull request.

## 📜 License

Released under the MIT License. Add a `LICENSE` file to your repository to make this official.

## 👤 Author

**Mr Sabaz Ali Khan**
Cyber Security Engineer

> *Coded by Mr Sabaz Ali Khan*

---

<div align="center">

⭐ If you find this project useful, please give it a star!

</div>
