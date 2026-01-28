
import logging
import time
import numpy as np
import torch
from huggingface_hub import hf_hub_download
try:
    import moshi
    import moshi.models.loaders
    from moshi.models.lm import LMModel
except ImportError:
    moshi = None

from backend.app.core.config import CHUNK_SIZE, MODEL_TYPE, DEVICE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PersonaPlex-Engine")

class MoshiWrapper:
    def __init__(self):
        self.device = DEVICE
        # Use Moshiko (Kyutai) as the stable base model due to architecture mismatches 
        # with the current installed 'moshi' library and the NVIDIA checkpoint keys.
        self.repo_id = "kyutai/moshiko-pytorch-bf16"
        
        logger.info(f"Loading Moshi Tokenizer (Mimi) from {self.repo_id}...")
        # Specific checkpoint that works with current library
        mimi_weight = hf_hub_download(repo_id=self.repo_id, filename="tokenizer-e351c8d8-checkpoint125.safetensors")
        self.mimi = moshi.models.loaders.get_mimi(mimi_weight, device=self.device)
        self.mimi.to(self.device)
        self.mimi.eval()
        
        # Determine strict buffering rule from Mimi
        # Frame size is typically 1920 for 24kHz (80ms)
        self.frame_size = 1920 
        
        logger.info(f"Loading Moshi LM from {self.repo_id}...")
        lm_weight = hf_hub_download(repo_id=self.repo_id, filename="model.safetensors")
        self.lm = moshi.models.loaders.get_moshi_lm(lm_weight, device=self.device)
        self.lm.to(self.device)
        self.lm.eval()
        
        self.lm_gen = moshi.models.LMGen(self.lm)
        
        # Enter streaming context permanently
        self.streaming_ctx = self.mimi.streaming(batch_size=1)
        self.streaming_ctx.__enter__()
        
        self.lm_gen_ctx = self.lm_gen.streaming(batch_size=1)
        self.lm_gen_ctx.__enter__()
        
        logger.info("MoshiWrapper initialized successfully.")

    def process(self, audio_tensor: torch.Tensor) -> torch.Tensor | None:
        # audio_tensor: [B, C, T]
        with torch.no_grad():
            codes = self.mimi.encode(audio_tensor)
            # codes: [B, num_codebooks, T_frames]
            
            # SAFETY: Clamp codes to LM vocabulary size (likely 2048)
            # Moshi/Mimi sometimes output 2048 as a special token or padding, 
            # which might be out of bounds for the LM embedding.
            # logger.info(f"Codes min: {codes.min()}, max: {codes.max()}")
            codes = torch.clamp(codes, min=0, max=2047)
            
            tokens_out = self.lm_gen.step(codes)
            if tokens_out is None:
                return None
            
            # MEANINGFUL FIX: Clamp LM output tokens too
            # If LM predicts > 2047, Mimi decode might crash
            # tokens_out = torch.clamp(tokens_out, min=0, max=2047)
            
            # Check shape
            # Expected: [B, 16, 1]. 
            # Channel 0: Text. Channel 1-8: Audio. Channel 9-15: Input.
            # Check shape
            # Expected: [B, 16, 1]. 
            # Channel 0: Text. Channel 1-8: Audio. Channel 9-15: Input.
            # logger.info(f"Step out shape: {tokens_out.shape}")
            # logger.info(f"Chan 0 (Text): {tokens_out[0,0,0]}, Chan 1 (Audio): {tokens_out[0,1,0]}")

            # Correct Slicing: Skip Channel 0 (Text), Take Channels 1-8 (Audio)
            if tokens_out.shape[1] >= 9:
                audio_tokens = tokens_out[:, 1:9, :]
            else:
                # Fallback if shape is weird
                audio_tokens = tokens_out[:, :8, :]
            
            # Clamp ONLY audio tokens for Mimi
            audio_tokens = torch.clamp(audio_tokens, min=0, max=2047)
                
            audio_out = self.mimi.decode(audio_tokens)
            return audio_out

    def close(self):
        if self.streaming_ctx:
            self.streaming_ctx.__exit__(None, None, None)
        if self.lm_gen_ctx:
            self.lm_gen_ctx.__exit__(None, None, None)

    def reset(self):
        """Exit and re-enter streaming contexts to clear history."""
        # logger.info("Resetting Moshi state...")
        self.close()
        
        self.streaming_ctx = self.mimi.streaming(batch_size=1)
        self.streaming_ctx.__enter__()
        
        self.lm_gen_ctx = self.lm_gen.streaming(batch_size=1)
        self.lm_gen_ctx.__enter__()

