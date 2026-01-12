# Voice Server Installation Guide

## Overview

The Voice Server provides Speech-to-Text (STT) and Text-to-Speech (TTS) capabilities for JARVIS.

## Dependencies

### Required (STT only)
```bash
cd mcp-servers/mcp-voice
uv pip install faster-whisper pydub soundfile ffmpeg-python
```

### Optional (TTS)
Coqui TTS has build issues on Windows. You have two options:

#### Option 1: Skip TTS (STT only)
The server will work fine with just STT. TTS tools will return "not available" errors.

#### Option 2: Install TTS (Advanced)
If you want TTS, you need to install it separately:

**Prerequisites**:
- Microsoft C++ Build Tools
- Visual Studio 2019 or newer

**Installation**:
```bash
# Install build tools first
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Then install TTS
pip install TTS
```

**Alternative**: Use a pre-built wheel or Docker container.

## System Requirements

### For STT (Faster-Whisper):
- **Disk Space**: 1-10GB (depending on model)
  - tiny: ~75MB
  - base: ~142MB
  - small: ~466MB
  - medium: ~1.5GB
  - large: ~2.9GB
- **RAM**: 2GB minimum, 4GB+ recommended
- **CPU**: Any modern CPU (GPU optional but faster)

### For TTS (Coqui TTS):
- **Disk Space**: 500MB - 2GB per model
- **RAM**: 4GB minimum
- **CPU**: Modern CPU recommended

## FFmpeg Installation

FFmpeg is required for audio processing.

### Windows:
1. Download from: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH
4. Verify: `ffmpeg -version`

### Alternative (Chocolatey):
```bash
choco install ffmpeg
```

## Testing

### Test STT Only:
```bash
cd mcp-servers/mcp-voice
uv run python server.py
```

The server will start with STT available and TTS disabled.

### Test with Sample Audio:
```bash
curl -X POST http://localhost:8007/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "transcribe_audio",
    "parameters": {
      "audio_path": "path/to/audio.wav"
    }
  }'
```

## Recommended Setup

For most users, **STT-only mode is recommended**:
- Faster installation
- No build issues
- Sufficient for voice input
- Can add TTS later if needed

## Troubleshooting

### "faster-whisper not installed"
```bash
uv pip install faster-whisper
```

### "TTS not installed"
This is normal if you skipped TTS installation. The server will work fine for STT.

### "FFmpeg not found"
Install FFmpeg and add to PATH (see above).

### "Out of memory"
Use a smaller Whisper model:
- Change `WHISPER_MODEL=tiny` in `.env`
- Restart the server

## Configuration

Edit `.env` file:

```bash
# Whisper model size (tiny, base, small, medium, large)
WHISPER_MODEL=base

# Device (cpu or cuda)
WHISPER_DEVICE=cpu

# Compute type (int8, float16, float32)
WHISPER_COMPUTE_TYPE=int8

# TTS model (if installed)
TTS_MODEL=tts_models/en/ljspeech/tacotron2-DDC
TTS_LANGUAGE=en
```

## Performance Tips

1. **Use smaller models for faster processing**:
   - `tiny` or `base` for real-time
   - `small` or `medium` for better accuracy

2. **Use GPU if available**:
   - Set `WHISPER_DEVICE=cuda`
   - Requires NVIDIA GPU with CUDA

3. **Optimize compute type**:
   - `int8` - Fastest, least memory
   - `float16` - Good balance (GPU only)
   - `float32` - Best quality, slowest

## Next Steps

1. Start the voice server
2. Test with sample audio
3. Integrate with JARVIS agent
4. (Optional) Install TTS later if needed
