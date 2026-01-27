# PersonaPlex

PersonaPlex is a real-time speech-to-speech AI interaction platform. It combines a high-performance Python backend with a modern React frontend to deliver low-latency voice conversations with AI personas.

## Architecture

*   **Frontend**: React + Vite + TypeScript. Handles audio recording, playback, and visualization.
*   **Backend**: Python (FastAPI/WebSocket). Processes audio streams, integrates with AI models (Moshi/Qwen), and manages websocket connections.

## Prerequisites

*   Node.js (v18+)
*   Python 3.10+
*   `uv` (recommended for Python package management)

## Setup

### Backend

1.  Navigate to the backend directory (or root if shared):
    ```bash
    cd backend # or root depending on structure
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the server:
    ```bash
    uvicorn backend.app.main:app --reload
    ```

### Frontend

1.  Navigate to the project root:
    ```bash
    npm install
    ```
2.  Start the development server:
    ```bash
    npm run dev
    ```

## Features

*   Real-time audio streaming
*   Voice Activity Detection (VAD)
*   Interactive Audio Visualizer
*   Low-latency websocket communication

## License

[License Name]
