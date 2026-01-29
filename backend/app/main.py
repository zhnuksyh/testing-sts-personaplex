
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import websocket, admin

# Configure Logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="PersonaPlex Edge Node")

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(websocket.router)
app.include_router(admin.router)

if __name__ == "__main__":
    # HOSTING NOTE:
    # 0.0.0.0 allows external access
    uvicorn.run(app, host="0.0.0.0", port=8000)

