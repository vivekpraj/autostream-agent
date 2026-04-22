# PRD: AutoStream Conversational AI Agent
### For: ServiceHive ML Intern Assignment | Built with Claude Code

---

> **How to use this PRD with Claude Code:**
> Tell Claude Code — *"Read this PRD fully. Do NOT write any code yet. Explain each file, each line, why it exists, what it does, and what alternatives exist. Wait for my confirmation before writing anything."*

---

## 0. Ground Rules for Claude Code

1. **Never write code directly.** For every file, first explain:
   - What this file does
   - Why we need it
   - How each important line works
   - What alternatives exist and why we chose this one
2. Wait for the user to say **"okay, write it"** before generating any code.
3. Use the **simplest possible language.** Assume the user is a fresher.
4. Every concept introduced must have a **real-world analogy.**

---

## 1. Project Summary

**What we're building:** A chatbot that works like a smart sales assistant for AutoStream (a fictional SaaS video editing tool). It can answer questions, understand when someone is ready to buy, collect their details conversationally, and save them as a lead.

**Think of it like this:** Imagine a human sales rep on Instagram DMs. They don't immediately ask "name? email? phone?" — they chat naturally, understand what you want, and only when you say "I want to buy" do they ask for your details. That's exactly what this agent does.

---

## 2. Folder Structure (Complete)

```
autostream-agent/
│
├── knowledge_base/
│   └── autostream_kb.json          # The "brain" — pricing, features, policies
│
├── agent/
│   ├── __init__.py                 # Makes this a Python package
│   ├── state.py                    # What the agent "remembers" at any point
│   ├── nodes.py                    # The actual logic blocks (greeting, RAG, lead capture)
│   ├── graph.py                    # The flow — which node runs after which
│   └── tools.py                    # The mock lead capture function
│
├── rag/
│   ├── __init__.py
│   └── retriever.py                # Searches the knowledge base and returns answers
│
├── main.py                         # Entry point — run this to start the chatbot
├── requirements.txt                # All Python libraries needed
├── .env                            # API keys (never commit this to GitHub)
├── .env.example                    # Template showing what keys are needed
├── .gitignore                      # Tells Git to ignore .env and other junk
└── README.md                       # Setup instructions + architecture explanation
```

### Why this structure?

Each folder has **one job**:
- `knowledge_base/` = data only, no logic
- `agent/` = brain of the agent
- `rag/` = search engine for the knowledge base
- Root files = configuration and entry point

This is called **Separation of Concerns** — a real-world engineering principle that makes code easier to debug, test, and understand.

---

## 3. What Each File Does (Plain English)

### 3.1 `knowledge_base/autostream_kb.json`
**What it is:** A JSON file containing all the facts the agent is allowed to answer from. Think of it as the agent's "employee handbook."

**Why JSON?** It's structured, human-readable, and easy to search programmatically. Alternative: Markdown file (simpler to write but harder to search programmatically).

**Contents it must have:**
- Basic Plan details ($29/month, 10 videos, 720p)
- Pro Plan details ($79/month, unlimited, 4K, AI captions)
- Refund policy (no refunds after 7 days)
- Support policy (24/7 only on Pro)

---

### 3.2 `agent/state.py`
**What it is:** A Python class (or TypedDict) that defines what the agent remembers at every step of the conversation.

**Real-world analogy:** A waiter's notepad. Every time a customer says something, the waiter writes it down. The notepad is the "state."

**What it tracks:**
- Full conversation history (list of messages)
- Detected intent (greeting / inquiry / high-intent)
- Lead info collected so far (name, email, platform)
- Whether lead has been captured (True/False)

**Why this matters:** Without state, the agent forgets everything after each message. State gives it memory.

**Alternative:** Using LangChain's built-in `ConversationBufferMemory` — but LangGraph's state is more explicit and easier to debug.

---

### 3.3 `rag/retriever.py`
**What it is:** The search function that looks through the knowledge base and returns the most relevant information for a user's question.

**Real-world analogy:** A librarian. You ask "what's the price of the Pro plan?" and the librarian goes to the shelf (JSON file), finds the relevant section, and hands it to you.

