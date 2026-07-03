import Webcam from "react-webcam";
import { io } from "socket.io-client";

const ScreenCapture = () => {
  const webcamRef = React.useRef(null);
  const socket = io("http://localhost:5000");

  // Capture 10 FPS
  React.useEffect(() => {
    const interval = setInterval(() => {
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc) {
        socket.emit("frame", imageSrc);
      }
    }, 100);
    return () => clearInterval(interval);
  }, []);

  return (
    <Webcam
      ref={webcamRef}
      screenshotFormat="image/jpeg"
      style={{ width: "100%", height: "auto" }}
    />
  );
};

export default ScreenCapture;
