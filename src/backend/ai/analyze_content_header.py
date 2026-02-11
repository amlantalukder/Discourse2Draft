from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.fix import OutputFixingParser
from pydantic import BaseModel, Field
from ..utils import Config
from .common import StateContentManager, extractLLMResponse
from .prompts import setPrompt

class AnalyzeContentHeaderSchema(BaseModel):
    '''
    Represents the list of keyphrases extracted from content header to get context on.
    '''
    keyphrases: list[str] = Field(f'List of maximum {Config.MAX_KEYPHRASES} keyphrases', max_length=Config.MAX_KEYPHRASES)

class AnalyzeContentHeaderSchemaForLitSearch(BaseModel):
    '''
    Represents the list of keyphrases extracted from content header to get context on.
    '''
    keyphrases: list[str] = Field(f'List of maximum {Config.MAX_KEYPHRASES_LIT_SEARCH} keyphrases', max_length=Config.MAX_KEYPHRASES_LIT_SEARCH)

class AnalyzeContentHeader:

    analyze_content_header_system_prompt = lambda self, max_keyphrases: f'''\
        You will be given a section header on a topic. Analyze the section header and find a list of independent 'keyphrases' on which you need information to write the section content. Always follow the rules below

        <Instructions>
        - List maximum of {max_keyphrases} key phrases. THE LIST MUST NOT BE MORE THAN {max_keyphrases}.
        - Each key phrase must be relevant to the section header.
        - Each key phrase must be semantically independent so that it can be used later to search information about the topic and the section header.
        </Instructions>\
        '''

    analyze_content_header_human_prompt = lambda self, instructions: f'''\
        <Previous Content Summary>
        {{content_pre}}
        </Previous Content Summary>

        <Current Section>
        {{current_section}}
        </Current Section>

        <Instructions>
        {instructions}
        - Read the Previous Content Summary.
        - Provide a list of keyphrases on which you need information to write text under the current section.

        - Provide the output in the following format.
        {{format_instructions}}
        
        - Output must be in JSON format with `json` tags.
        </Instructions>\
        '''

    def __init__(self, llm, for_lit_search=False):
        
        if not for_lit_search:
            self.max_keyphrases = Config.MAX_KEYPHRASES
            obj_schema = AnalyzeContentHeaderSchema
        else:
            self.max_keyphrases = Config.MAX_KEYPHRASES_LIT_SEARCH
            obj_schema = AnalyzeContentHeaderSchemaForLitSearch

        self.llm = llm
        self.parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=obj_schema), llm=llm)
        analyze_content_header_prompt = setPrompt(self.analyze_content_header_system_prompt(self.max_keyphrases), 
                                              self.analyze_content_header_human_prompt(instructions=''), 
                                              self.parser)
        self.analyze_content_header_chain = analyze_content_header_prompt | self.llm | self.parser

    def __call__(self, state: StateContentManager) -> StateContentManager:
        '''
        Extracts keyphrases from user content_header
        '''
        
        if state['content_specific_instructions']:
            instructions = f'''
            <Analysis criteria of the current section>
            {state['content_specific_instructions']}
            </Analysis criteria of the current section>'''

            analyze_content_header_chain = setPrompt(self.analyze_content_header_system_prompt(self.max_keyphrases), 
                                                self.analyze_content_header_human_prompt(instructions), 
                                                self.parser) | self.llm | self.parser
        else:
            analyze_content_header_chain = self.analyze_content_header_chain

        return extractLLMResponse(task_name = 'Analyze Content Header', 
                                  chain = analyze_content_header_chain,
                                  kargs = {'content_pre': state['content_pre'],
                                            'current_section': state['current_section']},
                                  keys_to_find = ['keyphrases'],
                                  value_names = ['keyphrases'])
