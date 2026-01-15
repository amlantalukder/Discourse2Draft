from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables.base import RunnableLambda
from langchain.output_parsers.fix import OutputFixingParser
from langchain_core.tools import tool
from langchain.chains import GraphQAChain
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from .llms import getAIModel
from .common import (StateContentManager, extractLLMResponse,
                     GENERATE_CONTENT_INSTRUCTIONS, CITE_CONTEXT_INSTRUCTIONS)
from .prompts import setPrompt
from ..utils import Config
from utils import print_func_name

@tool
@print_func_name
def graphSearch(query: str) -> str:
    '''
    This tool provides the answer of a query using graph search
    '''
    llm = getAIModel('azure-gpt-4o')
    result = []
    for app_file_id, nx_graph in d_nx_graph.items():
        chain = GraphQAChain.from_llm(
            llm=llm, 
            graph=nx_graph
        )

        result.append(f'<{app_file_id}>{chain.invoke(query)['result']}</{app_file_id}>')

    return '\n\n'.join(result)

class GenerateContentGraphRAGSchema(BaseModel):
    '''
    Returns the content to fill the provided outline section
    '''
    content: str = Field(description='Content to fill the provided outline section')

# ---------------------------------------------------------------------------
class GenerateContentGraphRAG:

    generate_content_system_prompt = f'''\
    You will be provided a manuscript section header with or without previously written content on a specific topic. You are a scholarly ghost writer with expertise in the corresponding topic area. Your task is write a detailed and polished content on the section.
    
    {GENERATE_CONTENT_INSTRUCTIONS}\
    '''

    generate_content_human_prompt = lambda self, instructions: f'''\
    <Previous Content Summary>
    {{content_pre}}
    </Previous Content Summary>

    <Current Section>
    {{current_section}}
    </Current Section>
    
    <Instructions>
    {instructions}
    - Read the Previous Content Summary.
    - Find the <content> tag in Current Section. 
    - Write output texts that will fit in the <content> tag position and that will maintain continuity and relevance with the text above and below it.

    {CITE_CONTEXT_INSTRUCTIONS}

    - Provide the output in the following format.
    {{format_instructions}}
    
    - Output must be in JSON format with `json` tags.
    </Instructions>\
    '''

    def __init__(self, llm, instructions):

        self.llm = llm
        self.instructions = instructions

        self.parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=GenerateContentGraphRAGSchema), 
                                             llm=self.llm,
                                             max_retries=Config.RETRY_COUNTER)
        
        generate_content_prompt = setPrompt(self.generate_content_system_prompt, 
                                                self.generate_content_human_prompt(instructions), 
                                                self.parser)
        
        llm_with_tools = create_react_agent(model=self.llm, tools=[graphSearch]) 

        self.generate_content_chain = generate_content_prompt | llm_with_tools | RunnableLambda(lambda x: x['messages'][-1]) | self.parser


    def __call__(self, state: StateContentManager):
        '''LLM generates content for a given section header and previous section summary'''

        if state['content_specific_instructions']:
            instructions = f'{self.instructions}\n{state['content_specific_instructions']}'
            generate_content_chain = setPrompt(self.generate_content_system_prompt, 
                                                self.generate_content_human_prompt(instructions), 
                                                self.parser) | self.llm | self.parser
        else:
            generate_content_chain = self.generate_content_chain

        global d_nx_graph
        d_nx_graph = state['graphrag_context']

        return extractLLMResponse(task_name = 'Generate Content (GraphRAG)', 
                                  chain = generate_content_chain,
                                  kargs = {'content_pre': state['content_pre'],
                                            'current_section': state['current_section']},
                                  key_to_find = 'content',
                                  value_name = 'content')