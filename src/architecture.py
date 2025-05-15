from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph
from .utils import State
from .llms import getOpenAIModel
from .generate_report import GenerateReport
from .summarize import Summarize
from .add_citations import AddCitations
from typing import Literal

# -----------------------------------------------------------------------
def check_if_summary_needed(
        state: State,
    ) -> Literal['Summarize', 'Generate Report']:
        if len(state.get('content_pre').split()) > 500:
            return 'Summarize'
        return 'Generate Report'

class Architecture:

    def __init__(self, model_name, temperature, instructions):
        llm = getOpenAIModel(model_name=model_name, temperature=temperature)

        print(f'Using {llm.model_name} with temperature {temperature}\n')

        self.createAgent(llm, instructions)

    def createAgent(self, llm, instructions):

        # Define a new graph
        workflow = StateGraph(state_schema=State)

        # Define the (single) node in the graph
        workflow.add_node("Generate Report", GenerateReport(llm=llm, instructions=instructions))
        workflow.add_node("Summarize", Summarize(llm=llm))
        #workflow.add_node("Add Citations", AddCitations(llm))

        workflow.add_conditional_edges(START, check_if_summary_needed)
        workflow.add_edge("Summarize", "Generate Report")
        #workflow.add_edge("Generate Report", "Add Citations")
        #workflow.add_edge("Add Citations", END)

        # Add memory
        memory = MemorySaver()
        self.agent = workflow.compile(checkpointer=memory)