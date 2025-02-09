import os
import sys
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Add this if you need to resolve import paths
sys.path.append(str(Path(__file__).parent.parent))

# Add this at the top
PEER_SERVER_PORT = 9000  # Match your peer-server.js port


# Add CSP middleware
@app.middleware("http")
async def add_csp_header(request: Request, call_next):
    response = await call_next(request)
    csp_policy = (
        "script-src 'self' https://unpkg.com; "
        f"connect-src 'self' ws://localhost:{PEER_SERVER_PORT} http://localhost:{PEER_SERVER_PORT};"
    )
    response.headers["Content-Security-Policy"] = csp_policy
    return response


# Serve frontend files
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


# WebSocket endpoint for future analytics
@app.websocket("/analytics")
async def analytics_endpoint(websocket: WebSocket):
    await websocket.accept()
    print(f"Peer server running on port {PEER_SERVER_PORT}")


@app.get("/")
async def root():
    return {"message": "Hello World"}
