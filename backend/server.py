import base64
from pathlib import Path

from ai.object_detection import ScreenAnalyzer
from ai.text_processing import TextProcessor
from flask import Flask, request
from flask_socketio import SocketIO

from context.context_manager import ContextManager

app = Flask(__name__)
socketio = SocketIO(app, async_mode="gevent", cors_allowed_origins="*")

# Initialize components
model_path = Path(__file__).parent.parent / "models/yolo11m.pt"
if not model_path.exists():
    raise FileNotFoundError(
        f"Medium detection model missing. Download with:\ncurl -L https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov11m.pt -o {model_path}\nOr rename existing model file to 'yolo11m.pt'"
    )

analyzer = ScreenAnalyzer(model_size="m", model_type="detect")
text_processor = TextProcessor()
context_manager = ContextManager()

# Or for pose estimation with nano model
# pose_analyzer = ScreenAnalyzer(model_size="n", model_type="pose")


@socketio.on("connect")
def handle_connect():
    user_id = request.sid
    context_manager.initialize_user(user_id)


@socketio.on("frame")
def handle_frame(data):
    user_id = request.sid
    try:
        frame_data = data.split(",")[1]
        decoded = base64.b64decode(frame_data)

        # Parallel processing
        detections = analyzer.analyze_frame(decoded)
        text = text_processor.extract_text(decoded)
        changes = context_manager.get_changes(user_id, text)

        # Update context
        context_manager.update_context(user_id, decoded, text)

        socketio.emit(
            "analysis", {"objects": detections, "text": text, "changes": changes}
        )

    except Exception as e:
        socketio.emit("error", {"message": str(e)})


@socketio.on("voice-command")
def handle_voice(command):
    try:
        user_id = request.sid
        response = text_processor.process_command(user_id, command)
        context_manager.update_from_voice(user_id, command)
        socketio.emit("voice-response", {"response": response})
    except Exception as e:
        socketio.emit("error", {"message": str(e)})


if __name__ == "__main__":
    socketio.run(app, port=5000, allow_unsafe_werkzeug=True)
