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
    <Current Section>
    {current_section}
    </Current Section>
    
    Write under the provided subsection. Output in the following format.
    ```json
    {{
        "<last ontological branch term>": "<content>"    
    }}
    ```
    '''

    def __init__(self, llm, instructions):

        self.generate_report_prompt = setPrompt(self.generate_report_system_prompt(instructions), self.generate_report_human_prompt)
        self.generate_report_chain = self.generate_report_prompt | llm | JsonOutputParser()

    def __call__(self, state: State):
        '''LLM generates reports from a given outline'''
        response = self.generate_report_chain.invoke(input={'current_section': state['current_section']})
        return {'response': response, 'steps': ['Generate Report']}