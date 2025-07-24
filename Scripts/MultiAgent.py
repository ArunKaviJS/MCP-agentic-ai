import os
import sys
from pathlib import Path
from datetime import datetime
import pytz

from dotenv import load_dotenv
from livekit.agents import AgentSession, AutoSubscribe, JobContext, WorkerOptions, cli
from livekit import rtc

# Set up project root and load .env
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

dotenv_path = ROOT_DIR / "AcessTokens" / "env.ragu"
print(f"🔑 Loading environment from {dotenv_path}")

if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    print("⚠️ .env file not found! Please check the path.")

# === Import custom agents and controller ===
from agents.main_agent import MainAgent
from agents.mcp import MultiAgentController

# Optional: Set timezone
india = pytz.timezone("Asia/Kolkata")

# === Entrypoint function ===
async def entrypoint(ctx: JobContext):
    print("🔌 Connecting to LiveKit...")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    print("🔗 Connected. Waiting for participant...")

    participant = await ctx.wait_for_participant()
    print(f"✅ Participant joined: {participant.identity} ({participant.kind})")

    # Extract phone number if SIP (else fallback to test user)
    if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
        phone_number = participant.attributes.get("sip.phoneNumber", "unknown")
    else:
        phone_number = "test-user"

    print(f"📞 Phone number: {phone_number}")
    print("🚀 Starting agent session...")

    session = AgentSession()
    await session.start(
        agent=MainAgent(phone_number=phone_number),
        room=ctx.room
    )

    print("✅ Agent session started.")

# === Launch LiveKit Worker ===
if __name__ == "__main__":
    controller = MultiAgentController(entrypoint_fnc=entrypoint)
    cli.run_app(
        WorkerOptions(
            agent_name="devserver",  # Agent name used in LiveKit dashboard
            entrypoint_fnc=entrypoint
        )
    )
