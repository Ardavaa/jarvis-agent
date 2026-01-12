"""
Test script for MCP Voice Server
"""
import asyncio
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from server import VoiceServer


async def test_voice_server():
    """Test MCP Voice Server"""
    print("=" * 60)
    print("Testing MCP Voice Server")
    print("=" * 60)
    
    server = VoiceServer()
    server.setup_tools()
    
    print(f"\n✅ Server initialized: {server.name}")
    print(f"📝 Tools registered: {len(server.tools)}")
    print(f"🔧 Available tools:")
    for tool in server.tool_definitions:
        print(f"   - {tool.name}: {tool.description}")
    
    # Check Whisper availability
    print("\n" + "=" * 60)
    print("Test 1: Check Whisper Model")
    print("=" * 60)
    if server.whisper_model:
        print(f"✅ Whisper model loaded: {server.whisper_model_name}")
        print(f"   Device: {server.whisper_device}")
        print(f"   Compute type: {server.whisper_compute_type}")
    else:
        print("❌ Whisper model not available")
        return
    
    # Check TTS availability
    print("\n" + "=" * 60)
    print("Test 2: Check TTS Model")
    print("=" * 60)
    if server.tts_model:
        print(f"✅ TTS model loaded: {server.tts_model_name}")
    else:
        print("⚠️  TTS model not available (optional)")
        print("   This is normal if TTS wasn't installed")
    
    # Test with sample audio (if available)
    print("\n" + "=" * 60)
    print("Test 3: Test Audio Transcription")
    print("=" * 60)
    
    # Create a simple test audio file using text
    print("ℹ️  To test transcription, you need an audio file.")
    print("   You can:")
    print("   1. Record a voice message and save as WAV")
    print("   2. Use any existing audio file")
    print("   3. Skip this test for now")
    print("\n   Example test:")
    print("   result = await server.transcribe_audio({")
    print("       'audio_path': 'path/to/your/audio.wav'")
    print("   })")
    
    # Test language detection
    print("\n" + "=" * 60)
    print("Test 4: List TTS Models (if available)")
    print("=" * 60)
    if server.tts_model:
        result = await server.list_tts_models({})
        if result.get("success"):
            print(f"✅ Found {result.get('count')} TTS models")
            # Show first few
            models = result.get("models", [])
            print("   Sample models:")
            for model in models[:5]:
                print(f"   - {model}")
        else:
            print(f"❌ Failed: {result.get('error')}")
    else:
        print("⚠️  Skipped (TTS not available)")
    
    print("\n" + "=" * 60)
    print("✅ Voice server tests completed!")
    print("=" * 60)
    print("\nServer is ready to use!")
    print("Start with: uv run python server.py")


if __name__ == "__main__":
    asyncio.run(test_voice_server())
