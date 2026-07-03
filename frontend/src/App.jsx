import { useState, useEffect, useCallback, useMemo } from "react";
import io from "socket.io-client";
import { VoiceInterface } from "./voice";
import ScreenCapture from "./ScreenCapture";
import DetectionOverlay from "./DetectionOverlay";

export default function App() {
  const [response, setResponse] = useState("");
  const [detections, setDetections] = useState([]);
  const [extractedText, setExtractedText] = useState("");
  const [error, setError] = useState(null);

  // Initialize socket connection
  const socket = useMemo(() => io("http://localhost:5000"), []);

  const handleAnalysis = useCallback((data) => {
    setDetections(data.objects);
    setExtractedText(data.text.join(", "));
    if (data.changes.length > 0) {
      setResponse(`System changes detected: ${data.changes.join(", ")}`);
    }
  }, []);

  useEffect(() => {
    const voice = new VoiceInterface(socket);
    voice.start();

    socket.on("analysis", handleAnalysis);

    socket.on("voice-response", (data) => {
      const synth = window.speechSynthesis;
      const utterance = new SpeechSynthesisUtterance(data.response);
      synth.speak(utterance);
      setResponse(data.response);
    });

    socket.on("error", (err) => {
      setError(err.message);
      setTimeout(() => setError(null), 5000);
    });

    return () => {
      voice.stop();
      socket.off("analysis");
      socket.off("voice-response");
      socket.off("error");
      socket.disconnect();
    };
  }, [socket, handleAnalysis]);

  return (
    <div className="app-container">
      <ScreenCapture socket={socket} />

      <DetectionOverlay detections={detections} />

      <div className="info-panel">
        {error && <div className="error-banner">{error}</div>}
        <div className="text-display">
          <h3>Extracted Text:</h3>
          <p>{extractedText}</p>
        </div>
        <div className="voice-response">
          <h3>System Response:</h3>
          <p>{response}</p>
        </div>
      </div>
    </div>
  );
}
