
import safetensors.torch
from huggingface_hub import hf_hub_download

print(f"Inspecting kyutai/mimi/model.safetensors...")
file_path = hf_hub_download(repo_id="kyutai/mimi", filename="model.safetensors")

with safetensors.safe_open(file_path, framework="pt") as f:
    keys = list(f.keys())
    print(f"Total keys: {len(keys)}")
    print("First 20 keys:")
    for k in keys[:20]:
        print(k)
