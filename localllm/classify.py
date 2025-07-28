# === agents/classify.py ===

from llama_cpp import Llama
from faster_whisper import WhisperModel
from TTS.api import TTS
from pathlib import Path

# === Global Setup ===

# Load LLM (TinyLLaMA or similar)
LLM_MODEL_PATH = "models/tinyllama-1.1B-chat.Q4_K_M.gguf"
llm = Llama(model_path=LLM_MODEL_PATH, n_ctx=1024, n_threads=4)

# Load TTS
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")

# Load Whisper STT
stt_model = WhisperModel("base")

# === INTENT CLASSIFIER ===

INTENT_PROMPT = """
Classify the intent of this query:
- hostel
- transport
- placement
- admissions
- general
Reply only with one of the words above.
"""

async def classify_intent(message: str) -> str:
    full_prompt = f"{INTENT_PROMPT}\nQuery: {message}\nIntent:"
    response = llm(full_prompt, max_tokens=5, stop=["\n"])
    intent = response["choices"][0]["text"].strip().lower()
    print(f"🧠 Intent classified as: {intent}")
    return intent if intent in {"hostel", "transport", "placement", "admissions", "general"} else "general"

# === STT FUNCTION ===

def transcribe_audio(audio_path: str) -> str:
    segments, _ = stt_model.transcribe(audio_path)
    full_text = " ".join(segment.text for segment in segments)
    print(f"🗣️ Transcribed text: {full_text}")
    return full_text

# === TTS FUNCTION ===

def speak_text(text: str, output_path: str = "output.wav"):
    tts.tts_to_file(text=text, file_path=output_path)
    print(f"🔊 TTS audio saved to: {output_path}")
