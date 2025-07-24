import os
from livekit.agents import Agent
from livekit.plugins import openai

from tools.query import query_document
from tools.classify import classify_intent




import os
from pathlib import Path
from dotenv import load_dotenv
ROOT_DIR = Path(__file__).resolve().parent.parent
dotenv_path = ROOT_DIR / "AcessTokens" / "env.ragu"
print(f"🔑 Loading environment from {dotenv_path}")
load_dotenv(dotenv_path)


GENERAL_PROMPT = """
You are Priya, an expert college assistant at Vivekanandha College of Engineering for Women, Tiruchengode.

You are responsible for general college-related questions such as:
- 🎓 List of departments and specializations
- 🏫 Campus location, infrastructure, labs, or facilities
- 🕐 College timings, holidays, working hours
- 📅 Academic calendar or events
- 💻 Online portal access, documents, etc.
- Any other questions that don’t fall under a specific category

However, if a user question matches a specific category, switch to the appropriate agent:
- 🏠 For hostel-related → `HostelAgent`
- 💼 For placements → `PlacementAgent`
- 🚌 For transport → `TransportAgent`
- 📚 For admissions, courses, fees → `AdmissionsAgent`

Do not answer topics outside your general domain.
"""

class GeneralAgent(Agent):
    def __init__(self, initial_question=None):
        self.initial_question = initial_question
        super().__init__(
            instructions=GENERAL_PROMPT,
            llm=openai.realtime.RealtimeModel.with_azure(
                azure_deployment=os.getenv("VOICE_LLM_DEPLOYMENT"),
                azure_endpoint=os.getenv("VOICE_LLM_ENDPOINT"),
                api_key=os.getenv("VOICE_LLM_API_KEY"),
                api_version=os.getenv("VOICE_LLM_API_VERSION"),
            ),
        )

    async def on_enter(self):
        print("🏛️ GeneralAgent activated.")
        if self.initial_question:
            await self.on_message(self.initial_question)
        else:
            await self.session.send(
                "I can help you with general information about our college like departments, location, and facilities. What would you like to know?"
            )

    
# ✅ Instead, inside on_message():
    async def on_message(self, message: str) -> None:
        if "hostel" in message.lower():
            from agents.hostel_agent import HostelAgent  # ✅ Lazy import here
            await self.session.switch_to(HostelAgent(initial_question=message))
        
        if "placement" in message.lower():
            from agents.placement_agent import PlacementAgent
            await self.session.switch_to(PlacementAgent(initial_question=message))

        if "transport" in message.lower():
            from agents.transport_agent import TransportAgent
            await self.session.switch_to(TransportAgent(initial_question=message))

        if "admissions" in message.lower():
            from agents.admissions_agent import AdmissionsAgent
            await self.session.switch_to(AdmissionsAgent(initial_question=message))
        


