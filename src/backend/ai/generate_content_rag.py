from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.fix import OutputFixingParser
from typing import List, Dict
from pydantic import BaseModel, Field
from .common import (StateContentManager, extractLLMResponse, ReferenceSchema, 
                     GENERATE_CONTENT_INSTRUCTIONS, CITE_CONTEXT_INSTRUCTIONS)
from .prompts import setPrompt
from ..utils import Config
import logging

# ---------------------------------------------------------------------------
class GenerateContentRAGSchema(BaseModel):
    '''
    The content to fill the provided outline section
    '''
    content: str = Field(description='Content to fill the provided outline section')
    references: List[ReferenceSchema] = Field(description='A list references of the citations in the content')
    concept_map: Dict[str, List[str]] = Field(description='''Unidirectional hierarchical concept flow map of generated content.\
                                         Each node will be a keyphrase and will represent a concept of the generated content. \
                                         The nodes are represented as the keys in the dictionary. The edges of a key node are represented by a List of node names.''')

# ---------------------------------------------------------------------------
class GenerateContentRAG:

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

    <RAG Context>
    {{rag_context}}
    </RAG Context>
    
    <Instructions>
    {instructions}
    - Read the Previous Content Summary.
    - Find the <content> tag in Current Section. 
    - Write output texts that will fit in the <content> tag position and that will maintain continuity and relevance with the text above and below it.
    - Generate unidirectional hierarchical concept flow map of generated content.
    
    {CITE_CONTEXT_INSTRUCTIONS}
    
    - Provide the output in the following format.
    {{format_instructions}}
    
    - Output must be in JSON format with `json` tags.
    </Instructions>\
    '''

    def __init__(self, llm, instructions):

        self.llm = llm
        self.instructions = instructions
        self.parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=GenerateContentRAGSchema), 
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

        ret, response = extractLLMResponse(task_name = 'Generate Content (RAG)', 
                                  chain = generate_content_chain,
                                  kargs = {'content_pre': state['content_pre'],
                                           'current_section': state['current_section'],
                                           'rag_context': state['rag_context']},
                                  keys_to_find = ['content', 'concept_map'],
                                  value_names = ['content', 'concept_map'],
                                  return_response = True)
        try:
            references = {ref.file_id: ref.file_name for ref in dict(response).get('references', [])}
        except:
            logging.info(f'GenerateContentRAG response does not have references, response: {response}')
            references = {}

        return ret | {'references': references}