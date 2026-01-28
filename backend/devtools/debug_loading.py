
import logging
import torch
import safetensors.torch
import moshi
from huggingface_hub import hf_hub_download
import moshi.models.loaders
from moshi.models.lm import LMModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEVICE = "cuda"
MODEL_TYPE = "nvidia/personaplex-7b-v1"

print(f"Loading on {DEVICE}...")

# 1. Download/Load Mimi
print("Downloading/Loading Mimi Codec from kyutai/mimi...")
mimi_weight = hf_hub_download(repo_id="kyutai/mimi", filename="model.safetensors")
mimi = moshi.models.loaders.get_mimi(mimi_weight, device=DEVICE)
print("Mimi loaded.")

# 2. Download/Load PersonaPlex
print(f"Downloading PersonaPlex: {MODEL_TYPE}...")
lm_weight = hf_hub_download(repo_id=MODEL_TYPE, filename="model.safetensors")

print("Initializing Moshi LM architecture...")
config = moshi.models.loaders._lm_kwargs
lm = LMModel(**config)
lm.to(DEVICE)

print("Loading state dict and remapping keys...")
sd = safetensors.torch.load_file(lm_weight)
new_sd = {}

for k, v in sd.items():
    if k.startswith("transformer."):
        k = k.replace("transformer.", "decoder_transformer.")
    
    if "in_proj_weight" in k:
        q, k_key, val = v.chunk(3, dim=0)
        new_sd[k.replace("in_proj_weight", "q_proj.weight")] = q
        new_sd[k.replace("in_proj_weight", "k_proj.weight")] = k_key
        new_sd[k.replace("in_proj_weight", "v_proj.weight")] = val
        continue
    
    if "in_proj_bias" in k:
        q, k_key, val = v.chunk(3, dim=0)
        new_sd[k.replace("in_proj_bias", "q_proj.bias")] = q
        new_sd[k.replace("in_proj_bias", "k_proj.bias")] = k_key
        new_sd[k.replace("in_proj_bias", "v_proj.bias")] = val
        continue
        
    new_sd[k] = v

print("Load state dict...")
lm.load_state_dict(new_sd, strict=False)
print("SUCCESS: PersonaPlex LM loaded!")
