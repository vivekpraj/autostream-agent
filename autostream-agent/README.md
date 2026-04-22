# AutoStream Conversational AI Agent

A conversational AI sales assistant for AutoStream, a fictional SaaS video editing tool. Built with LangGraph, LangChain, and Google Gemini.

---

## What It Does

This agent works like a smart sales assistant on chat. It can:
- Answer questions about plans, pricing, and policies using a knowledge base (RAG)
- Detect when a user is ready to buy (intent detection)
- Collect lead details conversationally — name, email, platform — one at a time
- Save the lead once all details are collected (mock CRM tool)

---

## Folder Structure

```
autostream-agent/
├── knowledge_base/
│   └── autostream_kb.json       # Pricing, features, policies
├── agent/
│   ├── state.py                 # Conversation memory
│   ├── nodes.py                 # Logic blocks (greeting, RAG, lead collection)
│   ├── graph.py                 # Conversation flow
│   └── tools.py                 # Mock lead capture function
├── rag/
│   └── retriever.py             # Searches knowledge base
├── main.py                      # Entry point
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Setup Instructions

**Step 1 — Clone the repo**
```bash
git clone https://github.com/your-username/autostream-agent.git
cd autostream-agent
```

**Step 2 — Create and activate virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**Step 3 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 4 — Add your API key**
```bash
cp .env.example .env
```
Open `.env` and replace `your_gemini_api_key_here` with your actual key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

**Step 5 — Run**
```bash
python main.py
```

---

## Sample Conversation

```
You: Hi there!
Agent: Hello! Welcome to AutoStream. How can I help you today?

You: What plans do you offer?
Agent: AutoStream offers two plans — Basic ($29/month) and Pro ($79/month)...

You: I want to sign up for the Pro plan
Agent: I'd love to help! May I know your name?

You: Rahul
Agent: Nice to meet you, Rahul! What's your email address?

You: rahul@gmail.com
Agent: Got it! Which platform do you create content for?

You: YouTube
Agent: You're all set, Rahul! Our team will reach out to rahul@gmail.com shortly.
```

---

## Architecture

We chose **LangGraph** over a simple LangChain AgentExecutor because LangGraph gives explicit, visual control over the conversation flow. Each step of the conversation — intent detection, RAG retrieval, lead collection, and tool execution — is a separate node in a directed graph. This makes the agent easier to debug, test, and extend.

**State management** is handled via LangGraph's `StateGraph` with a typed state dictionary that persists across all conversation turns. The state stores the full message history, the detected intent, a `collecting_lead` flag, and progressively collected lead data (name, email, platform). This ensures the agent never forgets what was said earlier in the conversation.

**RAG** is implemented using a local JSON knowledge base. The entire knowledge base is passed to the LLM as context on every INQUIRY — preventing hallucination of pricing or policy information. This approach is simple and accurate for a small knowledge base.

**Intent detection** uses the LLM itself with a structured classification prompt, making it robust to varied phrasing. **Tool execution** (lead capture) is triggered only after all three required fields are confirmed in state, ensuring the mock API is never called prematurely.

---

## WhatsApp Deployment

To deploy this agent on WhatsApp:

1. **Use Twilio or Meta's WhatsApp Business API** — these services act as a bridge between WhatsApp and your Python code. When a user messages your WhatsApp number, Twilio/Meta receives it and forwards it to your app.

2. **Set up a Webhook URL** — a webhook is simply a URL you create and give to Twilio/Meta. Every time a user sends a message, Twilio/Meta automatically calls that URL with the message content. Your app receives it, processes it through the LangGraph agent, and sends the reply back.

3. **Session management** — each WhatsApp user has a unique phone number. This is used as a session ID so every user gets their own isolated state and conversation. User A and User B never interfere with each other.

4. **Deployment** — host your app on Railway or Render (free tier) to get a public HTTPS URL. Register that URL as your webhook in the Twilio or Meta console. The core agent code — `nodes.py`, `graph.py`, `state.py` — stays completely unchanged.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| LangGraph | Conversation flow and state management |
| LangChain | LLM integration |
| Google Gemini | Language model |
| Python dotenv | Environment variable management |

---


