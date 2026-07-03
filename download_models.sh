#!/bin/bash
MODELS=("yolov11n.pt" "yolov11s.pt" "yolo11m.pt" "yolov11n-seg.pt" "yolov11n-pose.pt")
BASE_URL="https://github.com/ultralytics/assets/releases/download/v8.3.0"

mkdir -p models
for model in "${MODELS[@]}"; do
    if [ ! -f "models/${model}" ]; then
        echo "Downloading ${model}..."
        curl -L "${BASE_URL}/${model}" -o "models/${model}"
    else
        echo "${model} exists ✓"
    fi
done
