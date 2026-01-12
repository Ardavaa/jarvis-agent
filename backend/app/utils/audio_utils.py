"""
Audio processing utilities
"""
import os
from typing import Optional, Tuple
from pathlib import Path


def validate_audio_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate audio file
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if file exists
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    
    # Check file extension
    valid_extensions = ['.wav', '.mp3', '.ogg', '.flac', '.m4a', '.webm']
    ext = Path(file_path).suffix.lower()
    
    if ext not in valid_extensions:
        return False, f"Unsupported audio format: {ext}. Supported: {', '.join(valid_extensions)}"
    
    # Check file size (max 100MB)
    max_size = 100 * 1024 * 1024  # 100MB
    file_size = os.path.getsize(file_path)
    
    if file_size > max_size:
        return False, f"File too large: {file_size / 1024 / 1024:.2f}MB (max 100MB)"
    
    if file_size == 0:
        return False, "File is empty"
    
    return True, None


def get_audio_duration(file_path: str) -> Optional[float]:
    """
    Get audio file duration in seconds
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Duration in seconds or None if error
    """
    try:
        import soundfile as sf
        info = sf.info(file_path)
        return info.duration
    except Exception as e:
        print(f"Error getting audio duration: {e}")
        return None


def convert_audio_format(
    input_path: str,
    output_path: str,
    target_format: str = "wav",
    sample_rate: int = 16000
) -> Tuple[bool, Optional[str]]:
    """
    Convert audio to target format
    
    Args:
        input_path: Input audio file path
        output_path: Output audio file path
        target_format: Target format (wav, mp3, etc.)
        sample_rate: Target sample rate
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        from pydub import AudioSegment
        
        # Load audio
        audio = AudioSegment.from_file(input_path)
        
        # Resample if needed
        if audio.frame_rate != sample_rate:
            audio = audio.set_frame_rate(sample_rate)
        
        # Export to target format
        audio.export(output_path, format=target_format)
        
        return True, None
        
    except Exception as e:
        return False, str(e)


def normalize_audio(input_path: str, output_path: str) -> Tuple[bool, Optional[str]]:
    """
    Normalize audio volume
    
    Args:
        input_path: Input audio file path
        output_path: Output audio file path
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        from pydub import AudioSegment
        from pydub.effects import normalize
        
        # Load and normalize
        audio = AudioSegment.from_file(input_path)
        normalized = normalize(audio)
        
        # Export
        normalized.export(output_path, format="wav")
        
        return True, None
        
    except Exception as e:
        return False, str(e)


def split_audio_chunks(
    file_path: str,
    chunk_duration: int = 30,
    output_dir: Optional[str] = None
) -> list:
    """
    Split audio into chunks
    
    Args:
        file_path: Input audio file path
        chunk_duration: Chunk duration in seconds
        output_dir: Output directory for chunks
        
    Returns:
        List of chunk file paths
    """
    try:
        from pydub import AudioSegment
        
        if output_dir is None:
            output_dir = os.path.dirname(file_path)
        
        # Load audio
        audio = AudioSegment.from_file(file_path)
        
        # Calculate chunks
        chunk_length_ms = chunk_duration * 1000
        chunks = []
        
        for i, start_ms in enumerate(range(0, len(audio), chunk_length_ms)):
            chunk = audio[start_ms:start_ms + chunk_length_ms]
            
            # Export chunk
            chunk_path = os.path.join(
                output_dir,
                f"{Path(file_path).stem}_chunk_{i}.wav"
            )
            chunk.export(chunk_path, format="wav")
            chunks.append(chunk_path)
        
        return chunks
        
    except Exception as e:
        print(f"Error splitting audio: {e}")
        return []