class PersonaPlexEngine:
    def __init__(self):
        self.is_mock = True
        self.wrapper = None
        self.buffer = np.array([], dtype=np.float32)

        if moshi is None:
            logger.error("Moshi library not found. Falling back to MOCK engine.")
            return

        try:
            self.wrapper = MoshiWrapper()
            self.is_mock = False
            logger.info("Real AI Engine Loaded Successfully.")
        except Exception as e:
            logger.error(f"Failed to load real model: {e}", exc_info=True)
            logger.warning("Falling back to MOCK engine.")
            self.is_mock = True

    def configure(self, persona: str, voice_id: str):
        pass

    def process_audio_frame(self, audio_frame: bytes) -> bytes:
        """
        Process incoming audio bytes and return generated audio bytes.
        """
        if self.is_mock:
            # Mock behavior: Echo random noise or simple tone
            # return audio_frame # Echo
            return np.random.uniform(-0.1, 0.1, len(audio_frame) // 4).astype(np.float32).tobytes()

        # Real inference
        try:
            # Convert bytes to float32 numpy
            audio_np = np.frombuffer(audio_frame, dtype=np.float32)

            # VALIDATION: Check for NaNs/Infs and Clamp
            if not np.isfinite(audio_np).all():
                logger.warning("Invalid audio data detected (NaN/Inf). returning silence to avoid model crash.")
                return np.zeros_like(audio_np).tobytes()
            
            # Auto-Scale Heuristic:
            # If values significantly exceed 1.0, it's likely Int16 data being treated as Float32.
            # Normal range of float audio is -1.0 to 1.0. Int16 is -32768 to 32767.
            max_val = np.abs(audio_np).max()
            rms_val = np.sqrt(np.mean(audio_np**2))
            # logger.info(f"Audio Frame RMS: {rms_val:.4f}, Max: {max_val:.4f}")

            if max_val > 5.0:
                 # logger.warning(f"High amplitude detected (max {max_val}). Assuming Int16 mismatch and normalizing.")
                 audio_np = audio_np / 32768.0

            # Clip to standard audio range [-1, 1] to prevent embedding explosions
            audio_np = np.clip(audio_np, -1.0, 1.0)
            
            # Add to buffer
            self.buffer = np.concatenate((self.buffer, audio_np))
            
            # Check if we have enough for a frame (1920 samples)
            # We strictly consume chunks of 1920
            FRAME_SIZE = 1920
            
            output_audio = b""
            
            while len(self.buffer) >= FRAME_SIZE:
                chunk = self.buffer[:FRAME_SIZE]
                self.buffer = self.buffer[FRAME_SIZE:]
                
                # To Tensor [1, 1, 1920]
                chunk_tensor = torch.from_numpy(chunk).view(1, 1, -1).to(DEVICE)
                
                out_tensor = self.wrapper.process(chunk_tensor)
                
                if out_tensor is not None:
                    # [1, 1, T] -> cpu numpy
                    out_np = out_tensor.squeeze().cpu().numpy().astype(np.float32)
                    output_audio += out_np.tobytes()
                else:
                    # Delay/Silence - send 0s or nothing? 
                    # If we send nothing, frontend might starve. 
                    # Use zeros for silence if LM is thinking/buffering.
                    # Or just return empty and let frontend wait.
                    pass 

            return output_audio
            
        except Exception as e:
            logger.error(f"Error in inference: {e}", exc_info=True)
            return b"" # Return silence or original on error

    def shutdown(self):
        if self.wrapper:
            self.wrapper.close()

    def reset(self):
        """Reset the internal buffer and model state for a new session."""
        self.buffer = np.array([], dtype=np.float32)
        if self.wrapper:
            self.wrapper.reset()


# Global Instance
engine = PersonaPlexEngine()
