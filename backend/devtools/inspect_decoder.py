
import safetensors.torch
from huggingface_hub import hf_hub_download
import json

REPO_ID = "nvidia/personaplex-7b-v1"
FILENAME = "model.safetensors"

print(f"Inspecting keys in {REPO_ID}/{FILENAME}...")
file_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME)

has_decoder = False
with safetensors.safe_open(file_path, framework="pt") as f:
    keys = f.keys()
    for k in keys:
        if "decoder" in k:
            has_decoder = True
            print(f"Found decoder key: {k}")
            break
    
    if not has_decoder:
        print("WARNING: No 'decoder' keys found!")

print("---")
print("Reading config.json...")
try:
    config_path = hf_hub_download(repo_id=REPO_ID, filename="config.json")
    with open(config_path, 'r') as f:
        print(json.dumps(json.load(f), indent=2))
except Exception as e:
    print(f"Failed to read config: {e}")
