#!/bin/bash
CUDA_LAUNCH_BLOCKING=1 uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000 --ssl-keyfile key.pem --ssl-certfile cert.pem
