from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.fix import OutputFixingParser
from typing import Dict, List
from pydantic import BaseModel, Field
from .common import StateContentManager, extractLLMResponse, GENERATE_CONTENT_INSTRUCTIONS
from .prompts import setPrompt
from ..utils import Config

class GenerateContentSchema(BaseModel):
    '''
    Returns the content to fill the provided outline section
    '''
    content: str = Field(description='Content to fill the provided outline section')
    concept_map: Dict[str, List[str]] = Field(description='''Unidirectional hierarchical concept flow map of generated content.\
                                         Each node will be a keyphrase and will represent a concept of the generated content. \
                                         The nodes are represented as the keys in the dictionary. The edges of a key node are represented by a List of node names.''')

# ---------------------------------------------------------------------------
class GenerateContent:

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
    - Generate unidirectional hierarchical concept flow map of generated content.

    - Provide the output in the following format.
    {{format_instructions}}
    
    - Output must be in JSON format with `json` tags.
    </Instructions>\
    '''

    def __init__(self, llm, instructions):

        self.llm = llm
        self.instructions = instructions

        self.parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=GenerateContentSchema), 
                                             llm=self.llm,
                                             max_retries=Config.RETRY_COUNTER)
        
        generate_content_prompt = setPrompt(self.generate_content_system_prompt, 
                                                self.generate_content_human_prompt(instructions), 
                                                self.parser)
        
        self.generate_content_chain = generate_content_prompt | self.llm | self.parser


    def __call__(self, state: StateContentManager):
        '''LLM generates content for a given section header and previous section summary'''
        
        if state['content_specific_instructions']:
            instructions = f'{self.instructions}\n{state['content_specific_instructions']}'
            generate_content_chain = setPrompt(self.generate_content_system_prompt, 
                                                self.generate_content_human_prompt(instructions), 
                                                self.parser) | self.llm | self.parser
        else:
            generate_content_chain = self.generate_content_chain

        return extractLLMResponse(task_name = 'Generate Content', 
                                  chain = generate_content_chain,
                                  kargs = {'content_pre': state['content_pre'],
                                            'current_section': state['current_section']},
                                  keys_to_find = ['content', 'concept_map'],
                                  value_names = ['content', 'concept_map'])