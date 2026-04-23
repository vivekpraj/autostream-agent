from langgraph.graph import StateGraph, START, END
from agent.state import AgentState
from agent.nodes import (
    intent_detector_node,
    greeting_node,
    rag_node,
    lead_collection_node,
    lead_capture_node
)


def route_after_intent(state: AgentState) -> str:
    # if lead collection is in progress, always route there regardless of intent
    if state.get("collecting_lead") and not state.get("lead_captured"):
        return "lead_collection_node"

    # route by intent
    intent = state.get("intent", "INQUIRY")
    if intent == "GREETING":
        return "greeting_node"
    elif intent == "HIGH_INTENT":
        return "lead_collection_node"
    else:
        return "rag_node"


def route_after_collection(state: AgentState) -> str:
    if state["lead_name"] and state["lead_email"] and state["lead_platform"] and not state["lead_captured"]:
        return "lead_capture_node"
    return END


def build_graph():
    graph = StateGraph(AgentState)

    # add all nodes
    graph.add_node("intent_detector_node", intent_detector_node)
    graph.add_node("greeting_node", greeting_node)
    graph.add_node("rag_node", rag_node)
    graph.add_node("lead_collection_node", lead_collection_node)
    graph.add_node("lead_capture_node", lead_capture_node)

    # entry point — always start here
    graph.add_edge(START, "intent_detector_node")

    # conditional routing after intent detection
    graph.add_conditional_edges("intent_detector_node", route_after_intent)

    # all nodes end the graph after running
    graph.add_edge("greeting_node", END)
    graph.add_edge("rag_node", END)
    graph.add_edge("lead_capture_node", END)

    # after lead_collection, check if all 3 collected → go to lead_capture immediately
    graph.add_conditional_edges("lead_collection_node", route_after_collection)

    return graph.compile()
