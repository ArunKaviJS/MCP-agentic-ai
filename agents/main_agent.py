# agents/main_agent.py

import os
from livekit.agents import Agent
from livekit.plugins import openai
from tools.query import query_document
from tools.classify import classify_intent

# Import all expert agents to be routed via MCP
from agents.hostel_agent import HostelAgent     # 🛏️
from agents.general_agent import GeneralAgent   # 📚 fallback
from agents.admissions_agent import AdmissionsAgent  # 🎓
from agents.placement_agent import PlacementAgent     # 💼
from agents.transport_agent import TransportAgent     # 🚌

import os
from pathlib import Path
from dotenv import load_dotenv
ROOT_DIR = Path(__file__).resolve().parent.parent
dotenv_path = ROOT_DIR / "AcessTokens" / "env.ragu"
print(f"🔑 Loading environment from {dotenv_path}")
load_dotenv(dotenv_path)


MAIN_PROMPT = """
Hello! I'm Priya, your virtual assistant from Vivekanandha College of Engineering for Women, Tiruchengode.

I can help you with:
🎓 Admissions – eligibility, courses, cut-offs, how to apply  
🛏️ Hostel – accommodation, rules, and facilities  
💼 Placements – company visits, training, and job offers  
🚌 Transport – bus routes, timings, and locations  
💰 Fees & quotas – government/management quota & scholarships  
🏛️ Departments and general college info

Once you ask a question, I will pass it to the right handler function:

- For hostel queries → `handle_hostel()`
- For admissions → `handle_admissions()`
- For transport → `handle_transport()`
- For placement → `handle_placement()`
- For anything else → `handle_general()` (calls `query_document()`)

Only college-related queries are handled.
"""

# Handler functions
async def handle_hostel(message, session):
    await session.switch_to(HostelAgent(initial_question=message))

async def handle_admissions(message, session):
    await session.switch_to(AdmissionsAgent(initial_question=message))

async def handle_transport(message, session):
    await session.switch_to(TransportAgent(initial_question=message))

async def handle_placement(message, session):
    await session.switch_to(PlacementAgent(initial_question=message))

async def handle_general(message, session):
    result = await query_document(message)
    await session.send(result)

class MainAgent(Agent):
    def __init__(self, phone_number=None):
        super().__init__(
            instructions=MAIN_PROMPT,
            llm=openai.realtime.RealtimeModel.with_azure(
                azure_deployment=os.getenv("VOICE_LLM_DEPLOYMENT"),
                azure_endpoint=os.getenv("VOICE_LLM_ENDPOINT"),
                api_key=os.getenv("VOICE_LLM_API_KEY"),
                api_version=os.getenv("VOICE_LLM_API_VERSION"),
            ),
        )
        self.phone_number = phone_number

    async def on_enter(self):
        print("🟢 MainAgent activated.")
        await self.send(
            "வணக்கம்! நான் Priya, Vivekanandha College of Engineering for Women, Tiruchengode-ல இருந்து பேசுறேன். "
            "Shall we continue in English or Tamil?"
        )

    async def on_message(self, message: str):
        print(f"📥 MainAgent received message: {message}")
        intent = await classify_intent(message)
        print(f"🧠 MainAgent classified intent as: {intent}")

        if intent == "hostel":
            await self.switch_to(HostelAgent(initial_question=message))

        elif intent == "admissions":
            await self.switch_to(AdmissionsAgent(initial_question=message))

        elif intent == "transport":
            await self.switch_to(TransportAgent(initial_question=message))

        elif intent == "placement":
            await self.switch_to(PlacementAgent(initial_question=message))

        elif intent == "general":
            await self.switch_to(GeneralAgent(initial_question=message))

        else:
            await self.send("I'm sorry, I couldn't understand your request. Could you please repeat it?")