**How it works (step by step):**
1. User asks a question
2. The retriever converts the question into a search query
3. It scans the JSON knowledge base
4. It returns the matching chunk of text
5. That text is fed into the LLM as context

**Why RAG and not just asking the LLM directly?**
Without RAG, the LLM might hallucinate prices ("oh it's probably $50/month"). With RAG, it's forced to answer only from real data. This is critical for business accuracy.

**Alternative approaches:**
- Vector database (FAISS, ChromaDB) — better for large datasets, overkill here
- Simple keyword matching — what we'll use, simpler and sufficient for a small JSON

---

### 3.4 `agent/nodes.py`
**What it is:** Each "node" is a Python function that handles one specific job in the conversation.

**Real-world analogy:** Think of a call center with different departments. The routing system sends you to the right department. Each department (node) does one thing.

**Nodes we need:**

| Node Name | What it does |
|---|---|
| `greeting_node` | Responds to casual hellos |
| `rag_node` | Answers product/pricing questions using the knowledge base |
| `intent_detector_node` | Classifies the message as greeting / inquiry / high-intent |
| `lead_collection_node` | Asks for name → email → platform one by one |
| `lead_capture_node` | Calls the mock API once all three are collected |

**Why separate nodes?** Each node can be tested independently. If the RAG is wrong, you fix only `rag_node` without touching anything else.

---

### 3.5 `agent/graph.py`
**What it is:** This is where you define the **flow** — which node runs after which, and what conditions decide the path.

**Real-world analogy:** A flowchart. "If user says hi → go to greeting. If user asks about price → go to RAG. If user says they want to buy → go to lead collection."

**How LangGraph works:**
- You create a `StateGraph`
- You add nodes to it
- You add edges (arrows) between nodes
- Some edges are conditional (based on intent)
- You compile it and run it

**Why LangGraph over simple if-else?**
With complex agents, if-else chains become spaghetti. LangGraph gives you a visual, manageable flow that's easier to extend and debug.

**Alternative:** LangChain AgentExecutor — simpler but less control over flow. AutoGen — good for multi-agent scenarios, overkill here.

---

### 3.6 `agent/tools.py`
**What it is:** The mock lead capture function.

**What it does:** When called with name + email + platform, it prints a success message (simulating an API call to a CRM like HubSpot or Salesforce).

```
# What the output looks like:
Lead captured successfully: Rahul, rahul@gmail.com, YouTube
```

**Why mock?** In a real product, this would call a real CRM API. For this assignment, a print statement proves the tool was called correctly and at the right time.

**What makes this tricky:** The agent must NOT call this until it has collected ALL THREE pieces of info. This tests proper tool calling logic.

---

### 3.7 `main.py`
**What it is:** The entry point. Run `python main.py` and the chatbot starts in your terminal.

**What it does:**
1. Loads environment variables (API key)
2. Initializes the LangGraph
3. Starts a loop: user types → agent responds → repeat

---

### 3.8 `.env` and `.env.example`
**What it is:** `.env` holds secret API keys. `.env.example` is a safe template showing the structure without actual keys.

**Why never commit `.env` to GitHub?** API keys are like passwords. If pushed to GitHub, anyone can use your account and you'll get billed.

**.env.example should look like:**
```
ANTHROPIC_API_KEY=your_key_here
```

---

### 3.9 `requirements.txt`
**What it is:** A list of all Python libraries the project needs. Anyone can install them with `pip install -r requirements.txt`.

**Libraries we'll need:**
```
langchain
langgraph
langchain-anthropic     # or langchain-openai / langchain-google-genai
python-dotenv           # to load .env file
```

---

## 4. Conversation Flow (Detailed)

```
User says something
        ↓
[intent_detector_node]
        ↓
Is it a greeting? ──→ [greeting_node] → respond → END
        ↓ no
Is it an inquiry? ──→ [rag_node] → search KB → respond → END
        ↓ no
Is it high-intent? ─→ [lead_collection_node]
                              ↓
                    Have name? No → ask for name
                    Have email? No → ask for email
                    Have platform? No → ask for platform
                    Have all three? Yes →
                              ↓
                    [lead_capture_node] → call mock_lead_capture() → confirm → END
```

