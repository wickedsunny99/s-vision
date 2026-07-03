import React, { useCallback } from "react";
import Webcam from "react-webcam";

export default function ScreenCapture({ socket }) {
  const captureFrame = useCallback(
    async (frameData) => {
      try {
        const resized = await resizeFrame(frameData, 1280, 720);
        socket.emit("frame", resized);
      } catch (err) {
        console.error("Frame processing error:", err);
      }
    },
    [socket]
  );

  return <Webcam screenshotFormat="image/jpeg" onUserMedia={captureFrame} />;
}
