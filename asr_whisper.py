import os
import shutil
import whisper


def _ensure_ffmpeg_on_path() -> None:
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return
    ffbin = os.getenv("FFMPEG_BIN", "")
    ffdir = os.getenv("FFMPEG_DIR", "")
    candidates = []
    if ffbin:
        candidates.append(os.path.dirname(ffbin))
    if ffdir:
        candidates.append(ffdir)
    # Common manual install path on Windows
    candidates.append(r"C:\ffmpeg\bin")
    for d in candidates:
        if d and os.path.exists(os.path.join(d, "ffmpeg.exe")):
            os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
            break


def transcribe_audio(audio_path: str, model_size: str | None = None) -> str:
    """
    Transcribe a single audio file using Whisper. Returns plain text.
    """
    _ensure_ffmpeg_on_path()
    size = model_size or os.getenv("WHISPER_MODEL", "base")
    model = whisper.load_model(size)
    result = model.transcribe(audio_path)
    return result.get("text", "").strip()

