from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.fix import OutputFixingParser
from pydantic import BaseModel, Field
from ..utils import Config
from .common import StateOutlineManager, extractLLMResponse, Config
from .prompts import setPrompt
import logging
import re

# ---------------------------------------------------------------------------
class GenerateOutlineSchema(BaseModel):
    '''
    Returns the outline on the provided query
    '''
    content: str = Field(description='Outline on the provided query')

# ---------------------------------------------------------------------------
class GenerateOutline:

    generate_outline_system_prompt = '''
    You are an expert in generating outline for content on a given query.

    <Instructions>
    - Read the given query. 
    - Generate an outline with section, subsection headers.
    - Each outline must start with a "Title".
    - Do not provide "References" section or any other extra sections or sub-sections that may not have content based on the query. 
    - Place "<content>" tag wherever the content should be written.
    - If there is section specific instructions in the query, create an "<instructions></instruction>" tag under that specifc section and provide the instructions inside it.
    </Instructions>

    <Output format>
    - The outline must have "<content>" tag in place of actual content.
    - Generate output in markdown format. Strictly follow the following example.
    </Output format>

    <Example>
    <Query> 
    Hypertensive Disorders of Pregnancy
    </Query>

    <Output>
    # Title: Hypertensive Disorders of Pregnancy: A Comprehensive Review of Pathophysiology, Clinical Management, Long-Term Implications, and Future Directions
    ## I. Introduction
    <instructions>
     - Provide a brief overview of hypertensive disorders of pregnancy, including their significance and impact on maternal and fetal
     - Provide statistics on prevalence and outcomes.
    </instructions>
    <content>
    ### A. Historical Perspective and Evolution of Understanding
    <content>
    ### B. Definition and Significance of Hypertensive Disorders of Pregnancy (HDP)
    #### 1. Global Burden of Disease (Maternal and Perinatal Morbidity & Mortality)
    <content>
    </Output>
    </Example>
    '''

    generate_outline_human_prompt = lambda self, instructions: (f'''
    <Query>
    {{query}}
    </Query>
                                              
    <Instructions>
    {instructions}
    
    - Provide the output in the following format.
    {{format_instructions}}
    </Instructions>
    ''')


    def __init__(self, llm, instructions):

        parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=GenerateOutlineSchema), 
                                             llm=llm,
                                             max_retries=Config.RETRY_COUNTER)
        
        self.generate_outline_prompt = setPrompt(self.generate_outline_system_prompt, 
                                                 self.generate_outline_human_prompt(instructions),
                                                 parser)
        
        self.generate_outline_chain = self.generate_outline_prompt | llm | parser

    def __call__(self, state: StateOutlineManager):
        '''LLM generates outline from a given query'''

        def contentChecker(response):
            if '<content>' not in response['content']:
                logging.info(f'Response does not have <content> tag, response: {response}')
                return False
            return True

        return_vals = extractLLMResponse(task_name = 'Generate Outline', 
                                  chain = self.generate_outline_chain,
                                  kargs = {'query': state['query']},
                                  keys_to_find = ['content'],
                                  value_names = ['content'],
                                  additionalCheckingFunc=contentChecker)
        
        # Remove markdown tags
        return_vals['content'] = return_vals['content'].strip()
        if return_vals['content'].startswith('```markdown'):
            return_vals['content'] = re.sub(r'```(markdown)?[\n]*', '', return_vals['content'])

        return return_vals