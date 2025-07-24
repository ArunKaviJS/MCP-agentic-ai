import os
from pathlib import Path
from dotenv import load_dotenv
from livekit.plugins import openai

# === Load environment variables ===
ROOT_DIR = Path(__file__).resolve().parent.parent
dotenv_path = ROOT_DIR / "AcessTokens" / "env.ragu"
print(f"🔑 Loading environment from {dotenv_path}")
load_dotenv(dotenv_path)

# === Set up Realtime LLM ===
llm = openai.realtime.RealtimeModel.with_azure(
    azure_deployment=os.getenv("VOICE_LLM_DEPLOYMENT"),
    azure_endpoint=os.getenv("VOICE_LLM_ENDPOINT"),
    api_key=os.getenv("VOICE_LLM_API_KEY"),
    api_version=os.getenv("VOICE_LLM_API_VERSION"),
)

# === Prompt for intent classification ===
INTENT_SYSTEM_PROMPT = """
Classify the user query into one of the following topics:
- hostel
- transport
- placement
- admissions
- general

Only respond with a single label from: hostel, transport, placement, admissions, general.
Do not explain or add anything else.
"""

# === Intent classifier function ===
async def classify_intent(message: str) -> str:
    try:
        result = await llm.complete(
            prompt=message,
            system=INTENT_SYSTEM_PROMPT,
        )
        intent = result.text.strip().lower()
        print(f"[Classifier] ➜ User query: '{message}' → Intent: '{intent}'")

        if intent in {"hostel", "transport", "placement", "admissions", "general"}:
            return intent
        else:
            print("⚠️ Unknown intent. Defaulting to 'general'.")
            return "general"
    except Exception as e:
        print(f"❌ classify_intent error: {e}")
        return "general"
