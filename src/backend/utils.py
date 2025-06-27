
import dotenv
from pathlib import Path
from typing_extensions import TypedDict
from operator import add
from typing import Annotated, List
from langchain_core.exceptions import OutputParserException

# ---------------------------------------------------------------------------
class Config:
    llms_with_structured_output_support = {'azure-gpt-4o', 'claude-3-5-sonnet', 'gemini-1.5-pro'}
    llms_selected = {
        'OpenAI': {'azure-o1-mini': 'o1-mini', 'azure-o1': 'o1', 'azure-o3-mini': 'o3-mini', 'azure-o3': 'o3', 'azure-gpt-4o': 'GPT-4o'}, 
        'Anthropic': {'claude-3-7-sonnet': 'Claude 3.7 sonnet', 'claude-3-5-sonnet': 'Claude 3.5 sonnet'}, 
        'Google': {'gemini-1.5-flash': 'Gemini 1.5 Flash', 'gemini-1.5-pro': 'Gemini 1.5 Pro'}, 
        'Meta': {'llama3-3-70b': 'Llama 3.3 70B', 'llama3-3-90b': 'Llama 3.3 90B', 'llama3-1-405b': 'Llama 3.1 405B', 'llama3-1-70b': 'Llama 3.1 70B'},
        'Mistral': {'mistral-large-2': 'Mistral Large 2'}
    }
    env_config = dotenv.dotenv_values(Path(".env"))

    # Generation
    NUM_TOKENS_SUMMARY = 500
    RETRY_COUNTER = 2

    # RAG
    TOKENS_PER_LLM_CALL = 5000
    MAX_KEYWORDS = 10
    SIMILARITY_METRIC = 'similarity_score_threshold'
    NUM_DOCS_MAX = 5
    SIMILARITY_THRESHOLD = 0.3

# ---------------------------------------------------------------------------
class State(TypedDict):
    content_pre: str
    current_section: str
    keyphrases: List[str]
    rag_context: str
    steps: Annotated[List[str], add]
    response: str

# ---------------------------------------------------------------------------
def retryInvoke(chain, input):

    for counter_retry in range(Config.RETRY_COUNTER):
        try:
            response = chain.invoke(input=input)
            return response
        except OutputParserException as exp:
            print(str(exp))
            print('retrying')

    raise Exception(f'Output could not be fixing after trying {Config.RETRY_COUNTER} times')