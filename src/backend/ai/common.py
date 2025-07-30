from typing_extensions import TypedDict
from operator import add
from typing import Annotated, List, Dict
from pydantic import BaseModel
from langchain_core.exceptions import OutputParserException
from langchain_community.graphs.networkx_graph import NetworkxEntityGraph
from ..utils import Config
from rich import print

# ---------------------------------------------------------------------------
class ReferenceSchema(BaseModel):
    '''
    The reference of file name with file id
    '''
    file_id: str
    file_name: str

# ---------------------------------------------------------------------------
class State(TypedDict):
    content_pre: str
    current_section: str
    keyphrases: List[str]
    rag_context: Annotated[str, lambda x, y: x + '\n\n' + y]
    graphrag_context: Dict[str, NetworkxEntityGraph]
    literature_list: List[Dict[str, str]]
    steps: Annotated[List[str], add]
    content: str
    references: List[ReferenceSchema]

# ---------------------------------------------------------------------------
class StateOutline(TypedDict):
    topic: str
    steps: Annotated[List[str], add]
    content: str