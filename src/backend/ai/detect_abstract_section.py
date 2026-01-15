from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.fix import OutputFixingParser
from pydantic import BaseModel, Field
from ..utils import Config
from .common import StateContentManager, extractLLMResponse, Config
from .prompts import setPrompt

# ---------------------------------------------------------------------------
class DetectAbstractSectionSchema(BaseModel):
    '''
    Returns a boolean indicating if the section header can be considered 
    as an abstract
    '''
    is_abstract: bool = Field(description='A boolean indicating if the section header can be considered as an abstract')

# ---------------------------------------------------------------------------
class DetectAbstractSection:

    detect_abstract_section_system_prompt = '''
    You are an expert in detecting if a section is an abstract given only the section header.

    <Instructions> 
    - Detect if the provided section header can be considered as an abstract.
    </Instructions>
    '''

    detect_abstract_section_human_prompt = lambda self, instructions: (f'''
    <Section Header>
    {{section_header}}
    </Section Header>
                                                              
    <Instructions>
    {instructions}
    
    - Provide the output in the following format.
    {{format_instructions}}
    </Instructions>
    ''')


    def __init__(self, llm, instructions):

        parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=DetectAbstractSectionSchema), 
                                             llm=llm,
                                             max_retries=Config.RETRY_COUNTER)
        
        self.detect_abstract_section_prompt = setPrompt(self.detect_abstract_section_system_prompt, 
                                                 self.detect_abstract_section_human_prompt(instructions),
                                                 parser)
        
        self.detect_abstract_section_chain = self.detect_abstract_section_prompt | llm | parser


    def __call__(self, state: StateContentManager):
        '''LLM detects an abstract section from a given section header'''

        return extractLLMResponse(task_name = 'Detect Abstract Section', 
                                  chain = self.detect_abstract_section_chain,
                                  kargs = {'section_header': state['current_section']},
                                  key_to_find = 'is_abstract',
                                  value_name = 'is_abstract')
        