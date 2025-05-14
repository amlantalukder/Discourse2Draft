from langchain_core.output_parsers import JsonOutputParser
from .utils import State, Config
from .prompts import setPrompt

# ---------------------------------------------------------------------------
class Summarize:

    summarize_system_prompt = f'''\
    You are an expert on writing summary of a given content.
    <Instructions>
    - The summary must not contain more than {Config.NUM_TOKENS_SUMMARY} tokens. 
    - The summary must include all important aspects of a given content.
    </Instructions>
    '''

    summarize_human_prompt = '''
    <Content>
    {content}
    </Content>
    
    Generate a comprehensive summary of the content.
    ```json
    {{
        "summary": "Summary of the content"    
    }}
    ```
    '''

    def __init__(self, llm):

        self.summarize_prompt = setPrompt(self.summarize_system_prompt, self.summarize_human_prompt)
        self.summarize_chain = self.summarize_prompt | llm | JsonOutputParser()

    def __call__(self, state: State):
        '''LLM generates reports from a given outline'''
        response = self.summarize_chain.invoke(input={'content': state['content_pre']})['summary']
        return {'content_pre': response, 'steps': ['Summarize']}