
import os
os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
import logging
import torch
import numpy as np
from huggingface_hub import hf_hub_download
import moshi.models.loaders

logging.basicConfig(level=logging.INFO)
DEVICE = "cuda"

class MoshiWrapper:
    def __init__(self):
        self.device = DEVICE
        self.repo_id = "kyutai/moshiko-pytorch-bf16"
        
        print(f"Loading Moshi Tokenizer (Mimi) from {self.repo_id}...")
        mimi_weight = hf_hub_download(repo_id=self.repo_id, filename="tokenizer-e351c8d8-checkpoint125.safetensors")
        self.mimi = moshi.models.loaders.get_mimi(mimi_weight, device=self.device)
        self.mimi.to(self.device)
        self.mimi.eval()
        
        print(f"Loading Moshi LM from {self.repo_id}...")
        lm_weight = hf_hub_download(repo_id=self.repo_id, filename="model.safetensors")
        self.lm = moshi.models.loaders.get_moshi_lm(lm_weight, device=self.device)
        self.lm.to(self.device)
        self.lm.eval()
        
        self.lm_gen = moshi.models.LMGen(self.lm)
        
        self.streaming_ctx = self.mimi.streaming(batch_size=1)
        self.streaming_ctx.__enter__()
        
        self.lm_gen_ctx = self.lm_gen.streaming(batch_size=1)
        self.lm_gen_ctx.__enter__()
        
        print("MoshiWrapper initialized.")

    def process(self, audio_tensor: torch.Tensor):
        with torch.no_grad():
            print(f"Encoding shape: {audio_tensor.shape}")
            codes = self.mimi.encode(audio_tensor)
            print(f"Codes shape: {codes.shape}")
            print(f"Codes min: {codes.min()}, Max: {codes.max()}")
            
            # Check LM config
            print(f"LM n_q: {self.lm.n_q}, dep_q: {self.lm.dep_q}")
            
            # Check ranges against LM config

            # LM expects codes in range [0, 2048)? 
            
            print("Stepping LM...")
            tokens_out = self.lm_gen.step(codes)
            
            if tokens_out is None:
                print("LM returned None")
                return None
            
            print(f"Tokens output shape: {tokens_out.shape}")   
            audio_out = self.mimi.decode(tokens_out)
            return audio_out

print("Starting Debug Test (Silence Check)...")
wrapper = MoshiWrapper()
# Test exact silence (zeros) to trigger potential padding code issues
chunk = torch.zeros(1, 1, 1920).to(DEVICE)
try:
    for i in range(10):
        out = wrapper.process(chunk)
        if out is not None:
             print(f"Step {i}: Got audio {out.shape}")
        else:
             print(f"Step {i}: None")
    print("Success!")
except Exception as e:
    print(f"CRASH: {e}")
except RuntimeError as re:
    print(f"RUNTIME ERROR: {re}")
