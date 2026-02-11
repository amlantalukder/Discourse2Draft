from langgraph.graph import START, END, StateGraph
from langgraph.types import Command
from typing import Literal
from .common import StateContentManager, StateOutlineManager
from .llms import getAIModel
from .analyze_content_header import AnalyzeContentHeader
from .gather_context import GatherContext
from .gather_context_graph import GatherContextGraph
from .summarize import Summarize
from .generate_content import GenerateContent
from .generate_content_rag import GenerateContentRAG
from .generate_content_graphrag import GenerateContentGraphRAG
from .generate_outline import GenerateOutline
from .format_outline import FormatOutline
from .add_literature import AddLiterature
from .detect_abstract_section import DetectAbstractSection
from .write_abstract import WriteAbstract
from ..utils import Config
from utils import print_func_name
import logging

# -----------------------------------------------------------------------
@print_func_name
def checkIfSummaryNeededForPrevContent(state: StateContentManager) -> bool:
    return len(state.get('content_pre').split()) > Config.NUM_TOKENS_SUMMARY

# -----------------------------------------------------------------------        
@print_func_name
def checkIfSummaryNeededForGenContent(state: StateContentManager) -> Command:
    if len(state.get('content').split()) > Config.NUM_TOKENS_SUMMARY:
        return Command(goto="Summarize Generated Content")
    return Command(update={'content_summary': state.get('content')}, goto=END)
        
# -----------------------------------------------------------------------
@print_func_name
def wait(state):
    return {'steps': ['Wait']}

# -----------------------------------------------------------------------
class Architecture:
     
    @print_func_name
    def __init__(self, model_name=Config.env_config['DEFAULT_AI_MODEL'], temperature=0, instructions=''):

        self.llm = getAIModel(model_name=model_name, temperature=temperature)
        self.instructions = instructions

    def createAgent(self):
        raise NotImplementedError

# -----------------------------------------------------------------------
class ContentWriterArchitecture(Architecture):

    @print_func_name
    def __init__(self, 
                 model_name=Config.env_config['DEFAULT_AI_MODEL'], 
                 temperature=0, 
                 instructions='', 
                 type='base', 
                 collection_name='', 
                 collection_name_lit_search=''):
        
        super().__init__(model_name=model_name, temperature=temperature, instructions=instructions)

        self.type = type
        self.collection_name = collection_name
        self.collection_name_lit_search = collection_name_lit_search

        logging.info(f'Using {model_name} with temperature {temperature} in {type} architecture\n')

        self.createAgent()

    @print_func_name
    def createAgent(self):

        match self.type:
            case 'rag':
                workflow = self.createRAGWorkflow()
            case 'graphrag':
                workflow = self.createGraphRAGWorkflow()
            case _:
                workflow = self.createBaseWorkflow()

        self.agent = workflow.compile()

    @print_func_name
    def createBaseWorkflow(self):

        # Define a new graph
        workflow = StateGraph(state_schema=StateContentManager)

        # Define the (single) node in the graph
        workflow.add_node("Summarize Previous Content", Summarize(llm=self.llm, input_field='content_pre', output_field='content_pre'))
        workflow.add_node("Generate Content", GenerateContent(llm=self.llm, instructions=self.instructions))
        workflow.add_node("Summarize Generated Content", Summarize(llm=self.llm, input_field='content', output_field='content_summary'))
        workflow.add_node("Check If Summary Needed", checkIfSummaryNeededForGenContent)

        workflow.add_conditional_edges(START, checkIfSummaryNeededForPrevContent, {True: "Summarize Previous Content", False: "Generate Content"})
        workflow.add_edge("Summarize Previous Content", "Generate Content")
        workflow.add_edge("Generate Content", "Check If Summary Needed")
    
        return workflow

    @print_func_name
    def createRAGWorkflow(self):

        assert self.collection_name != '' or self.collection_name_lit_search != '', f'Either collection_name must be provided, found {self.collection_name}'
    
        # Define a new graph
        workflow = StateGraph(state_schema=StateContentManager)

        # Define the (single) node in the graph
        workflow.add_node("Summarize Previous Content", Summarize(llm=self.llm, input_field='content_pre', output_field='content_pre'))
        workflow.add_node("Analyze Content Header", AnalyzeContentHeader(llm=self.llm))
        if self.collection_name:
            workflow.add_node("Gather Context from Documents", GatherContext(collection_name=self.collection_name))
        if self.collection_name_lit_search:
            workflow.add_node("Add Literature", AddLiterature(collection_name=self.collection_name_lit_search))
            workflow.add_node("Gather Context from Literature", GatherContext(collection_name=self.collection_name_lit_search))
        if self.collection_name and self.collection_name_lit_search:
            workflow.add_node("Wait for the Other Branch", wait)
        workflow.add_node("Generate Content", GenerateContentRAG(llm=self.llm, instructions=self.instructions))
        workflow.add_node("Summarize Generated Content", Summarize(llm=self.llm, input_field='content', output_field='content_summary'))
        workflow.add_node("Check If Summary Needed", checkIfSummaryNeededForGenContent)

        workflow.add_conditional_edges(START, checkIfSummaryNeededForPrevContent, {True: "Summarize Previous Content", False: "Analyze Content Header"})
        workflow.add_edge("Summarize Previous Content", "Analyze Content Header")
        if self.collection_name:
            workflow.add_edge("Analyze Content Header", "Gather Context from Documents")
            if self.collection_name_lit_search:
                workflow.add_edge("Gather Context from Documents", "Wait for the Other Branch")
                workflow.add_edge("Wait for the Other Branch", "Generate Content")
            else:
                workflow.add_edge("Gather Context from Documents", "Generate Content")
        if self.collection_name_lit_search:
            workflow.add_edge("Analyze Content Header", "Add Literature")
            workflow.add_edge("Add Literature", "Gather Context from Literature")
            workflow.add_edge("Gather Context from Literature", "Generate Content")
        workflow.add_edge("Generate Content", "Check If Summary Needed")

        return workflow

    @print_func_name
    def createGraphRAGWorkflow(self):

        assert self.collection_name != '', f'collection_name must be provided, found {self.collection_name}'

        # Define a new graph
        workflow = StateGraph(state_schema=StateContentManager)

        # Define the (single) node in the graph
        workflow.add_node("Summarize Previous Content", Summarize(llm=self.llm, input_field='content_pre', output_field='content_pre'))
        workflow.add_node("Analyze Content Header", AnalyzeContentHeader(llm=self.llm))
        workflow.add_node("Gather Context", GatherContextGraph(llm=self.llm, collection_name=self.collection_name))
        workflow.add_node("Generate Content", GenerateContentGraphRAG(llm=self.llm, instructions=self.instructions))
        workflow.add_node("Summarize Generated Content", Summarize(llm=self.llm, input_field='content', output_field='content_summary'))
        workflow.add_node("Check If Summary Needed", checkIfSummaryNeededForGenContent)

        workflow.add_conditional_edges(START, checkIfSummaryNeededForPrevContent, {True: "Summarize Previous Content", False: "Analyze Content Header"})
        workflow.add_edge("Summarize Previous Content", "Analyze Content Header")
        workflow.add_edge("Analyze Content Header", "Gather Context")
        workflow.add_edge("Gather Context", "Generate Content")
        workflow.add_edge("Generate Content", "Check If Summary Needed")

        return workflow

