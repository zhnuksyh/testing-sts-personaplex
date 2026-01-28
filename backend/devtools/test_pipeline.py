
import logging
import torch
import moshi.models.loaders
from huggingface_hub import hf_hub_download

logging.basicConfig(level=logging.INFO)
DEVICE = "cuda"
MODEL_TYPE = "kyutai/moshiko-pytorch-bf16"

print("Loading models...")
mimi_weight = hf_hub_download(repo_id=MODEL_TYPE, filename="tokenizer-e351c8d8-checkpoint125.safetensors")
mimi = moshi.models.loaders.get_mimi(mimi_weight, device=DEVICE)

lm_weight = hf_hub_download(repo_id=MODEL_TYPE, filename="model.safetensors")
lm = moshi.models.loaders.get_moshi_lm(lm_weight, device=DEVICE)
lm_gen = moshi.models.LMGen(lm)

print("Models loaded. Testing pipeline...")

# Create dummy audio: [Batch, Channels, Time]
# 24kHz, 0.1s
audio = torch.randn(1, 1, 2400).to(DEVICE)

try:
    with torch.no_grad(), mimi.streaming(batch_size=1):
        # 1. Encode
        codes = mimi.encode(audio)
        print(f"Codes shape: {codes.shape}") 
        # Expected: [B, num_codebooks, T_frames]
        
        # 2. LM Step
        # LMGen.step(input_tokens)
        # We need to pass the codes. 
        # LMGen typically handles [B, K, T] or [B, T]? 
        # Moshi works on codebooks.
        
        out_tokens = lm_gen.step(codes)
        # out_tokens might be None if no output yet (delay) or [B, K, T]
        
        if out_tokens is not None:
             print(f"Out tokens shape: {out_tokens.shape}")
             
             # 3. Decode
             audio_out = mimi.decode(out_tokens)
             print(f"Audio out shape: {audio_out.shape}")
        else:
             print("LMGen returned None (buffering/delay)")

    print("Pipeline SUCCESS")

except Exception as e:
    print(f"Pipeline FAILED: {e}")
