from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.fix import OutputFixingParser
from pydantic import BaseModel, Field
from ..utils import Config
from .common import StateOutlineManager, extractLLMResponse, Config
from .prompts import setPrompt
import logging

# ---------------------------------------------------------------------------
class FormatOutlineSchema(BaseModel):
    '''
    Returns the formatted outline
    '''
    content: str = Field(description='Formatted outline')

# ---------------------------------------------------------------------------
class FormatOutline:

    format_outline_system_prompt = '''
    You are an expert in extracting an structured outline from a given unstructured outline.

    <Instructions> 
    - Extract an outline with section, subsection headers.
    - Each outline must start with a which is the top level Title section.
    - Do not create any extra sections or sub-sections that may not be part of the unstructured outline. 
    - Place "<content>" tag wherever the content should be written.
    </Instructions>

    <Output format>
    - The outline must have "<content>" tag in place of actual content.
    - Generate output following markdown syntax. Do not wrap the output in code backticks. tStrictly follow the following example.
    </Output format>

    <Example>
    <Topic> 
    Hypertensive Disorders of Pregnancy
    </Topic>

    <Output>
    # Title: Hypertensive Disorders of Pregnancy: A Comprehensive Review of Pathophysiology, Clinical Management, Long-Term Implications, and Future Directions
    ## I. Introduction
    <content>
    ### A. Historical Perspective and Evolution of Understanding
    <content>
    ### B. Definition and Significance of Hypertensive Disorders of Pregnancy (HDP)
    #### 1. Global Burden of Disease (Maternal and Perinatal Morbidity & Mortality)
    <content>
    </Output>
    </Example>
    '''

    format_outline_human_prompt = lambda self, instructions: (f'''
    <Unformatted Outline>
    {{outline_unstructured}}
    </Unformatted Outline>
                                                              
    <Instructions>
    {instructions}
    
    - Provide the output in the following format.
    {{format_instructions}}
    </Instructions>
    ''')


    def __init__(self, llm, instructions):

        parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=FormatOutlineSchema), 
                                             llm=llm,
                                             max_retries=Config.RETRY_COUNTER)
        
        self.format_outline_prompt = setPrompt(self.format_outline_system_prompt, 
                                                 self.format_outline_human_prompt(instructions),
                                                 parser)
        
        self.format_outline_chain = self.format_outline_prompt | llm | parser


    def __call__(self, state: StateOutlineManager):
        '''LLM generates a structured outline from a given unstructured outline'''

        def contentChecker(response):
            if '<content>' not in response['content']:
                logging.info(f'Response does not have <content> tag, response: {response}')
                return False
            return True
        
        return extractLLMResponse(task_name = 'Format Outline', 
                                  chain = self.format_outline_chain,
                                  kargs = {'outline_unstructured': state['outline_unstructured']},
                                  key_to_find = 'content',
                                  value_name = 'content',
                                  additionalCheckingFunc=contentChecker)