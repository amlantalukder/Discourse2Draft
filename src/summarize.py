from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from .utils import State, Config, retryInvoke
from .prompts import setPrompt

class SummarizeSchema(BaseModel):
    '''
    Returns the summary of the provided content
    '''
    summary: str = Field(description='Summary of the provided content')

class SummarizeOutputParser(JsonOutputParser):

    def __init__(self, output_parser=SummarizeSchema):
        super().__init__(pydantic_object=output_parser)

    def parseOutput(self, data):
        response = self.parse(data.content)
        return response

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
        "summary": "Summary of the provided content"    
    }}
    ```
    '''

    def __init__(self, llm):

        self.summarize_prompt = setPrompt(self.summarize_system_prompt, self.summarize_human_prompt)
        if llm.model_name in Config.llms_with_structured_output_support:
            self.summarize_chain = self.summarize_prompt | llm.with_structured_output(SummarizeSchema)
        else:
            self.summarize_chain = self.summarize_prompt | llm | SummarizeOutputParser().parseOutput

    def __call__(self, state: State):
        '''LLM generates summary for a given content'''

        response = retryInvoke(self.summarize_chain, input={'content': state['content_pre']})['summary']
        return {'content_pre': response, 'steps': ['Summarize']}