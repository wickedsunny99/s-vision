const { PeerServer } = require("peer");

const peerServer = PeerServer({
  port: 9000,
  path: "/myapp",
  allow_discovery: true, // Add this line
  corsOptions: {
    origin: ["http://localhost:8000", "http://127.0.0.1:8000"],
    methods: ["GET", "POST"],
  },
});

peerServer.on("connection", (client) => {
  console.log("Peer connected:", client.id);
});

console.log("PeerJS server running on port 9000");
