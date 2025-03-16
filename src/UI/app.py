import logging
from chat_ui import chat_ui
from src.agent.arxiv_agent import query_handler


logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s")
logging.getLogger("agent_framework").setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)

# Dummy function that always returns the same response
def dummy_generate_response(prompt):
    return "This is a static response. Replace this with your AI model."

if __name__ == "__main__":
    chat_ui(query_handler)
