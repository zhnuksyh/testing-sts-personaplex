
import logging
import os
import numpy as np
import torch
from huggingface_hub import hf_hub_download

try:
    from moshi.models import loaders, LMGen
    from moshi.models.compression import MimiModel
    from moshi.models.lm import LMModel
    MOSHI_AVAILABLE = True
except ImportError:
    MOSHI_AVAILABLE = False
    loaders = None
    LMGen = None

from backend.app.core.config import SAMPLE_RATE, CHUNK_SIZE, DEVICE, HF_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PersonaPlex-Engine")


class PersonaPlexWrapper:
    """
    Wrapper for NVIDIA PersonaPlex-7B model.
    Uses official moshi-personaplex loaders for proper model initialization.
    """
    
    def __init__(self, device: str = "cuda", cpu_offload: bool = False):
        self.device = torch.device(device)
        self.repo_id = loaders.DEFAULT_REPO  # nvidia/personaplex-7b-v1
        
        logger.info(f"Loading PersonaPlex from {self.repo_id}...")
        
        # Download and load Mimi (Neural Audio Codec)
        logger.info("Loading Mimi tokenizer...")
        mimi_weight = hf_hub_download(
            repo_id=self.repo_id, 
            filename=loaders.MIMI_NAME,
            token=HF_TOKEN
        )
        self.mimi = loaders.get_mimi(mimi_weight, device=self.device)
        self.mimi.eval()
        
        # Frame size from Mimi config (24kHz / 12.5Hz = 1920 samples)
        self.frame_size = int(self.mimi.sample_rate / self.mimi.frame_rate)
        logger.info(f"Mimi loaded. Frame size: {self.frame_size}, Sample rate: {self.mimi.sample_rate}")
        
        # Download and load LM (Language Model - the "brain")
        logger.info("Loading PersonaPlex LM...")
        lm_weight = hf_hub_download(
            repo_id=self.repo_id, 
            filename=loaders.MOSHI_NAME,
            token=HF_TOKEN
        )
        self.lm = loaders.get_moshi_lm(
            lm_weight, 
            device=self.device,
            cpu_offload=cpu_offload
        )
        self.lm.eval()
        
        # Create LMGen for streaming inference with voice/text prompt support
        self.lm_gen = LMGen(
            self.lm,
            audio_silence_frame_cnt=int(0.5 * self.mimi.frame_rate),  # 0.5s of silence threshold
            sample_rate=self.mimi.sample_rate,
            device=self.device,
            frame_rate=self.mimi.frame_rate,
        )
        
        # Enter streaming mode
        self.mimi.streaming_forever(batch_size=1)
        self.lm_gen.streaming_forever(batch_size=1)
        
        # Voice prompt state
        self.current_voice_prompt = None
        self.voice_prompt_dir = None
        
        logger.info("PersonaPlex loaded successfully!")
    
    def set_voice_prompt_dir(self, voice_prompt_dir: str):
        """Set the directory containing voice prompt embeddings."""
        self.voice_prompt_dir = voice_prompt_dir
    
    def load_voice_prompt(self, voice_name: str):
        """Load a voice prompt embedding file (e.g., NATF0.pt, NATM1.pt)."""
        if self.voice_prompt_dir is None:
            logger.warning("Voice prompt directory not set. Skipping voice prompt.")
            return
        
        voice_path = os.path.join(self.voice_prompt_dir, f"{voice_name}.pt")
        if os.path.exists(voice_path):
            self.lm_gen.load_voice_prompt_embeddings(voice_path)
            self.current_voice_prompt = voice_name
            logger.info(f"Loaded voice prompt: {voice_name}")
        else:
            logger.warning(f"Voice prompt not found: {voice_path}")
    
    def set_text_prompt(self, text_prompt: str, tokenizer=None):
        """Set the text prompt (persona) for the model."""
        if tokenizer is not None:
            # Wrap with system tags as model expects
            cleaned = text_prompt.strip()
            if not (cleaned.startswith("<system>") and cleaned.endswith("<system>")):
                text_prompt = f"<system> {cleaned} <system>"
            self.lm_gen.text_prompt_tokens = tokenizer.encode(text_prompt)
            logger.info(f"Set text prompt: {text_prompt[:50]}...")
        else:
            logger.warning("No tokenizer provided. Text prompts require a tokenizer.")
    
    def process(self, audio_tensor: torch.Tensor) -> torch.Tensor | None:
        """
        Process a single frame of audio through the PersonaPlex pipeline.
        
        Args:
            audio_tensor: [1, 1, frame_size] float32 tensor
            
        Returns:
            Output audio tensor or None if still buffering
        """
        with torch.no_grad():
            # Encode user audio to acoustic tokens
            codes = self.mimi.encode(audio_tensor)
            # codes: [1, 8, T_frames]
            
            # Step through each time step
            output_audio = None
            for c in range(codes.shape[-1]):
                tokens = self.lm_gen.step(codes[:, :, c:c+1])
                if tokens is None:
                    continue
                
                # tokens: [1, 17, 1] - Channel 0 is text, Channels 1-8 are audio
                audio_tokens = tokens[:, 1:9, :]  # Extract audio channels
                
                # Decode to audio
                pcm = self.mimi.decode(audio_tokens)
                if output_audio is None:
                    output_audio = pcm
                else:
                    output_audio = torch.cat([output_audio, pcm], dim=-1)
            
            return output_audio
    
    def reset(self):
        """Reset streaming state for a new session."""
        logger.info("Resetting PersonaPlex state...")
        self.mimi.reset_streaming()
        self.lm_gen.reset_streaming()
    
    def warmup(self):
        """Warm up the model with dummy data."""
        logger.info("Warming up PersonaPlex...")
        for _ in range(4):
            chunk = torch.zeros(1, 1, self.frame_size, dtype=torch.float32, device=self.device)
            codes = self.mimi.encode(chunk)
            for c in range(codes.shape[-1]):
                tokens = self.lm_gen.step(codes[:, :, c:c+1])
                if tokens is not None:
                    _ = self.mimi.decode(tokens[:, 1:9])
        
        if self.device.type == 'cuda':
            torch.cuda.synchronize()
        logger.info("Warmup complete.")
    
    def close(self):
        """Cleanup resources."""
        pass  # streaming_forever handles cleanup


