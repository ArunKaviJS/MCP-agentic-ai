import os
import logging
from datetime import datetime
from pytz import timezone
from livekit.agents import (
    Agent,
    AgentSession,
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,  # ✅ Required for aws.realtime
)
from livekit import rtc
from livekit.plugins import aws

# === Logger and timezone ===
logger = logging.getLogger("voice-agent")
logging.basicConfig(level=logging.INFO)
india = timezone("Asia/Kolkata")



# === Hardcoded assistant instructions ===
MANUAL_PROMPT = """
You are a helpful AI assistant who answers transport-related questions about Chennai.
Please respond politely in English and Tamil, depending on the user's query.
Be brief, supportive, and easy to understand.
"""

# === Voice Agent ===
class VoiceOnlyAgent(Agent):
    def __init__(self, instructions: str):
        super().__init__(instructions=instructions) 
        

    async def on_start(self, session: AgentSession):
        await session.say("Hello! I'm your AWS-powered assistant.")
        async for user_msg in session.listen():
            response = await session.ask(user_msg.text)
            await session.say(response.text)

# === Entrypoint ===
async def entrypoint(ctx: JobContext):
    try:
        await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
        participant = await ctx.wait_for_participant()

        # Log phone number if SIP
        if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
            phone_number = participant.attributes.get("sip.phoneNumber", "unknown")
            print(f"📞 Caller phone number: {phone_number}")
            call_time = datetime.now(india).strftime("%Y-%m-%d %H:%M:%S")
        else:
            phone_number = "test-user"

        # ✅ Start the agent session with AWS voice models
        session = AgentSession(
            agent=VoiceOnlyAgent(instructions=MANUAL_PROMPT),
            llm=aws.realtime.RealtimeModel(
                model="sonic-llama3-8b",
                tool_choice="auto",
                max_tokens=4096
            ),
            tts="aws/polly/neural",
            stt="aws/transcribe",
        )
        await session.start(room=ctx.room)

    except Exception as e:
        logger.exception(f"❌ Agent session failed: {e}")

# === CLI Entrypoint ===
if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            agent_name="devserver",
            entrypoint_fnc=entrypoint
        )
    )
