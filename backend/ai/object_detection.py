import logging
from pathlib import Path

import cv2
import numpy as np
import torch
from torch import quantization
from ultralytics import YOLO


class ScreenAnalyzer:
    def __init__(self, model_size="n", model_type="detect"):
        self.logger = logging.getLogger(__name__)
        self.model = self._load_model(model_size, model_type)

    def _load_model(self, model_size: str, model_type: str):
        valid_sizes = ["n", "s", "m", "l", "x"]
        valid_types = ["detect", "segment", "pose"]

        if model_size not in valid_sizes:
            raise ValueError(f"Invalid size: {model_size}. Choose from {valid_sizes}")
        if model_type not in valid_types:
            raise ValueError(f"Invalid type: {model_type}. Choose from {valid_types}")

        model_name = (
            f"yolo{model_size}11m.pt"
            if model_type == "detect"
            else f"yolov{model_size}-pose.pt"
        )
        model_path = Path(__file__).parent.parent / "models" / model_name

        if not model_path.exists():
            self.logger.error(f"Missing {model_type} model! Download with:")
            self.logger.error(
                f"curl -L https://github.com/ultralytics/assets/releases/download/v8.3.0/{model_name} -o {model_path}"
            )
            raise FileNotFoundError(f"Model file missing: {model_path}")

        return YOLO(model_path, model="yolov8m.yaml")

    def analyze_frame(self, frame):
        """Process frame with optimized model"""
        with torch.no_grad():
            # Convert base64 to image
            img = cv2.imdecode(np.frombuffer(frame, np.uint8), cv2.IMREAD_COLOR)

            # Object detection
            results = self.model(img)
            detections = []

            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    label = result.names[int(box.cls[0])]
                    detections.append({"label": label, "bbox": [x1, y1, x2, y2]})

            return detections

    def _load_segmentation_model(self):
        """Load segmentation model"""
        try:
            model_path = (
                Path(__file__).resolve().parent.parent.parent
                / "models"
                / "yolov11n-seg.pt"
            )
            model = YOLO(str(model_path), task="segment")
            self.logger.info("Successfully loaded segmentation model")
            return model
        except Exception as e:
            self.logger.error(f"Model loading failed: {str(e)}")
            raise RuntimeError("Could not initialize segmentation model") from e

    def _load_pose_estimation_model(self):
        """Load pose estimation model"""
        try:
            model_path = (
                Path(__file__).resolve().parent.parent.parent
                / "models"
                / "yolov11n-pose.pt"
            )
            model = YOLO(str(model_path), task="pose")
            self.logger.info("Successfully loaded pose estimation model")
            return model
        except Exception as e:
            self.logger.error(f"Model loading failed: {str(e)}")
            raise RuntimeError("Could not initialize pose estimation model") from e
