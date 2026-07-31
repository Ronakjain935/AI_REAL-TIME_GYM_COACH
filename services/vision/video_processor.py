import os
import cv2
import av
import numpy as np
import mediapipe as mp
import threading
import sys
from streamlit_webrtc import VideoProcessorBase

from detectors.squats import SquatDetector
from detectors.pushup import PushupDetector
from detectors.biceps_curl import BicepsCurlDetector
from detectors.shoulder_press import ShoulderPressDetector
from detectors.lunges import LungesDetector
from services.config.workout_config import POSE_CONNECTIONS

class VideoProcessorClass(VideoProcessorBase):
    def __init__(self):
        self._lock = threading.Lock()
        self._latest_metrics = None
        self._exercise_type = "Squats"

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.model_path = os.path.join(base_dir, "ml_models", "pose_landmarker_full.task")

        self.use_tasks_api = False
        self._pose_legacy = None
        self._landmarker = None
        self._mp_initialized = False

        self._detectors = {
            "Squats": SquatDetector(),
            "Push-ups": PushupDetector(),
            "Biceps Curls (Dumbell)": BicepsCurlDetector(),
            "Biceps Curls (Dumbbell)": BicepsCurlDetector(),
            "Biceps curl (Dumbell)": BicepsCurlDetector(),
            "Shoulder Press": ShoulderPressDetector(),
            "Lunges": LungesDetector(),
        }

        self._frame_timestamps_ms = 0
        self.latest_result = {}

    def _init_mediapipe(self):
        with self._lock:
            if self._mp_initialized:
                return
            self._mp_initialized = True

            # Attempt legacy solutions API first
            try:
                if hasattr(mp, 'solutions') and hasattr(getattr(mp, 'solutions', None), 'pose'):
                    self._pose_legacy = mp.solutions.pose.Pose(
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5,
                        model_complexity=1
                    )
                    self.use_tasks_api = False
                    print("[INFO] MediaPipe Legacy Pose initialized successfully.")
                    return
            except Exception as e:
                print(f"[Warning] MediaPipe solutions.pose failed: {e}")
                self._pose_legacy = None

            # Fallback to Tasks API
            self.use_tasks_api = True
            try:
                import ctypes
                for lib in ['libGLESv2.so.2', 'libGL.so.1', 'libEGL.so.1']:
                    try:
                        ctypes.CDLL(lib)
                    except Exception:
                        pass
            except Exception:
                pass

            try:
                from mediapipe.tasks import python
                from mediapipe.tasks.python import vision

                delegate = getattr(python.BaseOptions, 'Delegate', None)
                cpu_delegate = getattr(delegate, 'CPU', None) if delegate else None

                if cpu_delegate is not None:
                    base_option = python.BaseOptions(model_asset_path=self.model_path, delegate=cpu_delegate)
                else:
                    base_option = python.BaseOptions(model_asset_path=self.model_path)

                options = vision.PoseLandmarkerOptions(
                    base_options=base_option,
                    running_mode=vision.RunningMode.VIDEO,
                    min_pose_detection_confidence=0.7,
                    min_pose_presence_confidence=0.7,
                    min_tracking_confidence=0.7,
                    output_segmentation_masks=False
                )
                self._landmarker = vision.PoseLandmarker.create_from_options(options)
                print("[INFO] MediaPipe Tasks PoseLandmarker initialized successfully.")
            except Exception as e:
                print(f"[Warning] Could not initialize PoseLandmarker: {e}")
                self._landmarker = None

    def set_latest_metrics(self, metrics):
        with self._lock:
            self._latest_metrics = metrics.copy()
            self.latest_result = metrics.copy()

    def get_latest_metrics(self):
        with self._lock:
            return None if self._latest_metrics is None else self._latest_metrics.copy()

    def set_exercise(self, exercise_type):
        with self._lock:
            if self._exercise_type != exercise_type:
                self._exercise_type = exercise_type
                detector_obj = self._detectors.get(exercise_type)
                if detector_obj:
                    detector_obj.reset()
                self._latest_metrics = None
                self.latest_result = {}

    def get_exercise(self):
        with self._lock:
            return self._exercise_type

    def _draw_skeleton(self, img, landmarks):
        h, w = img.shape[:2]
        for start_idx, end_idx in POSE_CONNECTIONS:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                p1 = landmarks[start_idx]
                p2 = landmarks[end_idx]

                if getattr(p1, 'visibility', 1.0) > 0.65 and getattr(p2, 'visibility', 1.0) > 0.65:
                    cv2.line(
                        img,
                        (int(p1.x * w), int(p1.y * h)),
                        (int(p2.x * w), int(p2.y * h)),
                        (254, 242, 0),
                        4
                    )

        for lm in landmarks:
            if getattr(lm, 'visibility', 1.0) > 0.65:
                cv2.circle(
                    img, 
                    (int(lm.x * w), int(lm.y * h)),
                    6,
                    (129, 185, 16),
                    -1
                )

    def _draw_no_pose_warnings(self, img):
        h, w = img.shape[:2]
        cv2.rectangle(img, (20, 20), (w - 20, 90), (15, 23, 42), -1)
        cv2.rectangle(img, (20, 20), (w - 20, 90), (239, 68, 68), 2)
        cv2.putText(img, "NO POSE DETECTED", (40, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (239, 68, 68), 2, cv2.LINE_AA)
        cv2.putText(img, "PLEASE STEP INTO THE CAMERA FRAME", (40, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)

    def _draw_overlays(self, img, metrics, ex_type):
        h, w = img.shape[:2]
        reps = metrics.get("reps", 0)
        detector_obj = self._detectors.get(ex_type)
        stage = getattr(detector_obj, "stage", None) or "N/A"

        # Top-Left REP HUD Card
        overlay = img.copy()
        cv2.rectangle(overlay, (15, 15), (290, 95), (15, 23, 42), -1)
        cv2.addWeighted(overlay, 0.85, img, 0.15, 0, img)
        cv2.rectangle(img, (15, 15), (290, 95), (254, 242, 0), 2)

        cv2.putText(img, f"REPS: {reps}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.95, (254, 242, 0), 2, cv2.LINE_AA)
        cv2.putText(img, f"STAGE: {str(stage).upper()}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

        # Top-Right LIVE AI SENSOR Badge
        cv2.rectangle(img, (w - 180, 15), (w - 15, 50), (15, 23, 42), -1)
        cv2.rectangle(img, (w - 180, 15), (w - 15, 50), (16, 185, 129), 1)
        cv2.circle(img, (w - 165, 32), 5, (16, 185, 129), -1)
        cv2.putText(img, "AI SENSOR LIVE", (w - 150, 37), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (240, 240, 240), 1, cv2.LINE_AA)

        # Bottom-Left Form Status Overlay Card
        status_text = ""
        is_error = False

        if ex_type == "Squats":
            val = metrics.get('depth_status', 'N/A')
            status_text = f"DEPTH: {val}"
            is_error = val == "TOO HIGH"
        elif ex_type == "Push-ups":
            val = metrics.get('body_alignment', 'N/A')
            status_text = f"ALIGN: {val}"
            is_error = val in ("Poor Form", "POOR ALIGNMENT")
        elif "Biceps" in ex_type:
            val = metrics.get('swing_status', 'N/A')
            status_text = f"SWING: {val}"
            is_error = val == "SWINGING"
        elif ex_type == "Shoulder Press":
            val = metrics.get('extension_status', 'N/A')
            status_text = f"EXT: {val}"
            is_error = "Excessive" in str(metrics.get('back_arch_status', ''))
        elif ex_type == "Lunges":
            val = metrics.get('balance_status', 'N/A')
            status_text = f"BALANCE: {val}"
            is_error = val in ("OFF BALANCE", "UNBALANCED")

        if status_text:
            color = (239, 68, 68) if is_error else (16, 185, 129)
            border_color = (239, 68, 68) if is_error else (254, 242, 0)
            
            overlay_b = img.copy()
            cv2.rectangle(overlay_b, (15, h - 65), (340, h - 15), (15, 23, 42), -1)
            cv2.addWeighted(overlay_b, 0.85, img, 0.15, 0, img)
            cv2.rectangle(img, (15, h - 65), (340, h - 15), border_color, 2)
            cv2.putText(img, status_text, (30, h - 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)

    def recv(self, frame):
        if not self._mp_initialized:
            self._init_mediapipe()

        image = cv2.flip(frame.to_ndarray(format="bgr24"), 1)
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        landmarks = None
        if not self.use_tasks_api:
            if self._pose_legacy is not None:
                try:
                    results = self._pose_legacy.process(img_rgb)
                    if results and results.pose_landmarks:
                        landmarks = results.pose_landmarks.landmark
                except Exception as e:
                    pass
        else:
            if self._landmarker is not None:
                try:
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
                    self._frame_timestamps_ms += 30
                    result = self._landmarker.detect_for_video(mp_image, self._frame_timestamps_ms)
                    if result and result.pose_landmarks and len(result.pose_landmarks) > 0:
                        landmarks = result.pose_landmarks[0]
                except Exception as e:
                    pass

        if landmarks is not None:
            self._draw_skeleton(image, landmarks)
            ex_type = self.get_exercise()
            detector = self._detectors.get(ex_type)

            if detector:
                try:
                    metrics = detector.process(landmarks)
                    metrics["pose_detected"] = True
                    self._draw_overlays(image, metrics, ex_type)
                    self.set_latest_metrics(metrics)
                except Exception as e:
                    pass
        else:
            self._draw_no_pose_warnings(image)
            with self._lock:
                if self._latest_metrics is not None:
                    self._latest_metrics["pose_detected"] = False
                else:
                    self._latest_metrics = {"pose_detected": False}

        return av.VideoFrame.from_ndarray(image, format="bgr24")

ExerciseVideoProcessor = VideoProcessorClass
