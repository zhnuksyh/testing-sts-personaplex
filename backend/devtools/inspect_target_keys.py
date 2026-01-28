
import moshi.models.loaders
import torch
import logging

# Suppress warnings
logging.getLogger().setLevel(logging.ERROR)

print("Instantiating dummy Moshi LM...")
try:
    # Try using None as filename to get initialized model
    # We might need to pass lm_kwargs. 
    # Let's try to get default kwargs from loaders or just guess.
    # Moshi 7B usually has dim=4096, n_layers=32, n_heads=32? 
    # But let's see if get_moshi_lm works without file.
    
    # We use a known public model ID just to trigger the config logic if needed, 
    # but passing filename=None usually means 'random init'.
    # However, get_moshi_lm logic might require a file to read config.
    
    # Let's try to import LMModel directly and init it.
    from moshi.models.lm import LMModel
    config = moshi.models.loaders._lm_kwargs("kyutai/moshiko-pytorch-bf16") # Get default configs
    if config is None:
         config = {
             "d_model": 4096, 
             "n_layers": 32, 
             "n_heads": 32, 
             "dim_feedforward": 16384,
             "vocab_size": 32000 # Guess
         }
         
    model = LMModel(**config)
    print("Model instantiated.")
    
    keys = list(model.state_dict().keys())
    print("Expected keys (first 20):")
    for k in keys[:20]:
        print(k)

except Exception as e:
    print(f"Failed to instantiate: {e}")