---

## 5. Intent Detection — How it Works

The agent uses the LLM itself to classify intent. We give it a prompt like:

> "Given this message from a user, classify it as one of: GREETING, INQUIRY, HIGH_INTENT. Message: '{user_message}'"

**Why use the LLM for this and not keyword matching?**
Keyword matching would fail on sentences like "I'm quite interested in checking out what you've got" — no obvious keyword, but clearly high-intent. The LLM understands context.

**Alternative:** Fine-tuned classifier model — overkill for this scope.

---

## 6. RAG Pipeline — Detailed Steps

```
Step 1: User asks "What's in the Pro plan?"
Step 2: retriever.py searches autostream_kb.json
Step 3: Returns: "Pro Plan: $79/month, Unlimited videos, 4K, AI captions"
Step 4: This context is added to the LLM prompt:
         "Using only this context: {retrieved_text}, answer: {user_question}"
Step 5: LLM generates a natural-sounding answer based ONLY on the retrieved data
```

**Key concept:** The LLM never makes up pricing. It only rephrases what we give it. This is RAG.

---

## 7. State Management — What's Retained

Across all 5-6 conversation turns, the state object always holds:

```python
{
  "messages": [...],          # Full conversation so far
  "intent": "HIGH_INTENT",    # Latest detected intent
  "lead_name": "Rahul",       # Collected progressively
  "lead_email": None,         # None until collected
  "lead_platform": None,
  "lead_captured": False
}
```

Every node reads from this state and writes back to it. Nothing is lost between turns.

---

## 8. How to Run Locally (Step by Step)

```bash
# Step 1: Clone your repo
git clone https://github.com/your-username/autostream-agent
cd autostream-agent

# Step 2: Create a virtual environment
python -m venv venv

# Step 3: Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Step 4: Install dependencies
pip install -r requirements.txt

# Step 5: Add your API key
cp .env.example .env
# Now open .env and paste your actual API key

# Step 6: Run
python main.py
```

---

## 9. WhatsApp Integration (README Section Answer)

This is one of the deliverables. Here's what to write:

**How to deploy this agent on WhatsApp using Webhooks:**

1. **Use Twilio or Meta's WhatsApp Business API** — these services act as a bridge between WhatsApp messages and your Python code.

2. **Set up a Webhook URL** — a webhook is a URL that WhatsApp calls every time a user sends a message. You deploy your Python app on a server (e.g., Railway, Render, or a simple Flask app) and expose a `/webhook` endpoint.

3. **Flask wrapper** — you wrap the agent in a Flask route:
   - WhatsApp sends a POST request to your `/webhook` with the user's message
   - Your route extracts the message, passes it to the LangGraph agent
   - Agent returns a response
   - You send the response back via the WhatsApp API

4. **Session management** — each WhatsApp user has a unique phone number. You use this as a session ID to maintain separate state for each user.

5. **Deployment** — host on Railway or Render (free tier), get a public HTTPS URL, register it as your webhook in Twilio/Meta console.

---

## 10. Architecture Explanation (~200 words for README)

> **Copy-paste this into your README.md:**

We chose **LangGraph** over a simple LangChain AgentExecutor because LangGraph gives explicit, visual control over the conversation flow. Each step of the conversation — intent detection, RAG retrieval, lead collection, and tool execution — is a separate node in a directed graph. This makes the agent easier to debug, test, and extend.

**State management** is handled via LangGraph's `StateGraph` with a typed state dictionary that persists across all conversation turns. The state stores the full message history, the detected intent, and progressively collected lead data (name, email, platform). This ensures the agent never forgets what was said earlier in the conversation.

**RAG** is implemented using a local JSON knowledge base. User questions are matched against the knowledge base via semantic search, and only the relevant chunk is passed to the LLM as context — preventing hallucination of pricing or policy information.