class PersonaPlexEngine:
    """
    Main engine class that handles audio processing.
    """
    
    def __init__(self):
        self.is_mock = True
        self.wrapper = None
        self.buffer = np.array([], dtype=np.float32)

        if not MOSHI_AVAILABLE:
            logger.error("moshi-personaplex not found. Falling back to MOCK engine.")
            logger.error("Install with: pip install /path/to/personaplex/moshi/.")
            return

        try:
            self.wrapper = PersonaPlexWrapper(device=DEVICE)
            self.wrapper.warmup()
            self.is_mock = False
            logger.info("PersonaPlex Engine loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load PersonaPlex: {e}", exc_info=True)
            logger.warning("Falling back to MOCK engine.")
            self.is_mock = True

    def configure(self, persona: str, voice_id: str):
        """Configure the persona and voice for the session."""
        if self.wrapper is not None:
            # Voice prompt loading would require voice prompt directory
            # For now, just log the configuration
            logger.info(f"Configured persona: {persona[:50]}..., voice: {voice_id}")
            # TODO: Implement voice prompt loading when voice files are available
            # self.wrapper.load_voice_prompt(voice_id)

    def process_audio_frame(self, audio_frame: bytes) -> bytes:
        """
        Process incoming audio bytes and return generated audio bytes.
        """
        if self.is_mock:
            # Mock: return low-volume noise
            return np.random.uniform(-0.1, 0.1, len(audio_frame) // 4).astype(np.float32).tobytes()

        try:
            # Convert bytes to float32 numpy
            audio_np = np.frombuffer(audio_frame, dtype=np.float32)

            # Validate input
            if not np.isfinite(audio_np).all():
                logger.warning("Invalid audio data (NaN/Inf). Returning silence.")
                return np.zeros_like(audio_np).tobytes()
            
            # Auto-scale if values look like Int16 misinterpreted as Float32
            max_val = np.abs(audio_np).max()
            if max_val > 5.0:
                audio_np = audio_np / 32768.0

            # Clip to [-1, 1]
            audio_np = np.clip(audio_np, -1.0, 1.0)
            
            # Add to buffer
            self.buffer = np.concatenate((self.buffer, audio_np))
            
            # Process frames
            FRAME_SIZE = self.wrapper.frame_size if self.wrapper else 1920
            output_audio = b""
            
            while len(self.buffer) >= FRAME_SIZE:
                chunk = self.buffer[:FRAME_SIZE]
                self.buffer = self.buffer[FRAME_SIZE:]
                
                # Convert to tensor [1, 1, frame_size]
                chunk_tensor = torch.from_numpy(chunk).view(1, 1, -1).to(
                    device=self.wrapper.device, 
                    dtype=torch.float32
                )
                
                out_tensor = self.wrapper.process(chunk_tensor)
                
                if out_tensor is not None:
                    out_np = out_tensor.squeeze().cpu().numpy().astype(np.float32)
                    output_audio += out_np.tobytes()

            return output_audio
            
        except Exception as e:
            logger.error(f"Error in inference: {e}", exc_info=True)
            return b""

    def reset(self):
        """Reset state for a new session."""
        self.buffer = np.array([], dtype=np.float32)
        if self.wrapper:
            self.wrapper.reset()

    def shutdown(self):
        """Shutdown the engine."""
        if self.wrapper:
            self.wrapper.close()


# Global Instance
engine = PersonaPlexEngine()
