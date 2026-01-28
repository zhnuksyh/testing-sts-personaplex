
import os

# --- AUDIO CONSTANTS ---
SAMPLE_RATE = 24000
CHUNK_SIZE = 1920  # Audio chunk size in frames (Must be multiple of 1920 for Mimi)

# --- MODEL SETTINGS ---
# In a real app, these might come from os.getenv()
MODEL_TYPE = "nvidia/personaplex-7b-v1"
DEVICE = "cuda"  # or "cpu"
