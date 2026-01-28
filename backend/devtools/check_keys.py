
import logging
from moshi.models.lm import LMModel
import torch.nn as nn

# Moshi 7B approx config
config = {
    "dim": 4096, 
    "text_card": 32000, 
    "existing_text_padding_id": 3, 
    "n_q": 16, 
    "dep_q": 8, 
    "card": 2048, 
    "num_heads": 32, 
    "num_layers": 32, 
    "hidden_scale": 4.125, 
    "causal": True, 
    "context": 3000, 
    "max_period": 10000, 
    "gating": "silu", 
    "norm": "rms_norm_f32", 
    "positional_embedding": "rope", 
    "depformer_dim": 1024, 
    "depformer_dim_feedforward": 4224, 
    "depformer_num_heads": 16, 
    "depformer_num_layers": 6, 
    "depformer_multi_linear": True, 
    "depformer_context": 8, 
    "depformer_max_period": 10000, 
    "depformer_gating": "silu", 
    "depformer_pos_emb": "none", 
    "depformer_weights_per_step": True, 
    "delays": [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1]
}

print("Instantiating LMModel...")
try:
    model = LMModel(**config)
    print("Keys (first 10):")
    keys = list(model.state_dict().keys())
    for k in keys[:10]:
        print(k)
        
    print("\nSearch for 'transformer' or 'decoder':")
    for k in keys:
        if "layers.0.self_attn" in k:
            print(k)
            break
            
except Exception as e:
    print(f"Error: {e}")
