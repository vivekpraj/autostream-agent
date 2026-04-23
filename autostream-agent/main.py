import os
from dotenv import load_dotenv
from agent.graph import build_graph

load_dotenv()

def main():
    print("AutoStream Agent is ready! Type 'exit' to quit.\n")

    graph = build_graph()

    state = {
        "messages": [],
        "intent": None,
        "lead_name": None,
        "lead_email": None,
        "lead_platform": None,
        "lead_captured": False,
        "collecting_lead": False
    }

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            if state["lead_captured"]:
                print(f"Agent: Thanks {state['lead_name']}! We'll be in touch at {state['lead_email']}. Goodbye!")
            elif state["collecting_lead"]:
                print("Agent: You haven't completed your signup yet. Come back anytime! Goodbye!")
            else:
                print("Agent: Thanks for chatting with AutoStream. Goodbye!")
            break

        if not user_input:
            continue

        state["messages"].append({"role": "user", "content": user_input})

        state = graph.invoke(state)

        reply = state["messages"][-1]["content"]
        print(f"Agent: {reply}\n")


if __name__ == "__main__":
    main()
