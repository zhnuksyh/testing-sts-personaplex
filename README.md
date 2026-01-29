# PersonaPlex

**PersonaPlex** is a real-time, full-duplex Speech-to-Speech conversational AI platform powered by NVIDIA's PersonaPlex-7B model.

> **Credits**: PersonaPlex-7B is developed by **NVIDIA** based on the Moshi architecture by **Kyutai**.

## Features

✅ **Ultra-Low Latency** (~170ms response time)  
✅ **Native Turn-Taking** - Model handles interruptions naturally  
✅ **18 Voice Options** - Natural and Expressive voices for M/F  
✅ **Dynamic Personas** - Text-based role prompts following NVIDIA's format  
✅ **Voice Previews** - Pre-generated samples for each voice  

## Core Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Frontend   │◄──►│   Backend    │◄──►│ PersonaPlex  │
│  (React/TS)  │WSS │  (FastAPI)   │    │   -7B Model  │
└──────────────┘    └──────────────┘    └──────────────┘
```

### The Neural Audio Codec: **Mimi**
- Compresses 24kHz audio into discrete tokens at 12.5 Hz
- 8 parallel codebooks for high-fidelity reconstruction

### The Language Model: **PersonaPlex-7B**
- Full-duplex conversational model (listens while speaking)
- Trained on synthetic conversations + Fisher corpus
- Supports voice prompts (timbre) and text prompts (persona)

## Quick Start

### Prerequisites
- **NVIDIA GPU** with 16GB+ VRAM
- **Python 3.10+**
- **Node.js v18+**
- **HuggingFace Token** with PersonaPlex access

### 1. Backend Setup

```bash
# Set your HuggingFace token
export HF_TOKEN=<YOUR_TOKEN>

# Install dependencies
pip install -r requirements.txt

# Run the server (handles SSL)
./scripts/run_host_https.sh
```

### 2. Frontend Setup

```bash
npm install
npm run dev
```

Access at `https://YOUR_IP:5173` (accept self-signed certificate).

## Usage

### Voice Selection
Choose from 18 NVIDIA voices:
- **Natural (Female)**: NATF0, NATF1, NATF2, NATF3
- **Natural (Male)**: NATM0, NATM1, NATM2, NATM3
- **Variety (Female)**: VARF0, VARF1, VARF2, VARF3, VARF4
- **Variety (Male)**: VARM0, VARM1, VARM2, VARM3, VARM4

### Persona Prompts (NVIDIA Format)
```
# Assistant Role
You are a wise and friendly teacher. Answer questions in a clear and engaging way.

# Customer Service
You work for [Company] which is a [type] and your name is [Name]. Information: [details]

# Casual
You enjoy having a good conversation.
```

## Project Structure

```
root/
├── backend/
│   ├── app/
│   │   ├── routers/     # WebSocket, Admin API
│   │   └── services/    # PersonaPlex Engine
│   └── devtools/
├── certs/               # SSL certificates
├── scripts/             # Run scripts
├── public/
│   └── voice-samples/   # Voice preview audio
├── src/                 # React frontend
└── docs/
```

## Admin API

Generate voice samples:
```bash
curl -X POST https://localhost:8000/api/admin/generate-voice-samples -k
```

## License

Code: MIT License  
Model Weights: NVIDIA Open Model License

## References

- [NVIDIA PersonaPlex Paper](https://research.nvidia.com/labs/adlr/files/personaplex/personaplex_preprint.pdf)
- [PersonaPlex-7B on HuggingFace](https://huggingface.co/nvidia/personaplex-7b-v1)
- [NVIDIA PersonaPlex GitHub](https://github.com/NVIDIA/personaplex)
