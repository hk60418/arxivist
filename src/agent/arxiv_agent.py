import random

from mlx_lm import load
from agent_framework import AgentFramework

# Main model (Ollama)
main_model = "deepseek-r1:70b"

# Tool model
tool_model, tool_tokenizer = load('/Users/henrikynsilehto/models/mlx_watt-tool-8B')

# Tools
def weather_forecast(location: str = None) -> str:
    """Get day's weather forecast for location.

    :param location: Location string
    :returns: str Weather forecast for the day.
    """
    responses = ["It rains and everybody are pissed.", "Sun is shining!", "Slightly overcast with small probability of rain.", "Snowing heavily."]
    response = responses[random.randrange(0,4)]
    return response
tools = [weather_forecast]


agent = AgentFramework(llm=main_model, tool_llm=tool_model, tool_tokenizer=tool_tokenizer, tools=tools)

query_handler = agent.invoke