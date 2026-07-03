# s-vision

Real-time screen/vision analysis. A React client streams video frames to a
Python backend that runs **object detection** (YOLO11), **OCR** (Tesseract),
and **context tracking** (Redis), then streams the results back over
WebSockets. It also accepts **voice commands** via the browser's Speech
Recognition API and replies with speech synthesis.

## Architecture

```
┌────────────────────────┐        Socket.IO (ws)        ┌────────────────────────────┐
│  Frontend (React)      │ ───────────────────────────► │  Backend (Flask-SocketIO)  │
│                        │  "frame"  (base64 JPEG)      │                            │
│  • ScreenCapture       │  "voice-command" (text)      │  • ScreenAnalyzer (YOLO11) │
│  • DetectionOverlay    │                              │  • TextProcessor (Tesseract)│
│  • VoiceInterface      │ ◄─────────────────────────── │  • ContextManager (Redis)  │
│                        │  "analysis" / "voice-response"│                           │
└────────────────────────┘                              └────────────────────────────┘
```

**Data flow**

1. The browser captures frames and emits them as base64 JPEG on the `frame` event.
2. The backend decodes each frame and runs, per frame:
   - **Object detection** — `ScreenAnalyzer.analyze_frame` returns `{label, bbox}` boxes.
   - **OCR** — `TextProcessor.extract_text` pulls text out of the frame.
   - **Context diff** — `ContextManager` compares the new text against the
     previous frame (stored per-user in Redis) and reports what changed.
3. Results are emitted back on the `analysis` event and drawn as overlays.
4. Spoken commands go up on `voice-command`; the reply comes back on
   `voice-response` and is read aloud by the browser.

## Tech stack

| Layer     | Technologies |
|-----------|--------------|
| Frontend  | React 18 (Create React App), `socket.io-client`, `react-webcam`, MUI |
| Backend   | Flask + Flask-SocketIO (gevent), Ultralytics YOLO11, OpenCV, PyTorch |
| OCR       | Tesseract via `pytesseract` |
| State     | Redis (per-user context) |
| Voice     | Web Speech API (recognition + synthesis, browser-side) |

## Prerequisites

- **Python 3.12**
- **Node.js 18+**
- **Redis** running locally on `localhost:6379`
- **Tesseract OCR** installed. The backend expects the binary at
  `/usr/bin/tesseract` (see `backend/ai/text_processing.py`); adjust that path
  for macOS/Homebrew (`/opt/homebrew/bin/tesseract`) if needed.

Install the system dependencies (macOS example):

```bash
brew install redis tesseract
brew services start redis
```

## Setup

### 1. Models

The backend will not start without `models/yolo11m.pt`. Download the YOLO11
weights:

```bash
./download_models.sh
```

This fetches the detection, segmentation, and pose models into `models/`.

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python server.py                  # serves Socket.IO on http://localhost:5000
```

### 3. Frontend

```bash
cd frontend
npm install
npm start                         # opens http://localhost:3000
```

The client connects to the backend at `http://localhost:5000`.

## Project structure

```
s-vision/
├── backend/
│   ├── server.py               # Flask-SocketIO entrypoint (port 5000)
│   ├── vision_processor.py     # FastAPI router (experimental HTTP endpoint)
│   ├── ai/
│   │   ├── object_detection.py # ScreenAnalyzer — YOLO11 detection/seg/pose
│   │   └── text_processing.py  # TextProcessor — Tesseract OCR
│   ├── context/
│   │   └── context_manager.py  # ContextManager — Redis-backed per-user state
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.jsx             # wires socket, overlays, and voice together
│       ├── ScreenCapture.jsx   # captures + emits frames
│       ├── DetectionOverlay.jsx# draws detection boxes
│       └── voice.js            # Web Speech API interface
├── models/                     # YOLO11 weights (via download_models.sh)
└── download_models.sh
```

## Socket.IO events

| Event            | Direction        | Payload |
|------------------|------------------|---------|
| `frame`          | client → server  | base64 JPEG data URL |
| `voice-command`  | client → server  | transcript string |
| `analysis`       | server → client  | `{ objects, text, changes }` |
| `voice-response` | server → client  | `{ response }` |
| `error`          | server → client  | `{ message }` |

## Notes & known limitations

- This is a prototype. `vision_processor.py` exposes an experimental FastAPI
  endpoint that is not yet wired into `server.py`.
- Model weights and the Redis dump (`dump.rdb`) are currently tracked in the
  repo; consider moving weights to Git LFS or fetching them at setup time via
  `download_models.sh` instead.
- Voice recognition/synthesis rely on the Web Speech API and work best in
  Chromium-based browsers.
