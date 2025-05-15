
import dotenv
from pathlib import Path
from typing_extensions import TypedDict
from operator import add
from typing import Annotated, List
from langchain_core.exceptions import OutputParserException

# ---------------------------------------------------------------------------
class Config:
    llms_with_structured_output_support = {'azure-gpt-4o', 'claude-3-5-sonnet', 'gemini-1.5-pro'}
    env_config = dotenv.dotenv_values(Path(".env"))
    dotenv.load_dotenv(Path(".env"))

    NUM_TOKENS_SUMMARY = 500
    RETRY_COUNTER = 2

# ---------------------------------------------------------------------------
class State(TypedDict):
    content_pre: str
    current_section: str
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