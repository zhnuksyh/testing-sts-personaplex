# PersonaPlex & Moshi Integration Journey

This document chronicles the challenges encountered during the integration of the NVIDIA/Kyutai "Moshiko" model for real-time Speech-to-Speech (STS), the specific errors that occurred, and the robust solutions implemented to fix them.

## 1. The Challenges (What Went Wrong)

We faced three distinct classes of critical failures that prevented stable operation.

### A. The "Device-Side Assert" (GPU Crash)
*   **Symptom**: The backend would crash with `RuntimeError: CUDA error: device-side assert triggered` immediately upon receiving audio or silence.
*   **Root Cause**: The Model (Neural Network) has a fixed "Vocabulary" of **2048** tokens.
    *   Inputting silence or undefined audio sometimes generated token IDs like `2050` or `3000`.
    *   When the GPU tried to look up these IDs in the embedding table (size 2048), it accessed invalid memory, causing a hard crash.
*   **Resolution**: **Safety Clamping**.
    *   We enforced a strict mathematical limit on all input and output tokens:
    *   `token = torch.clamp(token, min=0, max=2047)`
    *   This makes it physically impossible for the model to request an invalid ID.

### B. The "Static / White Noise"
*   **Symptom**: Determining the user's voice resulted in loud, aggressive static or "square wave" noise.
*   **Root Cause**: **Data Type Mismatch**.
    *   The Browser/Frontend recorded audio as `Int16` (Integers from -32,768 to +32,767).
    *   The Backend AI expected `Float32` (Decimals from -1.0 to +1.0).
    *   When the AI received `3000`, it interpreted it as "3000x louder than the loudest possible sound," resulting in destroyed audio.
*   **Resolution**: **End-to-End Float32**.
    *   Updated Frontend Loop: Send raw `Float32Array` directly from the AudioWorklet.
    *   Added Backend Heuristic: If we see values > 5.0, automatically divide by 32,768 just in case.

### C. The "Random Words / Semantic Noise"
*   **Symptom**: The model would output random words, lagging phrases, or semantic gibberish mixed with noise.
*   **Root Cause**: **Channel Mixing**.
    *   The Moshiko model outputs **16 Channels** of data.
    *   **Channel 0**: Text Control Tokens (Values > 2048, representing words).
    *   **Channels 1-8**: Audio Acoustic Tokens (Values < 2048, representing sound).
    *   Generic decoders often default to "Channel 0". We were feeding *Text Tokens* into the *Audio Decoder*, creating chaos.
*   **Resolution**: **Explicit Channel Slicing**.
    *   We modified the engine to discard Channel 0 and strictly select Channels 1-8: `tokens[:, 1:9, :]`.

---

## 2. Technical Architecture for Reliability

To ensure this setup remains stable ("less resistant"), we implemented the following architecture:

### 1. The "Safety Washer" Pipeline
Never trust raw model output.
```python
# 1. Clamp Inputs
codes = torch.clamp(codes, 0, 2047)

# 2. Slice Output (Ignore Text Channel)
audio_tokens = tokens_out[:, 1:9, :]

# 3. Clamp Outputs
audio_tokens = torch.clamp(audio_tokens, 0, 2047)
```

### 2. Session Isolation
Stateful streaming models (like Moshi) accumulate "memory" (KV Cache). If user A disconnects and user B connects, user B might hear user A's "ghost" context or suffer from a full buffer.
*   **Fix**: Call `engine.reset()` on every `websocket.accept()`.

### 3. Inspection Scripts
We created `inspect_model_config.py` to scientifically verify the model's physical limits (Vocabulary Size, Number of Quantizers) instead of guessing.

---

## 3. How to Approach Better Next Time

If setting this up again from scratch, follow these "Golden Rules":

1.  **Inspect Before Inference**: Run a config script to print `num_codebooks` and `cardinality`. If the documentation says "Moshi", verify if it's the 8-quantizer or 16-quantizer version immediately.
2.  **Strict Typing Protocol**: Decide on `Float32` vs `Int16` at the start. Use `numpy` or `blobs` to enforce this. Never rely on implicit casting.
3.  **Visualization**: Use the "RMS Logging" technique we added. Seeing `RMS: 0.0000` vs `RMS: 15403.0` immediately reveals data type errors that are invisible in code.
4.  **Isolate Modalities**: Multimodal models (Speech+Text) always interleave data. Always check which channel corresponds to which modality before routing to speakers.
