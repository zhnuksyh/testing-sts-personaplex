#!/bin/bash
# Need to run from project root context
cd "$(dirname "$0")/.."

# HuggingFace token for PersonaPlex model access
# Set your token: export HF_TOKEN=your_token_here
if [ -z "$HF_TOKEN" ]; then
    echo "⚠️  Warning: HF_TOKEN not set. PersonaPlex model download may fail."
    echo "   Set it with: export HF_TOKEN=your_huggingface_token"
fi

CUDA_LAUNCH_BLOCKING=1 HF_TOKEN=$HF_TOKEN uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000 --ssl-keyfile certs/key.pem --ssl-certfile certs/cert.pem
