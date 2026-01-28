#!/bin/bash
# Need to run from project root context
cd "$(dirname "$0")/.."
CUDA_LAUNCH_BLOCKING=1 uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000 --ssl-keyfile certs/key.pem --ssl-certfile certs/cert.pem
