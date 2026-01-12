"""
MCP Voice Server
Provides tools for Speech-to-Text and Text-to-Speech
"""
import sys
import os
import tempfile
from typing import Dict, Any, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from base_server import BaseMCPServer

# Voice processing imports
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️  Warning: faster-whisper not installed. Install with: pip install faster-whisper")

try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️  Warning: TTS (Coqui) not installed. Install with: pip install TTS")


class VoiceServer(BaseMCPServer):
    """
    MCP server for voice processing (STT and TTS)
    """
    
    def __init__(self):
        super().__init__(
            name="MCP Voice Server",
            description="Provides Speech-to-Text and Text-to-Speech capabilities",
            version="1.0.0",
            port=8007
        )
        
        # Configuration from environment
        self.whisper_model_name = os.getenv("WHISPER_MODEL", "base")
        self.whisper_device = os.getenv("WHISPER_DEVICE", "cpu")
        self.whisper_compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
        
        self.tts_model_name = os.getenv("TTS_MODEL", "tts_models/en/ljspeech/tacotron2-DDC")
        self.tts_language = os.getenv("TTS_LANGUAGE", "en")
        
        # Initialize models
        self.whisper_model = None
        self.tts_model = None
        
        if WHISPER_AVAILABLE:
            self._init_whisper()
        
        if TTS_AVAILABLE:
            self._init_tts()
    
    def _init_whisper(self):
        """Initialize Faster-Whisper model"""
        try:
            print(f"🎤 Loading Whisper model: {self.whisper_model_name}")
            self.whisper_model = WhisperModel(
                self.whisper_model_name,
                device=self.whisper_device,
                compute_type=self.whisper_compute_type
            )
            print("✅ Whisper model loaded")
        except Exception as e:
            print(f"❌ Failed to load Whisper model: {e}")
    
    def _init_tts(self):
        """Initialize Coqui TTS model"""
        try:
            print(f"🔊 Loading TTS model: {self.tts_model_name}")
            self.tts_model = TTS(model_name=self.tts_model_name)
            print("✅ TTS model loaded")
        except Exception as e:
            print(f"❌ Failed to load TTS model: {e}")
    
    def setup_tools(self):
        """Register all voice processing tools"""
        
        self.register_tool(
            name="transcribe_audio",
            description="Convert audio to text using Speech-to-Text",
            parameters=[
                {"name": "audio_path", "type": "string", "required": True},
                {"name": "language", "type": "string", "required": False},
                {"name": "task", "type": "string", "required": False}  # transcribe or translate
            ],
            handler=self.transcribe_audio
        )
        
        self.register_tool(
            name="synthesize_speech",
            description="Convert text to speech using Text-to-Speech",
            parameters=[
                {"name": "text", "type": "string", "required": True},
                {"name": "output_path", "type": "string", "required": False},
                {"name": "language", "type": "string", "required": False},
                {"name": "speaker", "type": "string", "required": False}
            ],
            handler=self.synthesize_speech
        )
        
        self.register_tool(
            name="detect_language",
            description="Detect language from audio file",
            parameters=[
                {"name": "audio_path", "type": "string", "required": True}
            ],
            handler=self.detect_language
        )
        
        self.register_tool(
            name="list_tts_models",
            description="List available TTS models",
            parameters=[],
            handler=self.list_tts_models
        )
    
    # Tool handlers
    
    async def transcribe_audio(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Transcribe audio to text"""
        if not self.whisper_model:
            return {
                "success": False,
                "error": "Whisper model not available. Install faster-whisper."
            }
        
        audio_path = params["audio_path"]
        language = params.get("language")
        task = params.get("task", "transcribe")  # transcribe or translate
        
        if not os.path.exists(audio_path):
            return {
                "success": False,
                "error": f"Audio file not found: {audio_path}"
            }
        
        try:
            # Transcribe audio
            segments, info = self.whisper_model.transcribe(
                audio_path,
                language=language,
                task=task
            )
            
            # Collect all segments
            transcription = []
            full_text = ""
            
            for segment in segments:
                transcription.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                })
                full_text += segment.text.strip() + " "
            
            return {
                "success": True,
                "text": full_text.strip(),
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration,
                "segments": transcription,
                "segment_count": len(transcription)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def synthesize_speech(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize speech from text"""
        if not self.tts_model:
            return {
                "success": False,
                "error": "TTS model not available. Install TTS (Coqui)."
            }
        
        text = params["text"]
        output_path = params.get("output_path")
        language = params.get("language", self.tts_language)
        speaker = params.get("speaker")
        
        # Generate output path if not provided
        if not output_path:
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, f"tts_output_{os.getpid()}.wav")
        
        try:
            # Synthesize speech
            if speaker and hasattr(self.tts_model, 'speakers'):
                self.tts_model.tts_to_file(
                    text=text,
                    file_path=output_path,
                    speaker=speaker
                )
            else:
                self.tts_model.tts_to_file(
                    text=text,
                    file_path=output_path
                )
            
            # Get file info
            file_size = os.path.getsize(output_path)
            
            return {
                "success": True,
                "audio_path": output_path,
                "file_size": file_size,
                "text_length": len(text),
                "language": language
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def detect_language(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Detect language from audio"""
        if not self.whisper_model:
            return {
                "success": False,
                "error": "Whisper model not available."
            }
        
        audio_path = params["audio_path"]
        
        if not os.path.exists(audio_path):
            return {
                "success": False,
                "error": f"Audio file not found: {audio_path}"
            }
        
        try:
            # Detect language (transcribe first 30 seconds)
            segments, info = self.whisper_model.transcribe(
                audio_path,
                language=None  # Auto-detect
            )
            
            return {
                "success": True,
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_tts_models(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available TTS models"""
        if not TTS_AVAILABLE:
            return {
                "success": False,
                "error": "TTS not available."
            }
        
        try:
            # Get list of available models
            models = TTS().list_models()
            
            # Categorize by language
            categorized = {}
            for model in models:
                parts = model.split('/')
                if len(parts) >= 2:
                    lang = parts[1]
                    if lang not in categorized:
                        categorized[lang] = []
                    categorized[lang].append(model)
            
            return {
                "success": True,
                "models": models,
                "categorized": categorized,
                "count": len(models)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    server = VoiceServer()
    server.run()
