import os
from livekit.agents import Agent
from livekit.plugins import openai

from tools.query import query_document
from tools.classify import classify_intent

from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).resolve().parent.parent
dotenv_path = ROOT_DIR / "AcessTokens" / "env.ragu"
print(f"🔑 Loading environment from {dotenv_path}")
load_dotenv(dotenv_path)

PLACEMENT_PROMPT = """
You are Priya, a specialist in placements and career support at Vivekanandha College of Engineering for Women, Tiruchengode.

💼 You are responsible for answering all placement-related queries, such as:
- Companies visiting the campus
- Salary packages (average, highest, domain-wise)
- Departments with highest placements
- Internship support and training
- Placement percentage statistics
- Soft-skill and interview prep support

If the user asks something outside placements, hand over to the correct agent:
- 🎓 For admissions, courses, eligibility → switch to `AdmissionsAgent`
- 🛏️ For hostel facilities → switch to `HostelAgent`
- 🚌 For college transport → switch to `TransportAgent`
- 🏛️ For general campus queries → switch to `GeneralAgent`

⚠️ Do not attempt to answer outside placement domain yourself.
Only speak from reliable college-level information.
"""

class PlacementAgent(Agent):
    def __init__(self, initial_question=None, memory=None):
        self.initial_question = initial_question
        self.memory = memory or {}
        super().__init__(
            instructions=PLACEMENT_PROMPT,
            llm=openai.realtime.RealtimeModel.with_azure(
                azure_deployment=os.getenv("VOICE_LLM_DEPLOYMENT"),
                azure_endpoint=os.getenv("VOICE_LLM_ENDPOINT"),
                api_key=os.getenv("VOICE_LLM_API_KEY"),
                api_version=os.getenv("VOICE_LLM_API_VERSION"),
            ),
        )

    async def on_enter(self):
        print("💼 PlacementAgent activated.")
        if self.initial_question:
            await self.on_message(self.initial_question)
        else:
            await self.session.send(
                "I'm here to help with placements. You can ask about visiting companies, salaries, or training support!"
            )

    async def on_message(self, message: str) -> None:
        intent = await classify_intent(message)
        print(f"🧠 PlacementAgent: classified intent as {intent}")

        if intent == "admissions":
            from agents.admissions_agent import AdmissionsAgent
            await self.session.switch_to(AdmissionsAgent(initial_question=message, memory=self.memory))

        elif intent == "hostel":
            from agents.hostel_agent import HostelAgent
            await self.session.switch_to(HostelAgent(initial_question=message, memory=self.memory))

        elif intent == "transport":
            from agents.transport_agent import TransportAgent
            await self.session.switch_to(TransportAgent(initial_question=message, memory=self.memory))

        elif intent == "general":
            from agents.general_agent import GeneralAgent
            await self.session.switch_to(GeneralAgent(initial_question=message, memory=self.memory))

        elif intent == "placement":
            result = await query_document(message)
            await self.session.send(result)

        else:
            await self.session.send("Please ask about placements — companies, salary packages, or training support.")
