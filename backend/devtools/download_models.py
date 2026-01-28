
import os
from huggingface_hub import hf_hub_download
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_models():
    DEVICE = "cuda" # Not used for download, just context
    MODEL_TYPE = "nvidia/personaplex-7b-v1"
    
    logger.info("--- STARTING DOWNLOAD ---")
    
    # 1. Download Mimi
    logger.info(f"1. Downloading Mimi Codec (model.safetensors) from kyutai/mimi...")
    try:
        mimi_path = hf_hub_download(repo_id="kyutai/mimi", filename="model.safetensors")
        logger.info(f"   SUCCESS: Mimi downloaded to {mimi_path}")
    except Exception as e:
        logger.error(f"   FAILED to download Mimi: {e}")
        return

    # 2. Download PersonaPlex
    logger.info(f"2. Downloading PersonaPlex Model (model.safetensors) from {MODEL_TYPE}...")
    logger.info("   WARNING: This file is LARGE (~7GB). Please wait...")
    try:
        lm_path = hf_hub_download(repo_id=MODEL_TYPE, filename="model.safetensors")
        logger.info(f"   SUCCESS: PersonaPlex downloaded to {lm_path}")
    except Exception as e:
        logger.error(f"   FAILED to download PersonaPlex: {e}")
        return

    logger.info("--- DOWNLOAD COMPLETE ---")
    logger.info("You can now restart './run_host_https.sh'")

if __name__ == "__main__":
    download_models()
