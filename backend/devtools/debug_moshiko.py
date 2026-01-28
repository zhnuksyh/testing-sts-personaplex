
import logging
import torch
import moshi.models.loaders

logging.basicConfig(level=logging.INFO)

DEVICE = "cuda"
MODEL_TYPE = "kyutai/moshiko-pytorch-bf16"

print(f"Testing loading of {MODEL_TYPE}...")

# 1. Download/Load Mimi
from huggingface_hub import hf_hub_download
print("Downloading/Loading Mimi Codec from kyutai/moshiko-pytorch-bf16...")
# Grab the tokenizer file which is the Mimi checkpoint
mimi_weight = hf_hub_download(repo_id=MODEL_TYPE, filename="tokenizer-e351c8d8-checkpoint125.safetensors")
mimi = moshi.models.loaders.get_mimi(mimi_weight, device=DEVICE)
print("Mimi loaded.")

# 2. Load Moshiko (Auto-download likely handled by loader if we pass repo_id/filename correctly)
# get_moshi_lm needs a filename usually.
print(f"Downloading Moshiko: {MODEL_TYPE}...")
lm_weight = hf_hub_download(repo_id=MODEL_TYPE, filename="model.safetensors")
lm = moshi.models.loaders.get_moshi_lm(lm_weight, device=DEVICE)
print("Moshiko LM loaded.")

model = moshi.models.LMGen(lm, mimi=mimi)
print("SUCCESS: Moshiko Loaded!")
