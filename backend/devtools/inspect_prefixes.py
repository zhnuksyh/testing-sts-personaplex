
import safetensors.torch
from huggingface_hub import hf_hub_download

REPO_ID = "nvidia/personaplex-7b-v1"
FILENAME = "model.safetensors"

file_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME)

prefixes = set()
with safetensors.safe_open(file_path, framework="pt") as f:
    for k in f.keys():
        prefix = k.split('.')[0]
        prefixes.add(prefix)

print("Top-level prefixes found:")
for p in prefixes:
    print(p)
