
import json
import logging
from typing import Literal

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ValidationError

from backend.app.services.engine import engine

logger = logging.getLogger("PersonaPlex-Router")
router = APIRouter()

# --- VALIDATION MODELS ---
class ConfigPayload(BaseModel):
    type: Literal["config"]
    persona: str
    voice: str

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main Duplex Loop.
    Maintains the connection - reading user audio, writing AI audio.
    """
    await websocket.accept()
    logger.info("Client Connected via WebSocket")
    
    try:
        while True:
            # 1. AWAIT INPUT
            message = await websocket.receive()
            
            # 2. HANDLE CONFIGURATION
            if "text" in message:
                try:
                    data = json.loads(message["text"])
                    # Pydantic Validation
                    if data.get("type") == "config":
                        config = ConfigPayload(**data)
                        engine.configure(config.persona, config.voice)
                except json.JSONDecodeError:
                    logger.error("Failed to parse config JSON")
                except ValidationError as e:
                    logger.error(f"Invalid Config: {e}")

            # 3. HANDLE AUDIO STREAM (HOT PATH)
            elif "bytes" in message:
                user_audio_chunk = message["bytes"]
                
                # --- INFERENCE STEP ---
                ai_audio_chunk = engine.process_audio_frame(user_audio_chunk)
                
                # --- RESPONSE STEP ---
                await websocket.send_bytes(ai_audio_chunk)

    except WebSocketDisconnect:
        logger.info("Client Disconnected")
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
