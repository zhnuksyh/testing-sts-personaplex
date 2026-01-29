# Hardware Compatibility Guide

This guide explains how to run PersonaPlex on different hardware configurations.

## Recommended Hardware

| Component | Recommended | Minimum |
|-----------|-------------|---------|
| **GPU** | NVIDIA RTX 3090/4090 (24GB VRAM) | NVIDIA GPU with 16GB+ VRAM |
| **RAM** | 32GB | 16GB |
| **CPU** | Modern multi-core | Any x86_64 |

## Running on Different Hardware

### NVIDIA GPU (Full Performance)
Standard setup - real-time inference (~170ms latency):
```bash
./scripts/run_host_https.sh
```

### CPU-Only Mode (No GPU)
For laptops or servers without NVIDIA GPU. **Very slow** (~10-30s per response).

```bash
# Install accelerate package
pip install accelerate

# Run with CPU offload
SSL_DIR=$(mktemp -d)
python -m moshi.server --ssl "$SSL_DIR" --cpu-offload
```

**Requirements for CPU mode:**
- 20GB+ RAM (or use swap)
- Modern multi-core CPU
- Patience (not real-time!)

### AMD GPU (ROCm)
Experimental - may work with ROCm-enabled PyTorch:
```bash
pip install torch --index-url https://download.pytorch.org/whl/rocm6.0
```
Note: Not officially tested.

### Apple Silicon (M1/M2/M3)
May work with MPS backend:
```python
# In config.py, change:
DEVICE = os.getenv("DEVICE", "mps")
```
Note: Not officially tested or supported.

## Alternative: Remote Backend

If your laptop lacks a GPU, run only the frontend locally:

1. **On GPU server:**
   ```bash
   ./scripts/run_host_https.sh
   ```

2. **On laptop:**
   ```bash
   npm run dev
   ```
   Then point the frontend to the GPU server's IP address.

## Alternative: Cloud GPU

Use cloud GPU services for inference:
- **RunPod**: ~$0.50/hr for RTX 4090
- **Lambda Labs**: ~$0.50/hr for A10
- **AWS/GCP**: p3/a2 instances

## Memory Requirements

| Model | GPU VRAM | RAM (CPU mode) |
|-------|----------|----------------|
| PersonaPlex-7B | 16-20GB | 20-32GB |

## Troubleshooting

### Out of Memory (OOM)
```bash
# Try CPU offload
python -m moshi.server --ssl "$SSL_DIR" --cpu-offload
```

### CUDA Not Found
```bash
# Verify CUDA installation
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

### Slow Response on CPU
This is expected. CPU inference is 10-50x slower than GPU. 
Consider using a remote GPU backend or cloud GPU service.
