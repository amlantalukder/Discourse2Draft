from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph
from .utils import State, StateOutline
from .llms import getAIModel
from .analyze_query import AnalyzeQuery
from .gather_context import GatherContext
from .summarize import Summarize
from .generate_content import GenerateContent
from .generate_content_rag import GenerateContentRAG
from .add_citations import AddCitations
from .generate_outline import GenerateOutline
from typing import Literal
from rich import print

# -----------------------------------------------------------------------
def check_if_summary_needed(
        state: State,
    ) -> Literal['Summarize', 'Generate Content']:
        if len(state.get('content_pre').split()) > 500:
            return 'Summarize'
        return 'Generate Content'

# -----------------------------------------------------------------------
def check_if_summary_needed_rag(
        state: State,
    ) -> Literal['Summarize', 'Analyze Query']:
        if len(state.get('content_pre').split()) > 500:
            return 'Summarize'
        return 'Analyze Query'

# -----------------------------------------------------------------------
class Architecture:

    def __init__(self, model_name, temperature, instructions, type='base', collection_name=''):
        llm = getAIModel(model_name=model_name, temperature=temperature)

        print(f'Using {llm.model_name} with temperature {temperature} in {type} architecture\n')

        match type:
            case 'rag':
                assert collection_name != '', f'collection_name must be provided, found {collection_name}'
                self.createRAGAgent(llm, instructions, collection_name=collection_name)
            case _:
                self.createBaseAgent(llm, instructions)

    def createBaseAgent(self, llm, instructions):

        # Define a new graph
        workflow = StateGraph(state_schema=State)

        # Define the (single) node in the graph
        workflow.add_node("Summarize", Summarize(llm=llm))
        workflow.add_node("Generate Content", GenerateContent(llm=llm, instructions=instructions))
        #workflow.add_node("Add Citations", AddCitations(llm))

        workflow.add_conditional_edges(START, check_if_summary_needed)
        workflow.add_edge("Summarize", "Generate Content")
        #workflow.add_edge("Generate Content", "Add Citations")
        #workflow.add_edge("Add Citations", END)

        # Add memory
        memory = MemorySaver()
        self.agent = workflow.compile(checkpointer=memory)

    def createRAGAgent(self, llm, instructions, collection_name):

        # Define a new graph
        workflow = StateGraph(state_schema=State)

        # Define the (single) node in the graph
        workflow.add_node("Summarize", Summarize(llm=llm))
        workflow.add_node("Analyze Query", AnalyzeQuery(llm=llm))
        workflow.add_node("Gather Context", GatherContext(collection_name=collection_name))
        workflow.add_node("Generate Content", GenerateContentRAG(llm=llm, instructions=instructions))
        #workflow.add_node("Add Citations", AddCitations(llm))

        workflow.add_conditional_edges(START, check_if_summary_needed_rag)
        workflow.add_edge("Summarize", "Analyze Query")
        workflow.add_edge("Analyze Query", "Gather Context")
        workflow.add_edge("Gather Context", "Generate Content")
        #workflow.add_edge("Generate Content", "Add Citations")
        #workflow.add_edge("Add Citations", END)

        # Add memory
        memory = MemorySaver()
        self.agent = workflow.compile(checkpointer=memory)


# -----------------------------------------------------------------------
class ArchitectureOutline:
     
    def __init__(self, model_name, temperature, instructions):

        llm = getAIModel(model_name=model_name, temperature=temperature)
        
        self.createOutlineAgent(llm, instructions)

    def createOutlineAgent(self, llm, instructions):

        # Define a new graph
        workflow = StateGraph(state_schema=StateOutline)

        # Define the (single) node in the graph
        workflow.add_node("Generate Outline", GenerateOutline(llm=llm, instructions=instructions))
        workflow.add_edge(START, "Generate Outline")

        # Add memory
        memory = MemorySaver()
        self.agent = workflow.compile(checkpointer=memory)