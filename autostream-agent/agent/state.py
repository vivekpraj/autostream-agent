from typing import TypedDict, Optional, List

class AgentState(TypedDict):
    messages: List[dict]
    intent: Optional[str]
    lead_name: Optional[str]
    lead_email: Optional[str]
    lead_platform: Optional[str]
    lead_captured: bool
    collecting_lead: bool
