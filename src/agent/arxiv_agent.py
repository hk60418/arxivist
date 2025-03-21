import logging
import random
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
# Ollama
if False:
    main_model = "deepseek-r1:70b"
    main_tokenizer = None
    tool_model ="llama3.2:3b"
    tool_tokenizer = None
    pipe = None
    toolpipe = None


# MLX_LM
if False:
    from mlx_lm import load
    main_model, main_tokenizer = load('/Users/henrikynsilehto/models/mlx_watt-tool-8B')
    tool_model, tool_tokenizer = load('/Users/henrikynsilehto/models/mlx_watt-tool-8B')
    pipe = None
    toolpipe = None

# Transformers
if True:
    from transformers import pipeline
    toolpipe = pipeline("text-generation", model="/Users/henrikynsilehto/models/Llama-3-Groq-8B-Tool-Use")
    pipe = pipeline("text-generation", model="/Users/henrikynsilehto/models/Llama-3-Groq-8B-Tool-Use")
    main_model = None
    tool_model = None
    main_tokenizer = None
    tool_tokenizer = None



# Tools
tools = [
    database_client.text_search,
    weather_forecast
]

agent = AgentFramework(
    llm=main_model,
    tokenizer=main_tokenizer,
    tool_llm=tool_model,
    tool_tokenizer=tool_tokenizer,
    tool_pipeline=toolpipe,
    pipeline=pipe,
    tools=tools)

query_handler = agent.invoke
