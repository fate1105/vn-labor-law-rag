"""
Package Multi-Agent System (War Room Architecture)
"""
from src.agents.war_room import WarRoomOrchestrator, WarRoomResult, AgentOutput
from src.agents.prompts import (
    AGENT_2_SOLUTION_PROMPT,
    AGENT_3_CRITIQUE_PROMPT,
    AGENT_4_DRAFTING_PROMPT,
    AGENT_5_EVALUATION_PROMPT,
)

__all__ = [
    "WarRoomOrchestrator",
    "WarRoomResult",
    "AgentOutput",
    "AGENT_2_SOLUTION_PROMPT",
    "AGENT_3_CRITIQUE_PROMPT",
    "AGENT_4_DRAFTING_PROMPT",
    "AGENT_5_EVALUATION_PROMPT",
]

