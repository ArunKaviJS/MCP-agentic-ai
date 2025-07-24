# agents/mcp.py

import os
from livekit.agents import Agent, AgentSession
from tools.classify import classify_intent
from tools.query import query_document

from agents.admissions_agent import AdmissionsAgent
from agents.placement_agent import PlacementAgent
from agents.transport_agent import TransportAgent
from agents.hostel_agent import HostelAgent
from agents.general_agent import GeneralAgent

class MultiAgentController:
    def __init__(self, entrypoint_fnc=None):
        self.entrypoint = entrypoint_fnc
        self.shared_memory = {}
        print("🧠 MCP initialized with shared memory.")

    async def handle_message(self, session, message: str):
        intent = await classify_intent(message)
        print(f"[MCP] 🧭 Intent: {intent}")

        self.shared_memory["last_user_message"] = message
        self.shared_memory["last_intent"] = intent

        if intent == "hostel":
            await session.switch_to(HostelAgent(initial_question=message, memory=self.shared_memory))
        elif intent == "transport":
            await session.switch_to(TransportAgent(initial_question=message, memory=self.shared_memory))
        elif intent == "placement":
            await session.switch_to(PlacementAgent(initial_question=message, memory=self.shared_memory))
        elif intent == "admissions":
            await session.switch_to(AdmissionsAgent(initial_question=message, memory=self.shared_memory))
        else:
            print(f"[MCP] 🤷 Unknown intent: '{intent}'. Using general document query.")
            response = await query_document(message)
            await session.send(response)
