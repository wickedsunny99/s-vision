let peer = null;
let screenStream = null;
const currentResolution = 1080; // Fixed to 1080p

// Initialize PeerJS with your server
function initializePeer() {
  if (peer && !peer.disconnected) {
    peer.destroy(); // Clean up existing connection
  }

  peer = new Peer({
    host: window.location.hostname, // Use current host
    port: 9000,
    path: "/myapp",
    secure: false,
    debug: 3,
  });

  // Improved error handling
  peer.on("error", (err) => {
    console.error("PeerJS error:", err);
    if (err.type === "network") {
      setTimeout(initializePeer, 2000); // Reconnect after 2 seconds
    }
  });

  peer.on("open", (id) => {
    console.log("My peer ID is:", id);
  });

  peer.on("disconnected", () => {
    console.log("Connection lost. Reconnecting...");
    peer.reconnect();
  });
}

// Capture screen with fixed 1080p resolution
async function startCapture() {
  try {
    screenStream = await navigator.mediaDevices.getDisplayMedia({
      video: {
        frameRate: 10,
        width: { ideal: currentResolution },
      },
    });

    const videoElement = document.getElementById("screen");
    if (videoElement) {
      videoElement.srcObject = screenStream;
    }

    // Send stream to PeerJS server
    if (peer && peer.open) {
      const call = peer.call("backend-peer", screenStream);
      if (call) {
        call.on("stream", (remoteStream) => {
          console.log("Streaming to backend at 1080p");
        });
        call.on("error", (err) => console.error("Call error:", err));
      }
    }
  } catch (error) {
    console.error("Screen capture failed:", error);
  }
}

// Initialize on page load
window.onload = () => {
  initializePeer();
  setTimeout(startCapture, 1000); // Wait for peer initialization
};

// Cleanup
window.onbeforeunload = () => {
  if (screenStream) {
    screenStream.getTracks().forEach((track) => track.stop());
  }
  if (peer) {
    peer.destroy();
  }
};

// Additional event listeners for better debugging
window.addEventListener("online", () => {
  console.log("Network connection restored");
  if (peer && peer.disconnected) {
    peer.reconnect();
  }
});

window.addEventListener("offline", () => {
  console.log("Network connection lost");
});
