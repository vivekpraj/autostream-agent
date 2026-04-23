from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from agent.state import AgentState
from agent.tools import mock_lead_capture
from rag.retriever import retrieve
from pydantic import BaseModel, EmailStr, ValidationError

class EmailValidator(BaseModel):
    email: EmailStr

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

def get_last_user_message(messages):
    for m in reversed(messages):
        if m["role"] == "user":
            return m["content"]
    return ""

def get_last_assistant_message(messages):
    for m in reversed(messages):
        if m["role"] == "assistant":
            return m["content"]
    return ""

def intent_detector_node(state: AgentState) -> dict:
    last_message = get_last_user_message(state["messages"])

    prompt = f"""Classify the following user message into exactly one of these three categories:
GREETING - if the user is saying hello or starting a conversation
INQUIRY - if the user is asking about features, pricing, or policies
HIGH_INTENT - if the user wants to sign up, buy, or get started

Reply with only one word: GREETING, INQUIRY, or HIGH_INTENT

User message: {last_message}"""

    try:
        response = llm.invoke(prompt)
        intent = response.content.strip().upper()
        if intent not in ["GREETING", "INQUIRY", "HIGH_INTENT"]:
            intent = "INQUIRY"
    except Exception:
        intent = "INQUIRY"

    return {"intent": intent}


def greeting_node(state: AgentState) -> dict:
    last_message = get_last_user_message(state["messages"])

    prompt = f"""You are a friendly sales assistant for AutoStream, a SaaS video editing tool.
Respond warmly and naturally to this greeting. Keep it short and ask how you can help.

User said: {last_message}"""

    try:
        response = llm.invoke(prompt)
        reply = response.content
    except Exception:
        reply = "Hello! Welcome to AutoStream. How can I help you today?"

    updated_messages = state["messages"] + [
        {"role": "assistant", "content": reply}
    ]

    return {"messages": updated_messages}


def rag_node(state: AgentState) -> dict:
    last_message = get_last_user_message(state["messages"])
    context = retrieve(last_message)

    prompt = f"""You are a sales assistant for AutoStream, a SaaS video editing tool.
Using ONLY the information provided below, answer the user's question directly and concisely.
Answer only what was specifically asked. Do not dump all available information.
Do not add any information that is not present in the context.
If the question is not covered in the context, say you don't have that information.

Context: {context}

User question: {last_message}"""

    history = state["messages"][-5:]
    formatted = ""
    for m in history:
        role = "User" if m["role"] == "user" else "Agent"
        formatted += f"{role}: {m['content']}\n"

    prompt = f"""You are a sales assistant for AutoStream, a SaaS video editing tool.
Using ONLY the information provided below, answer the user's question directly and concisely.
Answer only what was specifically asked. Do not dump all available information.
Do not add any information that is not present in the context.
If the question is not covered in the context, say you don't have that information.

Recent conversation:
{formatted}

Context: {context}

User question: {last_message}"""

    try:
        response = llm.invoke(prompt)
        reply = response.content
    except Exception:
        reply = "I'm having trouble right now. Please try again in a moment."

    updated_messages = state["messages"] + [
        {"role": "assistant", "content": reply}
    ]

    return {"messages": updated_messages}


def lead_collection_node(state: AgentState) -> dict:
    last_message = get_last_user_message(state["messages"])
    last_assistant = get_last_assistant_message(state["messages"])

    # Step 1: collect name
    if state["lead_name"] is None:
        if last_assistant and "name" in last_assistant.lower():
            name = last_message
            updated_messages = state["messages"] + [
                {"role": "assistant", "content": f"Nice to meet you, {name}! What's your email address?"}
            ]
            return {"lead_name": name, "messages": updated_messages}
        else:
            updated_messages = state["messages"] + [
                {"role": "assistant", "content": "I'd love to help you get started with AutoStream! May I know your name?"}
            ]
            return {"collecting_lead": True, "messages": updated_messages}

    # Step 2: collect email
    elif state["lead_email"] is None:
        try:
            EmailValidator(email=last_message)
            updated_messages = state["messages"] + [
                {"role": "assistant", "content": "Got it! Which platform do you primarily create content for? (e.g. YouTube, Instagram, TikTok)"}
            ]
            return {"lead_email": last_message, "messages": updated_messages}
        except ValidationError:
            updated_messages = state["messages"] + [
                {"role": "assistant", "content": "That doesn't look like a valid email. Could you please enter a valid email address?"}
            ]
            return {"messages": updated_messages}

    # Step 3: collect platform
    elif state["lead_platform"] is None:
        platform = last_message
        updated_messages = state["messages"] + [
            {"role": "assistant", "content": "Perfect! Let me get you all set up..."}
        ]
        return {"lead_platform": platform, "messages": updated_messages}

    return {}


def lead_capture_node(state: AgentState) -> dict:
    mock_lead_capture(state["lead_name"], state["lead_email"], state["lead_platform"])

    confirmation = f"You're all set, {state['lead_name']}! Our team will reach out to {state['lead_email']} shortly. Welcome to AutoStream!"

    updated_messages = state["messages"] + [
        {"role": "assistant", "content": confirmation}
    ]

    return {"lead_captured": True, "messages": updated_messages}
