#!/usr/bin/env python3
"""
Generate voice sample previews for PersonaPlex voices.
Requires the backend to be initialized with PersonaPlex.

Usage:
    python scripts/generate_voice_samples.py
"""

import os
import sys
import wave
import struct

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import torch
from huggingface_hub import hf_hub_download

# Sample text for voice preview
SAMPLE_TEXT = "Hello! I'm your AI assistant. How can I help you today?"

# All PersonaPlex voices
VOICES = {
    # Natural Female
    "NATF0": "Aria",
    "NATF1": "Luna", 
    "NATF2": "Nova",
    "NATF3": "Stella",
    # Natural Male
    "NATM0": "Atlas",
    "NATM1": "Orion",
    "NATM2": "Leo",
    "NATM3": "Felix",
    # Expressive Female
    "VARF0": "Ivy",
    "VARF1": "Ruby",
    "VARF2": "Jade",
    "VARF3": "Pearl",
    "VARF4": "Coral",
    # Expressive Male
    "VARM0": "Blaze",
    "VARM1": "Storm",
    "VARM2": "Ridge",
    "VARM3": "Drake",
    "VARM4": "Flint",
}

OUTPUT_DIR = "public/voice-samples"


def generate_placeholder_samples():
    """
    Generate placeholder audio samples (silence with different lengths).
    In production, these should be replaced with actual TTS samples.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    sample_rate = 24000
    duration = 2.0  # 2 seconds
    
    for voice_id, voice_name in VOICES.items():
        output_path = os.path.join(OUTPUT_DIR, f"{voice_id}.wav")
        
        # Generate a simple sine wave tone (different freq per voice for distinction)
        # This is a placeholder - real samples would come from PersonaPlex
        freq = 200 + hash(voice_id) % 300  # Different frequency per voice
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create a gentle fade in/out
        envelope = np.ones_like(t)
        fade_samples = int(0.1 * sample_rate)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        
        # Generate audio
        audio = 0.3 * np.sin(2 * np.pi * freq * t) * envelope
        audio = (audio * 32767).astype(np.int16)
        
        # Write WAV file
        with wave.open(output_path, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio.tobytes())
        
        print(f"Generated: {output_path} ({voice_name})")
    
    print(f"\n✅ Generated {len(VOICES)} placeholder samples in {OUTPUT_DIR}/")
    print("Note: These are placeholder tones. Replace with real PersonaPlex TTS for production.")


def generate_real_samples():
    """
    Generate actual voice samples using PersonaPlex TTS.
    This requires the full model to be loaded.
    """
    try:
        from moshi.models import loaders
        from backend.app.core.config import HF_TOKEN, DEVICE
    except ImportError:
        print("❌ Could not import PersonaPlex. Using placeholder samples.")
        generate_placeholder_samples()
        return
    
    # TODO: Implement real TTS generation when PersonaPlex TTS API is available
    # For now, use placeholders
    print("⚠️  Real TTS generation not yet implemented. Using placeholder samples.")
    generate_placeholder_samples()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate voice sample previews")
    parser.add_argument("--placeholder", action="store_true", 
                        help="Generate placeholder samples (sine waves)")
    args = parser.parse_args()
    
    if args.placeholder:
        generate_placeholder_samples()
    else:
        generate_real_samples()
