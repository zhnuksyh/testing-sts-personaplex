# PersonaPlex

**PersonaPlex** is a cutting-edge Real-Time Speech-to-Speech (STS) AI platform. It enables ultra-low-latency, full-duplex voice conversations with AI personas, powered by advanced neural audio codecs and language models.

> **Credits**: PersonaPlex is a product concept by **NVIDIA**. This implementation utilizes state-of-the-art open-source research from **Kyutai** (Moshi/Mimi).

## Project Status: Core Foundation
**Current Phase: Alpha (Stability Verified)**

This project currently represents a **stable, functional foundation** for high-fidelity neural audio streaming. While the core "ear-to-brain-to-mouth" pipeline is fully operational and crash-resistant, it does not yet feature higher-level conversational logic.

**Known Limitations (To Be Implemented):**
*   **No Turn-Taking Logic**: The model does not yet know when to stop talking if interrupted.
*   **No Voice Activity Detection (VAD)**: The system processes silence as input, occasionally leading to "hallucinated" apologies or responses.
*   **Fixed Persona**: Currently locked to a single base instruction set.

## Core Architecture

The system is built on a sophisticated neural pipeline designed for continuous audio streaming:

### 1. The Neural Audio Codec: **Mimi**
*   **Role**: The "Ear" and "Mouth".
*   **Function**: Compresses raw 24kHz audio into discrete token codes (quantization) and reconstructs them back to high-fidelity audio.
*   **Spec**: Operates at 12.5 Hz frame rate, compressing audio into 8 parallel codebooks (channels).

### 2. The Language Model: **Moshiko**
*   **Role**: The "Brain".
*   **Function**: A Transformer-based Large Language Model (LLM) trained on mixed-modality data (Text + Audio).
*   **Mechanism**: It receives acoustic tokens from Mimi and predicts the next acoustic tokens autoregressively, enabling it to "speak" directly without text-to-speech intermediate steps.

### 3. The Backend Engine (Python)
*   **Technology**: FastAPI, PyTorch, WebSockets.
*   **Pipeline**:
    *   Receives `Float32` audio from the client.
    *   **Safety Layer**: Clamps inputs/outputs to the model's vocabulary limits (0-2047) to prevent GPU crashes.
    *   **Channel Slicing**: Strictly separates semantic text tokens (Channel 0) from acoustic audio tokens (Channels 1-8).
    *   **Session Management**: Handles connection lifecycles and context resets.

### 4. The Frontend Client (React)
*   **Technology**: Vite, TypeScript, Web Audio API (AudioWorklet).
*   **Function**:
    *   Captures microphone input in real-time.
    *   Streams raw `Float32` PCM data to the backend via secure WebSockets (WSS).
    *   Buffers and plays back the returned neural audio with minimal jitter.

## Integration Journey

This project overcame significant technical challenges to achieve stability, including:
*   Resolving "Device-Side Assert" GPU crashes via token clamping.
*   Fixing "White Noise" issues through strict Float32 data typing.
*   Eliminating semantic noise by correctly isolating audio channels from text channels.
*   *See [docs/INTEGRATION_JOURNEY.md](docs/INTEGRATION_JOURNEY.md) for the full engineering report.*

## Quick Start

### Prerequisites
*   **NVIDIA GPU** (Required for real-time inference).
*   **Python 3.10+** (Managed preferably via `uv` or `conda`).
*   **Node.js v18+**.

### 1. Backend Setup
The backend requires SSL certificates for secure WebSocket (WSS) connections.

```bash
# 1. Install Dependencies
pip install -r requirements.txt

# 2. Run the Host Script (Handles SSL & Server Start)
./scripts/run_host_https.sh
```
*The server will start on https://0.0.0.0:8000*

### 2. Frontend Setup
```bash
# 1. Install Dependencies
npm install

# 2. Start the Client
npm run dev
```
*Access the UI at https://YOUR_LOCAL_IP:5173* (Accept the self-signed certificate warning).

## Project Structure

```
root/
├── backend/
│   ├── app/           # Core Application Logic (Engine, Router)
│   └── devtools/      # Debugging & Inspection Scripts
├── certs/             # SSL Certificates (cert.pem, key.pem)
├── scripts/           # Execution Scripts (run_host_https.sh)
├── src/               # React Frontend Source
└── docs/              # Documentation
```
