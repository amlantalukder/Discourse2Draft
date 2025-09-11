from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph
from .common import State, StateOutline
from .llms import getAIModel
from .analyze_content_header import AnalyzeContentHeader
from .gather_context import GatherContext
from .gather_context_graph import GatherContextGraph
from .summarize import Summarize
from .generate_content import GenerateContent
from .generate_content_rag import GenerateContentRAG
from .generate_content_graphrag import GenerateContentGraphRAG
from .add_citations import AddCitations
from .generate_outline import GenerateOutline
from .add_literature import AddLiterature
from typing import Literal
from rich import print
from utils import print_func_name

# -----------------------------------------------------------------------
@print_func_name
def check_if_summary_needed(
        state: State,
    ) -> Literal['Summarize', 'Generate Content']:
        if len(state.get('content_pre').split()) > 500:
            return 'Summarize'
        return 'Generate Content'

# -----------------------------------------------------------------------
@print_func_name
def check_if_summary_needed_rag(
        state: State,
    ) -> Literal['Summarize', 'Analyze Content Header']:
        if len(state.get('content_pre').split()) > 500:
            return 'Summarize'
        return 'Analyze Content Header'

@print_func_name
def wait(state):
    return {'steps': ['Wait']}

# -----------------------------------------------------------------------
class Architecture:

    @print_func_name
    def __init__(self, model_name, temperature, instructions, type='base', collection_name='', collection_name_lit_search=''):
        llm = getAIModel(model_name=model_name, temperature=temperature)

        print(f'Using {llm.model_name} with temperature {temperature} in {type} architecture\n')

        match type:
            case 'rag':
                assert collection_name != '' or collection_name_lit_search != '', f'Either collection_name must be provided, found {collection_name}'
                self.createRAGAgent(llm, instructions, collection_name=collection_name, collection_name_lit_search=collection_name_lit_search)
            case 'graphrag':
                assert collection_name != '', f'collection_name must be provided, found {collection_name}'
                self.createGraphRAGAgent(llm, instructions, collection_name=collection_name)
            case _:
                self.createBaseAgent(llm, instructions)

    @print_func_name
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

    @print_func_name
    def createRAGAgent(self, llm, instructions, collection_name='', collection_name_lit_search=''):

        # Define a new graph
        workflow = StateGraph(state_schema=State)

        # Define the (single) node in the graph
        workflow.add_node("Summarize", Summarize(llm=llm))
        workflow.add_node("Analyze Content Header", AnalyzeContentHeader(llm=llm))
        if collection_name:
            workflow.add_node("Gather Context from Documents", GatherContext(collection_name=collection_name))
        if collection_name_lit_search:
            workflow.add_node("Add Literature", AddLiterature(collection_name=collection_name_lit_search))
            workflow.add_node("Gather Context from Literature", GatherContext(collection_name=collection_name_lit_search))
        if collection_name and collection_name_lit_search:
            workflow.add_node("Wait for the Other Branch", wait)
        workflow.add_node("Generate Content", GenerateContentRAG(llm=llm, instructions=instructions))
        #workflow.add_node("Add Citations", AddCitations(llm))

        workflow.add_conditional_edges(START, check_if_summary_needed_rag)
        workflow.add_edge("Summarize", "Analyze Content Header")
        if collection_name:
            workflow.add_edge("Analyze Content Header", "Gather Context from Documents")
            if collection_name_lit_search:
                workflow.add_edge("Gather Context from Documents", "Wait for the Other Branch")
                workflow.add_edge("Wait for the Other Branch", "Generate Content")
            else:
                workflow.add_edge("Gather Context from Documents", "Generate Content")
        if collection_name_lit_search:
            workflow.add_edge("Analyze Content Header", "Add Literature")
            workflow.add_edge("Add Literature", "Gather Context from Literature")
            workflow.add_edge("Gather Context from Literature", "Generate Content")
        #workflow.add_edge("Generate Content", "Add Citations")
        #workflow.add_edge("Add Citations", END)

        # Add memory
        memory = MemorySaver()
        self.agent = workflow.compile(checkpointer=memory)

    @print_func_name
    def createGraphRAGAgent(self, llm, instructions, collection_name):

        # Define a new graph
        workflow = StateGraph(state_schema=State)

        # Define the (single) node in the graph
        workflow.add_node("Summarize", Summarize(llm=llm))
        workflow.add_node("Analyze Content Header", AnalyzeContentHeader(llm=llm))
        workflow.add_node("Gather Context", GatherContextGraph(llm=llm, collection_name=collection_name))
        workflow.add_node("Generate Content", GenerateContentGraphRAG(llm=llm, instructions=instructions))
        #workflow.add_node("Add Citations", AddCitations(llm))

        workflow.add_conditional_edges(START, check_if_summary_needed_rag)
        workflow.add_edge("Summarize", "Analyze Content Header")
        workflow.add_edge("Analyze Content Header", "Gather Context")
        workflow.add_edge("Gather Context", "Generate Content")
        #workflow.add_edge("Generate Content", "Add Citations")
        #workflow.add_edge("Add Citations", END)

        # Add memory
        memory = MemorySaver()
        self.agent = workflow.compile(checkpointer=memory)

# -----------------------------------------------------------------------
class ArchitectureOutline:
     
    @print_func_name
    def __init__(self, model_name, temperature, instructions):

        llm = getAIModel(model_name=model_name, temperature=temperature)
        
        self.createOutlineAgent(llm, instructions)

    @print_func_name
    def createOutlineAgent(self, llm, instructions):

        # Define a new graph
        workflow = StateGraph(state_schema=StateOutline)

        # Define the (single) node in the graph
        workflow.add_node("Generate Outline", GenerateOutline(llm=llm, instructions=instructions))
        workflow.add_edge(START, "Generate Outline")

        # Add memory
        memory = MemorySaver()
        self.agent = workflow.compile(checkpointer=memory)