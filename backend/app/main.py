
import logging
import uvicorn
from fastapi import FastAPI
from backend.app.routers import websocket

# Configure Logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="PersonaPlex Edge Node")

# Include Routers
app.include_router(websocket.router)

if __name__ == "__main__":
    # HOSTING NOTE:
    # 0.0.0.0 allows external access
    uvicorn.run(app, host="0.0.0.0", port=8000)
