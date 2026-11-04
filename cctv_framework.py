#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCTV Cam Framework
Multi-camera monitoring framework: RTSP/HTTP/USB cameras, motion detection,
event-triggered recording, snapshots, SQLite event log, retention cleanup,
live grid view and a self-audit for cameras YOU own.

Coded by Mr Sabaz Ali Khan (Cyber Security Engineer)

Install:  pip install opencv-python numpy
Run:      python3 cctv_framework.py
"""
import os
import sys
import json
import time
import socket
import sqlite3
import threading
import datetime as dt
from urllib.parse import urlparse

try:
    import cv2
    import numpy as np
except ImportError:
    print("[!] Missing dependencies. Run: pip install opencv-python numpy")
    sys.exit(1)

BANNER = r"""
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
"""
TITLE = "CCTV CAM FRAMEWORK"
CREDIT = "Coded by Mr Sabaz Ali Khan | Cyber Security Engineer"

BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE, "cctv_config.json")
DB_PATH = os.path.join(BASE, "cctv_events.db")
REC_DIR = os.path.join(BASE, "recordings")
SNAP_DIR = os.path.join(BASE, "snapshots")
REPORT_DIR = os.path.join(BASE, "reports")

DEFAULT_CONFIG = {
    "cameras": [],  # {"name": "Gate", "source": "rtsp://user:pass@192.168.1.10:554/stream1", "enabled": true}
    "motion": {"min_area": 1500, "var_threshold": 25, "warmup_frames": 60},
    "recording": {"cooldown_sec": 8, "max_clip_sec": 120, "fps": 15, "snapshot_on_motion": True},
    "retention_days": 14,
    "reconnect_delay_sec": 5,
}

lock_print = threading.Lock()


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def banner():
    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)
    print(f"  {TITLE}")
    print(f"  {CREDIT}")
    print("  " + "=" * 56)


def now():
    return dt.datetime.now()


def stamp():
    return now().strftime("%Y%m%d_%H%M%S")


def mask_source(src):
    """Hide credentials in URLs before printing/logging."""
    try:
        u = urlparse(str(src))
        if u.password:
            return str(src).replace(u.password, "****")
    except Exception:
        pass
    return str(src)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return json.loads(json.dumps(DEFAULT_CONFIG))
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    for k, v in DEFAULT_CONFIG.items():
        cfg.setdefault(k, v)
    return cfg


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    try:
        os.chmod(CONFIG_PATH, 0o600)  # may contain camera credentials
    except Exception:
        pass


def ensure_dirs():
    for d in (REC_DIR, SNAP_DIR, REPORT_DIR):
        os.makedirs(d, exist_ok=True)


def parse_source(src):
    s = str(src).strip()
    return int(s) if s.isdigit() else s


# --------------------------------------------------------------------------- #
# Event log (SQLite)
# --------------------------------------------------------------------------- #
class EventLog:
    def __init__(self, path=DB_PATH):
        self.path = path
        self.lock = threading.Lock()
        con = sqlite3.connect(self.path)
        con.execute("""CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT, camera TEXT, type TEXT, detail TEXT, file TEXT)""")
        con.commit()
        con.close()

    def add(self, camera, etype, detail="", file=""):
        with self.lock:
            con = sqlite3.connect(self.path)
            con.execute("INSERT INTO events(ts,camera,type,detail,file) VALUES(?,?,?,?,?)",
                        (now().isoformat(timespec="seconds"), camera, etype, detail, file))
            con.commit()
            con.close()

    def recent(self, limit=25, camera=None):
        con = sqlite3.connect(self.path)
        q = "SELECT ts,camera,type,detail,file FROM events"
        args = []
        if camera:
            q += " WHERE camera=?"
            args.append(camera)
        q += " ORDER BY id DESC LIMIT ?"
        args.append(limit)
        rows = con.execute(q, args).fetchall()
        con.close()
        return rows

    def stats(self):
        con = sqlite3.connect(self.path)
        rows = con.execute("SELECT camera,type,COUNT(*) FROM events GROUP BY camera,type").fetchall()
        con.close()
        return rows


# --------------------------------------------------------------------------- #
# Camera worker: capture + motion + recording
# --------------------------------------------------------------------------- #
class CameraWorker(threading.Thread):
    def __init__(self, cam, cfg, log):
        super().__init__(daemon=True)
        self.name_ = cam["name"]
        self.source = parse_source(cam["source"])
        self.cfg = cfg
        self.log = log
        self.stop_evt = threading.Event()
        self.frame_lock = threading.Lock()
        self.frame = None
        self.status = "starting"
        self.fps = 0.0
        self.motion_now = False
        self.motion_count = 0
        self.writer = None
        self.rec_started = 0
        self.last_motion = 0
        self.clip_path = ""

    # ---- recording
    def _start_rec(self, frame):
        h, w = frame.shape[:2]
        fps = self.cfg["recording"]["fps"]
        cam_dir = os.path.join(REC_DIR, self.name_)
        os.makedirs(cam_dir, exist_ok=True)
        self.clip_path = os.path.join(cam_dir, f"{self.name_}_{stamp()}.mp4")
        self.writer = cv2.VideoWriter(self.clip_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
        self.rec_started = time.time()
        self.log.add(self.name_, "REC_START", "motion triggered", self.clip_path)

    def _stop_rec(self):
        if self.writer is not None:
            self.writer.release()
            self.writer = None
            self.log.add(self.name_, "REC_STOP", f"{int(time.time() - self.rec_started)}s", self.clip_path)

    def _snapshot(self, frame):
        d = os.path.join(SNAP_DIR, self.name_)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, f"{self.name_}_{stamp()}.jpg")
        cv2.imwrite(p, frame)
        return p

    # ---- main loop
    def run(self):
        mcfg = self.cfg["motion"]
        rcfg = self.cfg["recording"]
        delay = self.cfg["reconnect_delay_sec"]
        while not self.stop_evt.is_set():
            cap = cv2.VideoCapture(self.source)
            if not cap.isOpened():
                self.status = "offline"
                self.log.add(self.name_, "OFFLINE", mask_source(self.source))
                if self.stop_evt.wait(delay):
                    break
                continue
            self.status = "online"
            self.log.add(self.name_, "ONLINE", mask_source(self.source))
            bg = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=mcfg["var_threshold"],
                                                    detectShadows=False)
            frames, t0, warm = 0, time.time(), 0
            while not self.stop_evt.is_set():
                ok, frame = cap.read()
                if not ok or frame is None:
                    self.status = "lost"
                    self.log.add(self.name_, "STREAM_LOST", "reconnecting")
                    break
                frames += 1
                if time.time() - t0 >= 2:
                    self.fps = frames / (time.time() - t0)
                    frames, t0 = 0, time.time()

                small = cv2.resize(frame, (640, int(frame.shape[0] * 640 / frame.shape[1])))
                gray = cv2.GaussianBlur(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY), (21, 21), 0)
                mask = bg.apply(gray)
                warm += 1
                moving = False
                if warm > mcfg["warmup_frames"]:
                    mask = cv2.dilate(cv2.erode(mask, None, iterations=2), None, iterations=3)
                    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    sx = frame.shape[1] / small.shape[1]
                    for c in cnts:
                        if cv2.contourArea(c) >= mcfg["min_area"] / 4:
                            moving = True
                            x, y, w, h = cv2.boundingRect(c)
                            cv2.rectangle(frame, (int(x * sx), int(y * sx)),
                                          (int((x + w) * sx), int((y + h) * sx)), (0, 0, 255), 2)

                cv2.putText(frame, f"{self.name_}  {now().strftime('%Y-%m-%d %H:%M:%S')}",
                            (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                t = time.time()
                if moving:
                    if not self.motion_now:
                        self.motion_count += 1
                        snap = self._snapshot(frame) if rcfg["snapshot_on_motion"] else ""
                        self.log.add(self.name_, "MOTION", "motion detected", snap)
                    self.last_motion = t
                    if self.writer is None:
                        self._start_rec(frame)
                self.motion_now = moving

                if self.writer is not None:
                    cv2.circle(frame, (frame.shape[1] - 20, 20), 8, (0, 0, 255), -1)
                    self.writer.write(frame)
                    if (t - self.last_motion > rcfg["cooldown_sec"]) or (t - self.rec_started > rcfg["max_clip_sec"]):
                        self._stop_rec()

                with self.frame_lock:
                    self.frame = frame
            cap.release()
            self._stop_rec()
            if self.stop_evt.wait(delay):
                break
        self._stop_rec()
        self.status = "stopped"

    def get_frame(self):
        with self.frame_lock:
            return None if self.frame is None else self.frame.copy()

    def stop(self):
        self.stop_evt.set()


# --------------------------------------------------------------------------- #
# Retention
# --------------------------------------------------------------------------- #
def cleanup_old(days):
    cutoff = time.time() - days * 86400
    removed = 0
    for root_dir in (REC_DIR, SNAP_DIR):
        for root, _, files in os.walk(root_dir):
            for f in files:
                p = os.path.join(root, f)
                try:
                    if os.path.getmtime(p) < cutoff:
                        os.remove(p)
                        removed += 1
                except OSError:
                    pass
    return removed


# --------------------------------------------------------------------------- #
# Monitor (headless or live grid)
# --------------------------------------------------------------------------- #
def build_grid(frames, cell=(480, 270)):
    tiles = []
    for name, fr in frames:
        if fr is None:
            tile = np.zeros((cell[1], cell[0], 3), np.uint8)
            cv2.putText(tile, f"{name}: no signal", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            tile = cv2.resize(fr, cell)
        tiles.append(tile)
    if not tiles:
        return None
    cols = 1 if len(tiles) == 1 else 2 if len(tiles) <= 4 else 3
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    return np.vstack(rows)


def monitor(cfg, log, live=True):
    cams = [c for c in cfg["cameras"] if c.get("enabled", True)]
    if not cams:
        print("[!] No enabled cameras. Add one first.")
        return
    removed = cleanup_old(cfg["retention_days"])
    if removed:
        print(f"[*] Retention cleanup removed {removed} old file(s)")
    workers = [CameraWorker(c, cfg, log) for c in cams]
    for w in workers:
        w.start()
    print(f"[*] Monitoring {len(workers)} camera(s). {'Press q in the window' if live else 'Press Ctrl+C'} to stop.")
    try:
        while True:
            if live:
                grid = build_grid([(w.name_, w.get_frame()) for w in workers])
                if grid is not None:
                    cv2.imshow("CCTV Cam Framework - Mr Sabaz Ali Khan", grid)
                if cv2.waitKey(30) & 0xFF in (ord("q"), 27):
                    break
            else:
                time.sleep(5)
                line = " | ".join(f"{w.name_}:{w.status} {w.fps:.0f}fps motion={w.motion_count}" for w in workers)
                print(f"[{now().strftime('%H:%M:%S')}] {line}")
    except KeyboardInterrupt:
        pass
    finally:
        for w in workers:
            w.stop()
        for w in workers:
            w.join(timeout=5)
        cv2.destroyAllWindows()
        print("[*] Monitor stopped.")


# --------------------------------------------------------------------------- #
# Camera management / tests
# --------------------------------------------------------------------------- #
def list_cameras(cfg):
    if not cfg["cameras"]:
        print("  (no cameras configured)")
    for i, c in enumerate(cfg["cameras"], 1):
        print(f"  {i}. {c['name']:<15} {'ON ' if c.get('enabled', True) else 'OFF'}  {mask_source(c['source'])}")


def add_camera(cfg):
    name = input("Camera name (no spaces, e.g. Gate): ").strip().replace(" ", "_")
    print("Source examples:  0 (USB webcam) | rtsp://user:pass@192.168.1.10:554/stream1 | http://ip:8080/video")
    src = input("Source: ").strip()
    if not name or not src:
        print("[!] Name and source required")
        return
    cfg["cameras"].append({"name": name, "source": src, "enabled": True})
    save_config(cfg)
    print("[+] Camera added")


def remove_camera(cfg):
    list_cameras(cfg)
    try:
        i = int(input("Remove which number: ")) - 1
        c = cfg["cameras"].pop(i)
        save_config(cfg)
        print(f"[+] Removed {c['name']}")
    except (ValueError, IndexError):
        print("[!] Invalid choice")


def toggle_camera(cfg):
    list_cameras(cfg)
    try:
        i = int(input("Toggle which number: ")) - 1
        c = cfg["cameras"][i]
        c["enabled"] = not c.get("enabled", True)
        save_config(cfg)
        print(f"[+] {c['name']} -> {'ON' if c['enabled'] else 'OFF'}")
    except (ValueError, IndexError):
        print("[!] Invalid choice")


def test_camera(cfg):
    list_cameras(cfg)
    try:
        i = int(input("Test which number: ")) - 1
        c = cfg["cameras"][i]
    except (ValueError, IndexError):
        print("[!] Invalid choice")
        return
    print(f"[*] Opening {c['name']} ...")
    t = time.time()
    cap = cv2.VideoCapture(parse_source(c["source"]))
    if not cap.isOpened():
        print("[-] Could not open stream (check URL, credentials, network)")
        return
    ok, fr = cap.read()
    cap.release()
    if ok:
        h, w = fr.shape[:2]
        p = os.path.join(SNAP_DIR, f"test_{c['name']}_{stamp()}.jpg")
        os.makedirs(SNAP_DIR, exist_ok=True)
        cv2.imwrite(p, fr)
        print(f"[+] OK  {w}x{h}  in {time.time() - t:.1f}s  test frame saved: {p}")
    else:
        print("[-] Opened but no frame received")


def self_audit(cfg, log):
    """Basic exposure check for cameras you own/are authorised to assess."""
    print("\n[!] Run this ONLY against cameras you own or are authorised to test.")
    if input("Confirm authorised (yes/no): ").strip().lower() != "yes":
        return
    ports = {554: "RTSP", 80: "HTTP", 443: "HTTPS", 8000: "HTTP-alt/SDK", 8080: "HTTP-alt",
             8554: "RTSP-alt", 37777: "Dahua SDK", 23: "Telnet", 21: "FTP", 22: "SSH"}
    report = [f"CCTV Self-Audit  {now().isoformat(timespec='seconds')}", CREDIT, ""]
    for c in cfg["cameras"]:
        u = urlparse(str(c["source"]))
        host = u.hostname
        if not host:
            continue
        report.append(f"== {c['name']} ({host})")
        print(f"\n[*] {c['name']} ({host})")
        if u.scheme == "rtsp" and u.password:
            report.append("  [WARN] Credentials stored in plain text in config (file is chmod 600; prefer a dedicated viewer account)")
        if u.scheme in ("http", "rtsp") and not u.password and not u.username:
            report.append("  [WARN] No credentials in URL - confirm stream requires authentication")
        for p, svc in ports.items():
            s = socket.socket()
            s.settimeout(1.0)
            open_ = s.connect_ex((host, p)) == 0
            s.close()
            if open_:
                flag = "  [WARN]" if p in (23, 21, 80, 8080) else "  [INFO]"
                msg = f"{flag} port {p}/{svc} open"
                if p == 23:
                    msg += " - Telnet should be disabled"
                if p in (80, 8080, 21):
                    msg += " - unencrypted service, restrict to LAN / use HTTPS"
                print(msg)
                report.append(msg)
        report += ["  Tips: change default passwords, update firmware, disable UPnP, keep cameras on an isolated VLAN, never port-forward RTSP to the internet.", ""]
    path = os.path.join(REPORT_DIR, f"audit_{stamp()}.txt")
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    log.add("-", "AUDIT", "self-audit run", path)
    print(f"\n[+] Report saved: {path}")


def show_events(log):
    cam = input("Filter by camera name (blank = all): ").strip() or None
    rows = log.recent(30, cam)
    if not rows:
        print("  (no events)")
    for ts, camn, typ, det, fil in rows:
        print(f"  {ts}  {camn:<12} {typ:<12} {det}  {os.path.basename(fil) if fil else ''}")


def show_stats(log):
    rows = log.stats()
    if not rows:
        print("  (no data)")
    for camn, typ, n in rows:
        print(f"  {camn:<14} {typ:<12} {n}")


def export_report(log):
    rows = log.recent(1000)
    path = os.path.join(REPORT_DIR, f"events_{stamp()}.json")
    os.makedirs(REPORT_DIR, exist_ok=True)
    data = [dict(ts=r[0], camera=r[1], type=r[2], detail=r[3], file=r[4]) for r in rows]
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"credit": CREDIT, "generated": now().isoformat(timespec="seconds"), "events": data}, f, indent=2)
    print(f"[+] Exported {len(data)} events -> {path}")


def settings(cfg):
    print(f"  1. Motion min_area      : {cfg['motion']['min_area']}")
    print(f"  2. Motion var_threshold : {cfg['motion']['var_threshold']}")
    print(f"  3. Record cooldown (s)  : {cfg['recording']['cooldown_sec']}")
    print(f"  4. Max clip length (s)  : {cfg['recording']['max_clip_sec']}")
    print(f"  5. Retention (days)     : {cfg['retention_days']}")
    ch = input("Change which (blank = back): ").strip()
    try:
        if ch == "1": cfg["motion"]["min_area"] = int(input("New value: "))
        elif ch == "2": cfg["motion"]["var_threshold"] = int(input("New value: "))
        elif ch == "3": cfg["recording"]["cooldown_sec"] = int(input("New value: "))
        elif ch == "4": cfg["recording"]["max_clip_sec"] = int(input("New value: "))
        elif ch == "5": cfg["retention_days"] = int(input("New value: "))
        else: return
        save_config(cfg)
        print("[+] Saved")
    except ValueError:
        print("[!] Numbers only")


# --------------------------------------------------------------------------- #
# Menu
# --------------------------------------------------------------------------- #
MENU = """
  [1] Start monitoring (live grid view)
  [2] Start monitoring (headless / server mode)
  [3] List cameras
  [4] Add camera
  [5] Remove camera
  [6] Enable / disable camera
  [7] Test camera connection
  [8] View recent events
  [9] Event statistics
  [10] Export events report (JSON)
  [11] Camera self-audit (your own cameras)
  [12] Settings
  [13] Cleanup old recordings now
  [0] Exit
"""


def main():
    ensure_dirs()
    cfg = load_config()
    log = EventLog()
    while True:
        banner()
        print(MENU)
        ch = input("  Select > ").strip()
        print()
        if ch == "1": monitor(cfg, log, live=True)
        elif ch == "2": monitor(cfg, log, live=False)
        elif ch == "3": list_cameras(cfg)
        elif ch == "4": add_camera(cfg)
        elif ch == "5": remove_camera(cfg)
        elif ch == "6": toggle_camera(cfg)
        elif ch == "7": test_camera(cfg)
        elif ch == "8": show_events(log)
        elif ch == "9": show_stats(log)
        elif ch == "10": export_report(log)
        elif ch == "11": self_audit(cfg, log)
        elif ch == "12": settings(cfg)
        elif ch == "13": print(f"[+] Removed {cleanup_old(cfg['retention_days'])} file(s)")
        elif ch == "0":
            print(f"\n  {CREDIT}\n")
            break
        else:
            print("[!] Invalid option")
        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n  {CREDIT}\n")
