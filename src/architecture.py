from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph
from .utils import State
from .llms import getOpenAIModel
from .generate_report import GenerateReport
from .add_citations import AddCitations

class Architecture:

    def __init__(self, model_name, temperature, instructions):
        llm = getOpenAIModel(model_name=model_name, temperature=temperature)
        self.createAgent(llm, instructions)

    def createAgent(self, llm, instructions):

        # Define a new graph
        workflow = StateGraph(state_schema=State)

        # Define the (single) node in the graph
        workflow.add_node("Generate Report", GenerateReport(llm=llm, instructions=instructions))
        #workflow.add_node("Add Citations", AddCitations(llm))
        workflow.add_edge(START, "Generate Report")
        #workflow.add_edge("Generate Report", "Add Citations")
        #workflow.add_edge("Add Citations", END)

        # Add memory
        memory = MemorySaver()
        self.agent = workflow.compile(checkpointer=memory)