**Intent detection** uses the LLM itself with a structured classification prompt, making it robust to varied phrasing. **Tool execution** (lead capture) is triggered only after all three required fields are confirmed in state, ensuring the mock API is never called prematurely.

---

## 11. Interview Topics You Must Know

These are the concepts that can be asked in interviews based on this project. Study each one.

### 11.1 LLMs & Prompting
- What is a Large Language Model (LLM)?
- What is a prompt? What is a system prompt vs user prompt?
- What is prompt engineering?
- What are tokens? Why do they matter for cost?
- What is temperature in LLMs? What does a high vs low temperature do?
- What is hallucination in LLMs? How does RAG prevent it?

### 11.2 RAG (Retrieval Augmented Generation)
- What is RAG and why is it needed?
- Difference between RAG and fine-tuning
- What is a vector embedding? (concept-level, not math)
- What is a vector database? (FAISS, ChromaDB, Pinecone)
- How do you chunk documents for RAG?
- What is semantic search vs keyword search?

### 11.3 LangChain & LangGraph
- What is LangChain? What problem does it solve?
- What is LangGraph? How is it different from LangChain AgentExecutor?
- What is a node in LangGraph?
- What is an edge? What is a conditional edge?
- What is state in LangGraph? How is it updated?
- What is a chain in LangChain?

### 11.4 AI Agents & Tool Use
- What is an AI agent vs a chatbot?
- What is tool calling / function calling?
- What is ReAct prompting? (Reasoning + Acting)
- What is an agentic workflow?
- How does an agent decide when to use a tool?

### 11.5 Software Engineering Concepts
- What is a REST API? What is a webhook?
- What is a virtual environment in Python and why use it?
- What is a `.env` file? Why should it never be committed?
- What is `requirements.txt`?
- What is separation of concerns?
- What is a Python package (`__init__.py`)?
- Difference between synchronous and asynchronous code (basic)

### 11.6 System Design (For This Project Specifically)
- How would you scale this to handle 10,000 users simultaneously?
- How would you add a database to persist leads permanently?
- How would you deploy this on WhatsApp?
- How would you add authentication so only logged-in users can use it?
- How would you monitor if the agent is giving wrong answers?

### 11.7 GenAI Product Concepts
- What is a lead? What is lead capture?
- What is intent detection? What are the different types of intent?
- What is a CRM? (Customer Relationship Management)
- What is the difference between a chatbot and a GenAI agent?
- What is multi-turn conversation and why is memory important?

---

## 12. Build Order (Do This Sequence)

Follow this exact order to avoid confusion:

```
Step 1 → Create folder structure
Step 2 → Create knowledge_base/autostream_kb.json
Step 3 → Create rag/retriever.py (understand RAG first)
Step 4 → Create agent/state.py (understand state)
Step 5 → Create agent/tools.py (the mock function)
Step 6 → Create agent/nodes.py (one node at a time)
Step 7 → Create agent/graph.py (wire the nodes)
Step 8 → Create main.py (run it!)
Step 9 → Test full conversation flow
Step 10 → Write README.md
Step 11 → Record demo video
Step 12 → Push to GitHub
```

---

## 13. Sample Test Conversation to Verify Everything Works

Run through this conversation to confirm all features are working:

```
You: Hi there!
Agent: [Should greet warmly — tests greeting node]

You: What plans do you offer?
Agent: [Should mention Basic ($29) and Pro ($79) — tests RAG]

You: Does the Pro plan have AI captions?
Agent: [Should say yes, from knowledge base — tests RAG accuracy]

You: What's your refund policy?
Agent: [Should say no refunds after 7 days — tests policy RAG]

You: I want to sign up for the Pro plan for my YouTube channel.
Agent: [Should detect high-intent, ask for name — tests intent detection]

You: My name is Rahul.
Agent: [Should ask for email — tests progressive lead collection]

You: rahul@gmail.com
Agent: [Should ask for platform — tests state persistence]

You: YouTube
Agent: [Should call mock_lead_capture() and confirm — tests tool execution]
```

If all 8 turns work correctly, the assignment is complete.

---

*PRD Version 1.0 | AutoStream Agent | ServiceHive ML Intern Assignment*
