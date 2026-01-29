
import os

# --- AUDIO CONSTANTS ---
SAMPLE_RATE = 24000
CHUNK_SIZE = 1920  # Audio chunk size in frames (Must be multiple of 1920 for Mimi)

# --- MODEL SETTINGS ---
MODEL_TYPE = "nvidia/personaplex-7b-v1"
DEVICE = os.getenv("DEVICE", "cuda")  # or "cpu"

# --- HUGGINGFACE SETTINGS ---
HF_TOKEN = os.getenv("HF_TOKEN", None)  # Required for PersonaPlex model access

