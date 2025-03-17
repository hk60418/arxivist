import logging
import random
from mlx_lm import load
from agent_framework import AgentFramework
from src.arxiv_agent.ml.embedding_model_sentence_transformer import EmbeddingSentenceTransformer as Embedding
from src.database.database_client_qdrant import DatabaseClientQdrant as DatabaseClient


logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s")
logging.getLogger("agent_framework").setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)

def weather_forecast(location: str = None) -> str:
    """Get day's weather forecast for location.

    :param location: Location string
    :returns: str Weather forecast for the day.
    """
    responses = ["It rains and everybody are pissed.", "Sun is shining!", "Slightly overcast with small probability of rain.", "Snowing heavily."]
    response = responses[random.randrange(0,4)]
    return response

embedding_model = Embedding()

database_client = DatabaseClient.get_instance()

# Tool model
tool_model, tool_tokenizer = load('/Users/henrikynsilehto/models/mlx_watt-tool-8B')

# Tools
tools = [
    database_client.text_search,
    weather_forecast
]

print(f'DOC: {tools[0].__doc__}')

agent = AgentFramework(llm=tool_model, tokenizer=tool_tokenizer, tool_llm=tool_model, tool_tokenizer=tool_tokenizer, tools=tools)

query_handler = agent.invoke
