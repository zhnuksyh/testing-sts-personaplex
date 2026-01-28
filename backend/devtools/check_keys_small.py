
from moshi.models.lm import LMModel
import torch.nn as nn

# Tiny config
config = {
    "dim": 128, 
    "text_card": 100, 
    "existing_text_padding_id": 3, 
    "n_q": 2, 
    "dep_q": 2, 
    "card": 100, 
    "num_heads": 4, 
    "num_layers": 2, 
    "hidden_scale": 2, 
    "causal": True, 
    "context": 128, 
    "max_period": 1000, 
    "gating": "silu", 
    "norm": "rms_norm_f32", 
    "positional_embedding": "rope", 
    "depformer_dim": 64, 
    "depformer_dim_feedforward": 128, 
    "depformer_num_heads": 4, 
    "depformer_num_layers": 2, 
    "depformer_multi_linear": True, 
    "depformer_context": 8, 
    "depformer_max_period": 1000, 
    "depformer_gating": "silu", 
    "depformer_pos_emb": "none", 
    "depformer_weights_per_step": True, 
    "delays": [0] * 3 # n_q + 1 ?
}

print("Instantiating Tiny LMModel...")
# Adjust delays dynamically if needed
model = LMModel(**config)
print("Keys:")
keys = list(model.state_dict().keys())
for k in keys:
    if "layers.0.self_attn" in k:
        print(k)
