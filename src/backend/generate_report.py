from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from .utils import State, Config, retryInvoke
from .prompts import setPrompt

class GenerateReportSchema(BaseModel):
    '''
    Returns the content to fill the provided outline section
    '''
    content: str = Field(description='Content to fill the provided outline section')

# ---------------------------------------------------------------------------
class GenerateReport:

    generate_report_system_prompt = lambda self, instructions: f'''\
    <Instructions>
    {instructions}
    </Instructions>
    '''

    generate_report_human_prompt = '''
    <Previous Content Summary>
    {content_pre}
    </Previous Content Summary>

    <Current Section>
    {current_section}
    </Current Section>
    
    <Instructions>
    - Read the Previous Content Summary. 
    - Find the <content> tag in Current Section. 
    - Write output texts that will fit in the <content> tag position and that will maintain continuity and relevance with the text above and below it.

    - Provide the output in the following format.
    {format_instructions}
    
    - Output must be in JSON format with `json` tags.
    </Instructions>
    '''

    def __init__(self, llm, instructions):

        parser = PydanticOutputParser(pydantic_object=GenerateReportSchema)
        self.generate_report_prompt = setPrompt(self.generate_report_system_prompt(instructions), 
                                                self.generate_report_human_prompt, 
                                                parser)
        self.generate_report_chain = self.generate_report_prompt | llm | parser


    def __call__(self, state: State):
        '''LLM generates reports from a given outline'''
        
        response = retryInvoke(self.generate_report_chain, input={'content_pre': state['content_pre'],
                                                            'current_section': state['current_section']})
        try:
            response = dict(response)['content']
        except:
            raise Exception(f'GenerateReport response does not have content, response: {response}')

        return {'response': response, 'steps': ['Generate Report']}