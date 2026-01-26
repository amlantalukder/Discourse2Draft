from typing_extensions import TypedDict
from operator import add
from typing import Annotated, List, Dict
from pydantic import BaseModel
from langchain_community.graphs.networkx_graph import NetworkxEntityGraph
from ..utils import Config
from utils import print_func_name
import logging
import re

# ---------------------------------------------------------------------------
class ReferenceSchema(BaseModel):
    '''
    The reference of file name with file id
    '''
    file_id: str
    file_name: str

# ---------------------------------------------------------------------------
class StateContentManager(TypedDict):
    content_pre: str
    current_section: str
    content_specific_instructions: str
    keyphrases: List[str]
    rag_context: Annotated[str, lambda x, y: x + '\n\n' + y]
    graphrag_context: Dict[str, NetworkxEntityGraph]
    literature_list: List[Dict[str, str]]
    steps: Annotated[List[str], add]
    content: str
    references: List[ReferenceSchema]
    is_abstract: bool

# ---------------------------------------------------------------------------
class StateOutlineManager(TypedDict):
    query: str
    steps: Annotated[List[str], add]
    content: str
    outline_unstructured: str

# ---------------------------------------------------------------------------
@print_func_name
def extractLLMResponse(task_name, chain, kargs, key_to_find, value_name, additionalCheckingFunc=None, return_response=False):

    task_node_name = re.sub(r'[ ()]', '', task_name)

    for c in range(Config.RETRY_COUNTER):
        
        response = chain.invoke(input=kargs)
        try:
            response = dict(response)
            value = response[key_to_find]
        except:
            logging.info(f'{task_node_name} response does not have {key_to_find}, response: {response}')
            if c < Config.RETRY_COUNTER:
                logging.info('Retrying...')
            continue

        if additionalCheckingFunc and not additionalCheckingFunc(response):
            if c < Config.RETRY_COUNTER:
                logging.info('Retrying...')
            continue 

        if return_response:
            return {value_name: value, 'steps': [task_name]}, response    

        return {value_name: value, 'steps': [task_name]}
        
    raise Exception(f'{task_node_name} failed to generate content after {Config.RETRY_COUNTER} retries.')


# ---------------------------------------------------------------------------
GENERATE_CONTENT_INSTRUCTIONS = '''\
<Instructions>
    <Consistency>
    - Your writing must be consistent with previous section.
    - You must maintain the flow of writing.
    </Consistency>
    
    <Voice and register>
    - Doctoral‑level, formal scientific style (as in a peer‑reviewed journal).
    - Integrate definitions, mechanisms, empirical findings and theoretical nuance as appropriate.
    - Write at great enough depth that the reader will fully understand the various aspects of the sub section, but avoid being overly redundant with other sections.
    </Voice and register>
    
    <Form>
    - Only paragraphs — no headings, no numbering, no bullet points, no embedded outline codes.
    - You may use multiple paragraphs if needed to cover the content deeply and coherently. 
    - If not absolutely necessary, do not split related content into different paragraphs to maintain consistency.
    </Form>

    <Writing Depth and Style>
    - Avoid repeating detailed explanations already supplied for earlier sections unless essential for clarity; instead, use concise forward/backward references if necessary.
    - Where deemed necessary to illustrate a point/provide clarity, employ specific/detailed examples that help the reader better understand critical concepts.
    - When responding your sole values should be scientific accuracy, application of rigorous scientific reasoning, and material reasoning/rationality.
    - Identify hidden biases in your answer and correct them.
    </Writing Depth and Style>
</Instructions>\
'''

CITE_CONTEXT_INSTRUCTIONS = '''\
<Adding text from context>
    - The context is provided with RAG Context under file_id tags. Each file_id tag contains the reference and content.
    - In your writing, take context from the RAG Context whenever possible.
    - At the end of your writing from the context, cite the RAG context with the file_id within "[" and "]" in the following format: [CITE(file_id)].
    - If the context of a line is taken from the RAG context of multiple file_id's, you can cite all the file_ids in a comma separated string within "[" and "]" in the following format: [CITE(file_id1, file_id2)]. 
    - Do not put the citation after texts if the written texts are not from the RAG context.
    - If the written texts from RAG context is divided into multiple paragraphs, put citation at the end of each of the paragraphs.
    - You must put the citation before the ending "." of the corresponding line.
</Adding text from context>\
'''