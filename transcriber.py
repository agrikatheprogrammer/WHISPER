from typing import Union
import ffmpeg
import numpy as np
import requests
import torch
import whisper
from yt_dlp import YoutubeDL
from transformers import pipeline
from config import LOCAL_DIR
import mimetypes
from pathlib import Path
import ssl
import pytube.request

# Bypass SSL verification (for debugging purposes)
ssl._create_default_https_context = ssl._create_unverified_context
pytube.request.default_ssl_context = ssl._create_unverified_context()

def validate_audio_file(file_path: Path) -> bool:
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type and mime_type.startswith("audio")

class Transcription:
    def __init__(self, name: str, source: Union[str, bytes], source_type: str, start: float, duration: float):
        self.name = name
        self.source = source
        self.source_type = source_type
        self.transcribed = False
        self.summarized = False

        # Create a save directory
        self.save_dir = LOCAL_DIR / self.name
        if not self.save_dir.exists():
            self.save_dir.mkdir(parents=True, exist_ok=True)

        # Handle different source types
        if self.source_type == "youtube" or self.source_type == "link":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(self.save_dir / 'audio.%(ext)s'),
            }
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.source, download=True)
                audio_file_path = Path(ydl.prepare_filename(info_dict))

            print(f"Downloaded file: {audio_file_path}")
            print(f"File size: {audio_file_path.stat().st_size} bytes")

        elif self.source_type == "file":
            audio_file_path = self.save_dir / "audio.mp3"
            with open(audio_file_path, "wb") as f:
                f.write(self.source.read())

            # Validate the uploaded file
            if not validate_audio_file(audio_file_path):
                raise ValueError(f"The uploaded file is not a valid audio file: {audio_file_path}")

        # Continue with trimming using FFmpeg
        try:
            if duration > 0:
                audio = ffmpeg.input(str(audio_file_path), ss=start, t=duration)
            else:
                audio = ffmpeg.input(str(audio_file_path), ss=start)

            self.og_audio_path = audio_file_path
            self.audio_path = self.save_dir / "audio_trimmed.mp4"

            audio = ffmpeg.output(audio, str(self.audio_path.resolve()), acodec="copy")
            ffmpeg.run(audio, overwrite_output=True)
        except ffmpeg.Error as e:
            if e.stderr:
                error_message = e.stderr.decode()
            else:
                error_message = "An unknown FFmpeg error occurred."
            print(f"FFmpeg error: {error_message}")
            raise

    def transcribe(self, whisper_model: str = "base"):
        # Load the Whisper model
        model = whisper.load_model(whisper_model)

        # Perform transcription with default settings
        print(f"Transcribing audio from {self.audio_path} using Whisper model '{whisper_model}'...")
        result = model.transcribe(str(self.audio_path.resolve()))

        # Store the results
        self.raw_output = result
        self.segments = result.get("segments", [])
        self.language = result.get("language", "unknown")

        # Aggregate the text from all segments
        self.text = " ".join(segment["text"] for segment in self.segments)

        # Mark transcription as complete
        self.transcribed = True

    def summarize(self):
        if not self.transcribed:
            raise ValueError("Transcription must be completed before summarization.")

        print("Summarizing transcription...")
        summarizer = pipeline("summarization")
        text = self.text  # Use the full transcribed text
        self.summary = summarizer(text)  # No additional arguments passed
        self.summarized = True
        print("Summarization completed.")
