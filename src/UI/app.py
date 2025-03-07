"""TODO after agent framework."""
from chat_ui import chat_ui

# Dummy function that always returns the same response
def dummy_generate_response(prompt):
    return "This is a static response. Replace this with your AI model."

if __name__ == "__main__":
    chat_ui(dummy_generate_response)
