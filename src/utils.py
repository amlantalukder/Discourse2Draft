
import dotenv
from pathlib import Path
from typing_extensions import TypedDict
from operator import add
from typing import Annotated, List

# ---------------------------------------------------------------------------
class Config:
    llms_with_structured_output_support = {'azure-gpt-4o', 'claude-3-5-sonnet', 'gemini-1.5-pro'}
    env_config = dotenv.dotenv_values(Path(".env"))
    dotenv.load_dotenv(Path(".env"))

# ---------------------------------------------------------------------------
class State(TypedDict):
    current_section: str
    steps: Annotated[List[str], add]
    response: str