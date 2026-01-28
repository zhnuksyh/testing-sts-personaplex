
import safetensors.torch
from huggingface_hub import hf_hub_download

REPO_ID = "nvidia/personaplex-7b-v1"
FILENAME = "model.safetensors"

print(f"Inspecting {REPO_ID}/{FILENAME}...")
file_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME)

with safetensors.safe_open(file_path, framework="pt") as f:
    keys = f.keys()
    print(f"Total keys: {len(keys)}")
    print("First 20 keys:")
    for k in list(keys)[:20]:
        print(k)
