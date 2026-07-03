export default function DetectionOverlay({ detections }) {
  return (
    <div className="detection-overlay">
      {detections.map((obj, i) => (
        <div
          key={i}
          className="detection-box"
          style={{
            left: obj.bbox[0],
            top: obj.bbox[1],
            width: obj.bbox[2] - obj.bbox[0],
            height: obj.bbox[3] - obj.bbox[1],
          }}
        >
          {obj.label}
        </div>
      ))}
    </div>
  );
}
