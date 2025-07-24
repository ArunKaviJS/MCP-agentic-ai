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

TRANSPORT_PROMPT = """
You are Priya, a college transport support agent at Vivekanandha College of Engineering for Women, Tiruchengode.

🚌 You are responsible for answering all transport-related queries, such as:
- Bus routes and stops
- Pickup and drop timing
- Bus pass or ID requirements
- Safety and attendance tracking
- Fee structure for transportation
- Emergency transport availability

If the user asks something outside of transport, you must switch to the right agent:
- 🎓 For admissions, courses, fees → switch to `AdmissionsAgent`
- 🛏️ For hostel facilities → switch to `HostelAgent`
- 💼 For placements → switch to `PlacementAgent`
- 🏛️ For general questions → switch to `GeneralAgent`

⚠️ Do not answer beyond your transport domain. Be precise and fact-based.
"""

class TransportAgent(Agent):
    def __init__(self, initial_question=None, memory=None):
        self.initial_question = initial_question
        self.memory = memory or {}
        super().__init__(
            instructions=TRANSPORT_PROMPT,
            llm=openai.realtime.RealtimeModel.with_azure(
                azure_deployment=os.getenv("VOICE_LLM_DEPLOYMENT"),
                azure_endpoint=os.getenv("VOICE_LLM_ENDPOINT"),
                api_key=os.getenv("VOICE_LLM_API_KEY"),
                api_version=os.getenv("VOICE_LLM_API_VERSION"),
            ),
        )

    async def on_enter(self):
        print("🚌 TransportAgent activated.")
        if self.initial_question:
            await self.on_message(self.initial_question)
        else:
            await self.session.send(
                "Hi! I can help you with transport details like routes, timings, and bus fees. What would you like to know?"
            )

    async def on_message(self, message: str) -> None:
        intent = await classify_intent(message)
        print(f"🧠 TransportAgent: classified intent as {intent}")

        if intent == "admissions":
            from agents.admissions_agent import AdmissionsAgent
            await self.session.switch_to(AdmissionsAgent(initial_question=message, memory=self.memory))

        elif intent == "hostel":
            from agents.hostel_agent import HostelAgent
            await self.session.switch_to(HostelAgent(initial_question=message, memory=self.memory))

        elif intent == "placement":
            from agents.placement_agent import PlacementAgent
            await self.session.switch_to(PlacementAgent(initial_question=message, memory=self.memory))

        elif intent == "general":
            from agents.general_agent import GeneralAgent
            await self.session.switch_to(GeneralAgent(initial_question=message, memory=self.memory))

        elif intent == "transport":
            result = await query_document(message)
            await self.session.send(result)

        else:
            await self.session.send(
                "Please ask transport-related questions like bus routes, stops, or timing. For other topics, I’ll transfer you to the right expert."
            )
