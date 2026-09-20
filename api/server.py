from __future__ import annotations

import time
from pathlib import Path
from threading import Lock

import cv2
import numpy as np
from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from vision.camera import AUREXCamera
from vision.human_detector import AUREXHumanDetector
from vision.person_tracker import AUREXPersonTracker


# ============================================================
# AUREX PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT / "frontend"


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AUREX Spatial Intelligence",
    version="1.0.0",
    description="AUREX real-time spatial intelligence backend",
)


# ============================================================
# AUREX VISION COMPONENTS
# ============================================================

camera = AUREXCamera()
detector = AUREXHumanDetector()
tracker = AUREXPersonTracker()

camera_lock = Lock()


# ============================================================
# RUNTIME STATE
# ============================================================

runtime_state = {
    "online": True,
    "camera": False,
    "camera_enabled": False,
    "people_count": 0,
    "object_count": 0,
    "fps": 0.0,
    "uptime": 0.0,
    "last_update": 0.0,
}

start_time = time.time()


# ============================================================
# RUNTIME UPDATE
# ============================================================

def update_runtime(
    people_count: int,
    fps: float,
    camera_active: bool,
) -> None:

    runtime_state["online"] = True

    runtime_state["camera"] = camera_active

    runtime_state["people_count"] = int(
        people_count
    )

    runtime_state["fps"] = round(
        float(fps),
        1,
    )

    runtime_state["uptime"] = round(
        time.time() - start_time,
        1,
    )

    runtime_state["last_update"] = time.time()


# ============================================================
# CAMERA ACCESS
# ============================================================

def get_camera():

    with camera_lock:

        if not camera.open():
            return None

        return camera


# ============================================================
# ERROR FRAME
# ============================================================

def create_error_frame(message: str):

    image = np.zeros(
        (480, 640, 3),
        dtype=np.uint8,
    )

    cv2.putText(
        image,
        message,
        (45, 240),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (220, 230, 240),
        2,
        cv2.LINE_AA,
    )

    return image


# ============================================================
# API — CAMERA START
# ============================================================

@app.post("/api/camera/start")
def camera_start():

    with camera_lock:

        try:

            if camera.open():

                runtime_state["camera"] = True

                return {
                    "status": "started",
                    "camera": True,
                    "message": "AUREX camera started",
                }

            runtime_state["camera"] = False

            return {
                "status": "unavailable",
                "camera": False,
                "message": "AUREX camera could not be opened",
            }

        except Exception as exc:

            runtime_state["camera"] = False

            return {
                "status": "error",
                "camera": False,
                "message": str(exc),
            }


# ============================================================
# API — CAMERA STOP
# ============================================================

@app.post("/api/camera/stop")
def camera_stop():

    with camera_lock:

        try:

            camera.release()

            runtime_state["camera"] = False
            runtime_state["people_count"] = 0
            runtime_state["object_count"] = 0
            runtime_state["fps"] = 0.0
            runtime_state["last_update"] = time.time()

            return {
                "status": "stopped",
                "camera": False,
                "message": "AUREX camera released",
            }

        except Exception as exc:

            return {
                "status": "error",
                "camera": False,
                "message": str(exc),
            }


# ============================================================
# LIVE CAMERA STREAM
# ============================================================

