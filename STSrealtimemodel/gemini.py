from pathlib import Path
import os
import sys
import logging
from dotenv import load_dotenv
from datetime import datetime
import pytz

# === LiveKit Imports ===
from livekit.agents import Agent, AgentSession, AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.plugins import google  # ✅ Google AI plugin

# === Timezone Configuration ===
india = pytz.timezone("Asia/Kolkata")

# === Set Environment Path ===
THIS_DIR = Path(__file__).parent
sys.path.insert(0, str(THIS_DIR))
dotenv_path = THIS_DIR / "AcessTokens" / "env.ragu"
print(f"🔑 Loading environment from {dotenv_path}")
load_dotenv(dotenv_path)

# === Logging Configuration ===
logger = logging.getLogger("voice-agent")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


# Optional: define your custom instructions
PROMPT_INSTRUCTIONS = """
You are a helpful voice-based AI assistant. Use the knowledge available to you to answer clearly and concisely.
"""

class RagAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="Repeat back whatever the user says.",
            llm=google.LLM(
                model="gemini-2.0-flash",
                api_key=os.getenv("GOOGLE_API_KEY"),
                project_id=os.getenv("GOOGLE_PROJECT_ID"),
                location=os.getenv("GOOGLE_LOCATION",)
            ),
            stt=google.STT(),
            tts=google.TTS(),
        )

    async def on_enter(self):
        self.session.generate_reply()

# === Entrypoint for LiveKit Job ===
async def entrypoint(ctx: JobContext):
    try:
        await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
        participant = await ctx.wait_for_participant()

        if participant.kind.name == "PARTICIPANT_KIND_SIP":
            phone_number = participant.attributes.get("sip.phoneNumber", "unknown")
            print(f"📞 SIP Caller phone number: {phone_number}")
        else:
            phone_number = "test-user"

        call_time = datetime.now(india).strftime("%Y-%m-%d %H:%M:%S")

        instructions = (
            "You are a helpful voice assistant. Answer user questions clearly and briefly."
        )

        session = AgentSession()
        await session.start(agent=RagAgent(instructions=instructions), room=ctx.room)

    except Exception as e:
        logger.exception(f"❌ Agent session failed: {e}")



# === Main Launcher ===
if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            agent_name="devserver",
            entrypoint_fnc=entrypoint,
        )
    )
