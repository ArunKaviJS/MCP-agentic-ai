# === agents/mcp.py ===

from sub_agents.hosel_agent import HostelAgent
from classify import classify_intent

class MultiAgentController:
    def __init__(self, entrypoint_fnc):
        self.entrypoint_fnc = entrypoint_fnc  # Entry agent function if needed

    async def handle_message(self, session, message: str):
        # 1. Classify user query
        intent = await classify_intent(message)
        print(f"🔍 Intent identified as: {intent}")

        # 2. Select appropriate agent class
        agent_cls = {
            "hostel": HostelAgent,
            # "transport": TransportAgent,
            # "admissions": AdmissionsAgent,
            # "placement": PlacementAgent,
            # "general": GeneralAgent,
        }.get(intent, HostelAgent)  # default fallback agent

        # 3. Instantiate and route to sub-agent
        new_agent = agent_cls(initial_question=message, memory={})
        print(f"📦 Switching to agent: {agent_cls.__name__}")
        await session.transfer(new_agent)
