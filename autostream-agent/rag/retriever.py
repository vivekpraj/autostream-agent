import json
import os

def load_knowledge_base():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    kb_path = os.path.join(base_dir, "knowledge_base", "autostream_kb.json")
    with open(kb_path, "r") as f:
        return json.load(f)

def retrieve(query: str) -> str:
    kb = load_knowledge_base()
    all_entries = kb.get("plans", []) + kb.get("policies", [])

    context = ""
    for entry in all_entries:
        context += f"{entry['topic']}:\n{entry['content']}\n\n"

    return context.strip()
