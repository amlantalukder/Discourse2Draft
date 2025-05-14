from langchain_core.output_parsers import JsonOutputParser
from .utils import State
from .prompts import setPrompt

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
        "content": "Content text"    
    }}
    ```
    </Instructions>
    '''

    def __init__(self, llm, instructions):

        self.generate_report_prompt = setPrompt(self.generate_report_system_prompt(instructions), self.generate_report_human_prompt)
        self.generate_report_chain = self.generate_report_prompt | llm | JsonOutputParser()

    def __call__(self, state: State):
        '''LLM generates reports from a given outline'''
        response = self.generate_report_chain.invoke(input={'content_pre': state['content_pre'],
                                                            'current_section': state['current_section']})
        return {'response': response, 'steps': ['Generate Report']}