# -----------------------------------------------------------------------
class AbstractSectionDetectorArchitecture(Architecture):

    @print_func_name
    def __init__(self, model_name=Config.env_config['DEFAULT_AI_MODEL'], temperature=0, instructions=''):
        
        super().__init__(model_name=model_name, temperature=temperature, instructions=instructions)

        logging.info(f'Using {model_name} with temperature {temperature} in AbstractSectionDetectorArchitecture architecture\n')

        self.createAgent()

    @print_func_name
    def createAgent(self):

        # Define a new graph
        workflow = StateGraph(state_schema=StateContentManager)

        # Define the (single) node in the graph
        workflow.add_node("Detect Abstract Section", DetectAbstractSection(llm=self.llm, instructions=self.instructions))
        workflow.add_edge(START, "Detect Abstract Section")

        self.agent = workflow.compile()

# -----------------------------------------------------------------------
class AbstractWriterArchitecture(Architecture):

    @print_func_name
    def __init__(self, model_name=Config.env_config['DEFAULT_AI_MODEL'], temperature=0, instructions=''):
        
        super().__init__(model_name=model_name, temperature=temperature, instructions=instructions)

        logging.info(f'Using {model_name} with temperature {temperature} in AbstractWriterArchitecture architecture\n')

        self.createAgent()

    @print_func_name
    def createAgent(self):

        # Define a new graph
        workflow = StateGraph(state_schema=StateContentManager)

        # Define the (single) node in the graph
        workflow.add_node("Write Abstract", WriteAbstract(llm=self.llm, instructions=self.instructions))
        workflow.add_edge(START, "Write Abstract")

        self.agent = workflow.compile()

# -----------------------------------------------------------------------
class OutlineCreatorArchitecture(Architecture):

    @print_func_name
    def __init__(self, model_name=Config.env_config['DEFAULT_AI_MODEL'], temperature=0, instructions=''):
        
        super().__init__(model_name=model_name, temperature=temperature, instructions=instructions)

        logging.info(f'Using {model_name} with temperature {temperature} in OutlineCreatorArchitecture architecture\n')

        self.createAgent()

    @print_func_name
    def createAgent(self):

        # Define a new graph
        workflow = StateGraph(state_schema=StateOutlineManager)

        # Define the (single) node in the graph
        workflow.add_node("Generate Outline", GenerateOutline(llm=self.llm, instructions=self.instructions))
        workflow.add_edge(START, "Generate Outline")

        self.agent = workflow.compile()

# -----------------------------------------------------------------------
class OutlineFormatterArchitecture(Architecture):

    @print_func_name
    def __init__(self, model_name=Config.env_config['DEFAULT_AI_MODEL'], temperature=0, instructions=''):
        
        super().__init__(model_name=model_name, temperature=temperature, instructions=instructions)
        logging.info(f'Using {model_name} with temperature {temperature} in OutlineFormatterArchitecture architecture\n')

        self.createAgent()

    @print_func_name
    def createAgent(self):

        # Define a new graph
        workflow = StateGraph(state_schema=StateOutlineManager)

        # Define the (single) node in the graph
        workflow.add_node("Format Outline", FormatOutline(llm=self.llm, instructions=self.instructions))
        workflow.add_edge(START, "Format Outline")

        self.agent = workflow.compile()