# === agents/main_agent.py ===

import os
import logging
from datetime import datetime
from pytz import timezone
from livekit.agents import Agent
from livekit.agents import UserInputTranscribedEvent, ConversationItemAddedEvent
from mcp import MultiAgentController

# === Timezone and Logging Setup ===
india = timezone("Asia/Kolkata")
logger_path = "conversation_logs/transcripts.csv"
os.makedirs(os.path.dirname(logger_path), exist_ok=True)

class CSVFormatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.now(india).strftime("%Y-%m-%d %H:%M:%S")
        msg = record.getMessage().replace(",", " ")
        return f"{timestamp},{msg}"

logger = logging.getLogger("voice_logger")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler(logger_path, mode="a")
    fh.setFormatter(CSVFormatter())
    logger.addHandler(fh)

# === Welcome Prompt ===
PROMPT = """
வணக்கம்! நான் Priya, Vivekanandha College of Engineering for Women, Tiruchengode-ல இருந்து பேசுறேன்.
Shall we continue in English or Tamil? / தமிழா?

I can help you with:
- admissions
- eligibility
- courses
- fees
- hostel
- placement
- transport
- departments
"""

# === Main Agent ===
class MainAgent(Agent):
    def __init__(self, phone_number: str, mcp: MultiAgentController):
        self.phone_number = phone_number
        self.mcp = mcp
        super().__init__(instructions=PROMPT)

    async def on_enter(self):
        await self.session.send(PROMPT)
        # Attach event listeners
        self.session.on("user_input_transcribed", self.handle_user_input_transcribed)
        self.session.on("conversation_item_added", self.handle_conversation_item_added)

    async def handle_user_input_transcribed(self, event: UserInputTranscribedEvent):
        if event.is_final:
            logger.info(f"user,final,{event.transcript}")
            await self.mcp.handle_message(self.session, event.transcript)

    async def handle_conversation_item_added(self, event: ConversationItemAddedEvent):
        for content in event.item.content:
            if isinstance(content, str):
                logger.info(f"agent,text,{content}")
