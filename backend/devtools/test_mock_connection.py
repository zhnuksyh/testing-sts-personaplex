import asyncio
import websockets
import json
import numpy as np

async def test_connection():
    uri = "ws://localhost:8000/ws"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            # 1. Send Config
            config = {
                "type": "config",
                "persona": "Test Persona",
                "voice": "test_voice"
            }
            await websocket.send(json.dumps(config))
            print("Sent Config.")
            
            # 2. Send Mock Audio
            # Generate 1024 bytes of dummy audio
            dummy_audio = np.random.bytes(1024)
            await websocket.send(dummy_audio)
            print("Sent Audio Chunk.")
            
            # 3. Receive Response
            response = await websocket.recv()
            print(f"Received {len(response)} bytes of response.")
            
            if len(response) > 0:
                print("SUCCESS: Server responded with audio data.")
            else:
                print("FAILURE: Server sent empty response.")
                
    except Exception as e:
        print(f"ERROR: Could not connect or communicate: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
