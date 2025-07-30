import os
import sys
import logging
from datetime import datetime
from pathlib import Path
import pytz
from dotenv import load_dotenv
from typing import AsyncIterable

# === LiveKit Agent Imports ===
from livekit.agents import (
    Agent, AgentSession, JobContext, WorkerOptions,
    cli, AutoSubscribe
)
from livekit import rtc
from livekit.agents import (
    UserInputTranscribedEvent,
    ConversationItemAddedEvent
)
from livekit.agents.llm import AudioContent, ImageContent

# === Setup Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Load Environment File ===
india = pytz.timezone("Asia/Kolkata")
THIS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(THIS_DIR))
dotenv_path = THIS_DIR / "AcessTokens" / "env.ragu"
print(f"🔑 Loading environment from {dotenv_path}")
load_dotenv(dotenv_path)

# === Simple STT Agent ===
class WhisperSTTAgent(Agent):
    def __init__(self, instructions: str):
        super().__init__(instructions=instructions)

    async def on_enter(self):
        self.session.on("user_input_transcribed", self.handle_user_input_transcribed)
        self.session.on("conversation_item_added", self.handle_conversation_item_added)
        logger.info("🎤 WhisperSTTAgent is now listening...")

    async def transcription_node(
        self, text: AsyncIterable[str], model_settings=None, metadata=None
    ):
        async for chunk in text:
            print(f"[Partial Transcript] {chunk}")
            yield chunk

    def handle_user_input_transcribed(self, event: UserInputTranscribedEvent):
        if event.is_final:
            print(f"[✅ Final STT] {event.transcript}")

    def handle_conversation_item_added(self, event: ConversationItemAddedEvent):
        print(f"[Conversation] From {event.item.role}: {event.item.text_content}, Interrupted: {event.item.interrupted}")
        for content in event.item.content:
            if isinstance(content, str):
                print(f"  - Text: {content}")
            elif isinstance(content, ImageContent):
                print(f"  - Image: {content.image}")
            elif isinstance(content, AudioContent):
                print(f"  - Audio Frame: {content.frame} | Transcript: {content.transcript}")

# === Entrypoint ===
async def entrypoint(ctx: JobContext):
    try:
        await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

        participant = await ctx.wait_for_participant()
        if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
            phone_number = participant.attributes.get("sip.phoneNumber", "unknown")
        else:
            phone_number = "test-user"

        print(f"📞 Connected Participant: {phone_number}")

        # Instructions can be anything – Whisper-only agent doesn't respond
        instructions = "This agent only performs speech-to-text and prints transcripts. No response will be generated."

        session = AgentSession()
        await session.start(agent=WhisperSTTAgent(instructions=instructions), room=ctx.room)

    except Exception as e:
        logger.exception(f"❌ Agent session failed: {e}")

# === Main Launcher ===
if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            agent_name="devserver",
            entrypoint_fnc=entrypoint
        )
    )