def generate_frames():

    cam = get_camera()

    if cam is None:

        placeholder = cv2.imencode(
            ".jpg",
            create_error_frame(
                "AUREX CAMERA UNAVAILABLE"
            ),
        )[1].tobytes()

        while True:

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + placeholder
                + b"\r\n"
            )

            time.sleep(1)

        return

    frame_counter = 0
    fps_timer = time.time()
    current_fps = 0.0

    while True:

        frame = cam.read()

        if frame is None:

            runtime_state["camera"] = False
            runtime_state["people_count"] = 0
            runtime_state["fps"] = 0.0

            break

        frame_counter += 1

        elapsed = time.time() - fps_timer

        if elapsed >= 1.0:

            current_fps = (
                frame_counter / elapsed
            )

            frame_counter = 0
            fps_timer = time.time()

        try:

            # ------------------------------------------------
            # HUMAN DETECTION
            # ------------------------------------------------

            detections = detector.detect(
                frame
            )

            people_count = len(
                detections
            )

            # ------------------------------------------------
            # PERSON TRACKING
            # ------------------------------------------------

            tracks = tracker.update(
                detections,
                frame.shape[1],
            )

            # ------------------------------------------------
            # VISUAL OVERLAYS
            # ------------------------------------------------

            for person in tracks:

                x1 = int(person.x1)
                y1 = int(person.y1)
                x2 = int(person.x2)
                y2 = int(person.y2)

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (180, 220, 255),
                    2,
                )

                label = (
                    f"PERSON {person.person_id}"
                )

                cv2.putText(
                    frame,
                    label,
                    (
                        x1,
                        max(
                            25,
                            y1 - 10,
                        ),
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (220, 235, 255),
                    2,
                    cv2.LINE_AA,
                )

            # ------------------------------------------------
            # UPDATE RUNTIME
            # ------------------------------------------------

            update_runtime(
                people_count=people_count,
                fps=current_fps,
                camera_active=True,
            )

        except Exception as exc:

            cv2.putText(
                frame,
                (
                    "PERCEPTION ERROR: "
                    + str(exc)[:70]
                ),
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (80, 120, 255),
                2,
                cv2.LINE_AA,
            )

            update_runtime(
                people_count=0,
                fps=current_fps,
                camera_active=True,
            )

        # ----------------------------------------------------
        # AUREX WATERMARK
        # ----------------------------------------------------

        cv2.putText(
            frame,
            "AUREX // LIVE SPATIAL PERCEPTION",
            (
                20,
                frame.shape[0] - 25,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (220, 230, 240),
            2,
            cv2.LINE_AA,
        )

        # ----------------------------------------------------
        # JPEG ENCODING
        # ----------------------------------------------------

        success, encoded = cv2.imencode(
            ".jpg",
            frame,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                82,
            ],
        )

        if not success:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + encoded.tobytes()
            + b"\r\n"
        )

    # --------------------------------------------------------
    # STREAM ENDED
    # --------------------------------------------------------

    runtime_state["camera_enabled"] = False
    runtime_state["camera"] = False
    runtime_state["people_count"] = 0
    runtime_state["fps"] = 0.0


# ============================================================
# API — HEALTH
# ============================================================

@app.get("/api/health")
def health():

    return {
        "status": "online",
        "service": "AUREX Spatial Intelligence",
        "version": "1.0.0",
        "backend": True,
        "timestamp": time.time(),
    }


# ============================================================
# API — RUNTIME STATUS
# ============================================================

@app.get("/api/status")
def status():

    runtime_state["uptime"] = round(
        time.time() - start_time,
        1,
    )

    return {
        **runtime_state,
        "status": "online",
        "service": "AUREX Spatial Intelligence",
    }


# ============================================================
# API — CAMERA STATUS
# ============================================================

@app.get("/api/camera/status")
def camera_status():

    return {
        "active": runtime_state[
            "camera"
        ],
        "people_count": runtime_state[
            "people_count"
        ],
        "fps": runtime_state[
            "fps"
        ],
    }


# ============================================================
# API — LIVE CAMERA
# ============================================================

@app.get("/api/camera/stream")
def camera_stream():

    return StreamingResponse(
        generate_frames(),
        media_type=(
            "multipart/x-mixed-replace;"
            " boundary=frame"
        ),
    )


# ============================================================
# FRONTEND
# ============================================================

@app.get("/")
def frontend():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# ============================================================
# FRONTEND STATIC FILES
#
# This exposes:
#
# /style.css
# /app.js
# /assets/*
# ============================================================

app.mount(
    "/",
    StaticFiles(
        directory=FRONTEND_DIR,
        html=True,
    ),
    name="frontend",
)


# ============================================================
# SHUTDOWN
# ============================================================

@app.on_event("shutdown")
def shutdown():

    try:

        camera.release()

    except Exception:

        pass