from pathlib import Path

ESSENTIAL_MODELS = [
    "yolo11m.pt",  # Nano detection
    "yolo11n-seg.pt",  # Nano segmentation
    "yolo11n-pose.pt",  # Nano pose
]


def verify_models():
    missing = [m for m in ESSENTIAL_MODELS if not (Path("models") / m).exists()]

    if missing:
        print("Missing essential models:")
        for model in missing:
            print(f"  - {model}")
        print("\nDownload with:")
        print(
            "curl -L https://github.com/ultralytics/assets/releases/download/v8.3.0/MODEL_NAME -o models/MODEL_NAME"
        )
        print("Or run: ./download_models.sh")
        exit(1)


if __name__ == "__main__":
    verify_models()
