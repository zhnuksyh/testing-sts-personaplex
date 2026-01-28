
import safetensors.torch
from huggingface_hub import hf_hub_download

REPO_ID = "nvidia/personaplex-7b-v1"
FILENAME = "model.safetensors"

file_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME)

with safetensors.safe_open(file_path, framework="pt") as f:
    if "transformer.layers.0.self_attn.q_proj.weight" in f.keys():
        tensor = f.get_tensor("transformer.layers.0.self_attn.q_proj.weight")
        print(f"Shape: {tensor.shape}")
    else:
        print("Key not found!")
