# === main.py ===
import os
from livekit.agents import cli, AgentSession, AutoSubscribe, JobContext
from livekit import rtc
from livekit.agents.worker import WorkerOptions
from localllm.agents.base_agent import MainAgent
from localllm.agents.mcp import MultiAgentController

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()

    phone_number = participant.attributes.get("sip.phoneNumber", "unknown")
    mcp = MultiAgentController(entrypoint_fnc=entrypoint)

    session = AgentSession()
    await session.start(
        agent=MainAgent(phone_number=phone_number, mcp=mcp),
        room=ctx.room
    )

if __name__ == "__main__":
    cli.run_app(WorkerOptions(agent_name="localvoice", entrypoint_fnc=entrypoint))
