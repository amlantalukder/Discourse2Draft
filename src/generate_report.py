from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from .utils import State, Config, retryInvoke
from .prompts import setPrompt

class GenerateReportSchema(BaseModel):
    '''
    Returns the content to fill the provided outline section
    '''
    content: str = Field(description='Content to fill the provided outline section')

class GenerateReportOutputParser(JsonOutputParser):

    def __init__(self, output_parser=GenerateReportSchema):
        super().__init__(pydantic_object=output_parser)

    def parseOutput(self, data):
        response = self.parse(data.content)
        return response

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
    ```json
    {{
        "content": "Content to fill the provided outline section"    
    }}
    ```
    </Instructions>
    '''

    def __init__(self, llm, instructions):

        self.generate_report_prompt = setPrompt(self.generate_report_system_prompt(instructions), self.generate_report_human_prompt)
        
        if llm.model_name in Config.llms_with_structured_output_support:
            self.generate_report_chain = self.generate_report_prompt | llm.with_structured_output(GenerateReportSchema)
        else:
            self.generate_report_chain = self.generate_report_prompt | llm | GenerateReportOutputParser().parseOutput


    def __call__(self, state: State):
        '''LLM generates reports from a given outline'''
        
        response = retryInvoke(self.generate_report_chain, input={'content_pre': state['content_pre'],
                                                            'current_section': state['current_section']})
        try:
            response = dict(response)['content']
        except:
            raise Exception(f'GenerateReport response does not have content, response: {response}')

        return {'response': response, 'steps': ['Generate Report']}