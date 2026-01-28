
import safetensors.torch
from huggingface_hub import hf_hub_download

REPO_ID = "nvidia/personaplex-7b-v1"
FILENAME = "model.safetensors"

file_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME)

print("Keys under 'transformer':")
with safetensors.safe_open(file_path, framework="pt") as f:
    count = 0
    for k in f.keys():
        if k.startswith("transformer."):
            print(k)
            count += 1
            if count > 20:
                break
