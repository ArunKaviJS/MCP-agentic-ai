from livekit.agents import Agent, ChatMessage
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

HOSTEL_PROMPT = """
You are Priya, an expert in hostel-related queries at Vivekanandha College of Engineering for Women, Tiruchengode.

🎯 You should mainly handle questions related to:
- Hostel facilities, accommodation types, and fees
- Room sharing, amenities, mess food, safety, curfew
- Hostel rules and regulations

If the student asks about other topics, trigger the correct agent:

- 🎓 For **admissions, courses, cutoffs, eligibility**, or **how to apply**, switch to `AdmissionsAgent`
- 💰 For **college fees or scholarships**, switch to `AdmissionsAgent`
- 💼 For **placements, company visits, job opportunities**, switch to `PlacementAgent`
- 🚌 For **college transport facilities**, switch to `TransportAgent`
- 🏛️ For **general campus or department info**, switch to `GeneralAgent`

❗Do not answer questions outside hostel topics yourself. Let the correct expert agent handle it.

Use friendly, helpful, and concise answers for hostel-related questions only.
"""

class HostelAgent(Agent):
    def __init__(self, initial_question=None, memory=None):
        self.initial_question = initial_question
        self.memory = memory or {}
        super().__init__(
            instructions=HOSTEL_PROMPT,
            llm=openai.realtime.RealtimeModel.with_azure(
                azure_deployment=os.getenv("VOICE_LLM_DEPLOYMENT"),
                azure_endpoint=os.getenv("VOICE_LLM_ENDPOINT"),
                api_key=os.getenv("VOICE_LLM_API_KEY"),
                api_version=os.getenv("VOICE_LLM_API_VERSION"),
            ),
        )

    async def on_enter(self):
        print("🏠 HostelAgent activated.")
        if self.initial_question:
            await self.on_message(self.initial_question)
        else:
            await self.session.send("Sure, I'm here to help you with hostel-related queries!")

    async def on_message(self, message: str) -> None:
        intent = await classify_intent(message)
        print(f"🧠 HostelAgent: classified intent as {intent}")

        if intent == "placement":
            from agents.placement_agent import PlacementAgent
            await self.session.switch_to(PlacementAgent(initial_question=message, memory=self.memory))

        elif intent == "transport":
            from agents.transport_agent import TransportAgent
            await self.session.switch_to(TransportAgent(initial_question=message, memory=self.memory))

        elif intent == "admissions":
            from agents.admissions_agent import AdmissionsAgent
            await self.session.switch_to(AdmissionsAgent(initial_question=message, memory=self.memory))

        elif intent == "general":
            from agents.general_agent import GeneralAgent
            await self.session.switch_to(GeneralAgent(initial_question=message, memory=self.memory))

        elif intent == "hostel":
            result = await query_document(message)
            await self.session.send(result)

        else:
            await self.session.send("Please ask hostel-related questions like rooms, fees, or rules. For other topics, I’ll transfer you to the right expert.")
