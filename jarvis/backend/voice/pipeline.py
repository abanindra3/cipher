from __future__ import annotations

from pathlib import Path

from jarvis.backend.ai import AssistantEngine
from jarvis.backend.voice.audio_io import MicrophoneRecorder
from jarvis.backend.voice.stt import SpeechToText
from jarvis.backend.voice.tts import TextToSpeech


class VoicePipeline:
    def __init__(self) -> None:
        self.recorder = MicrophoneRecorder()
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.engine = AssistantEngine()

    def capture_respond_speak(self, conversation_id: int | None = None) -> dict:
        audio = self.recorder.record_command()
        return self.process_audio(audio, conversation_id)

    def process_audio(self, audio: Path, conversation_id: int | None = None) -> dict:
        text = self.stt.transcribe(audio)
        if not text:
            text = self.recorder.recognize_local_text()
        result = self.engine.respond(text, conversation_id)
        self.tts.speak(result.text)
        return {
            "conversation_id": result.conversation_id,
            "transcript": text,
            "response": result.text,
            "tools": result.tool_results,
        }
