
import moshi.models.loaders
import logging

try:
    # Try to access the internal config dict
    # It seems to be _lm_kwargs in some versions, or hardcoded.
    # We will try to inspect the loaders module content to find where the config is.
    print(dir(moshi.models.loaders))
    
    # If _lm_kwargs is a dict:
    if hasattr(moshi.models.loaders, '_lm_kwargs') and isinstance(moshi.models.loaders._lm_kwargs, dict):
        print("Found _lm_kwargs dict:")
        # Print keys
        print(moshi.models.loaders._lm_kwargs.keys())
        # Try to print the config for moshiko
        if 'kyutai/moshiko-pytorch-bf16' in moshi.models.loaders._lm_kwargs:
             print("Config for moshiko:")
             print(moshi.models.loaders._lm_kwargs['kyutai/moshiko-pytorch-bf16'])
             
except Exception as e:
    print(f"Error: {e}")
