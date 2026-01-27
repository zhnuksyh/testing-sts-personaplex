
import os

# --- AUDIO CONSTANTS ---
SAMPLE_RATE = 24000
CHUNK_SIZE = 512  # Audio chunk size in frames

# --- MODEL SETTINGS ---
# In a real app, these might come from os.getenv()
MODEL_TYPE = "PersonaPlex-7B"
DEVICE = "cuda"  # or "cpu"
