from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from .utils import State, Config, retryInvoke
from .prompts import setPrompt

class SummarizeSchema(BaseModel):
    '''
    Returns the summary of the provided content
    '''
    summary: str = Field(description='Summary of the provided content')

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
    
    <Instructions>
    - Generate a comprehensive summary of the content.
    
    - Provide the output in the following format.
    {format_instructions}

    - Output must be in JSON format with `json` tags.
    </Instructions>
    '''

    def __init__(self, llm):

        parser = PydanticOutputParser(pydantic_object=SummarizeSchema)
        self.summarize_prompt = setPrompt(self.summarize_system_prompt, self.summarize_human_prompt, parser)
        self.summarize_chain = self.summarize_prompt | llm | parser

    def __call__(self, state: State):
        '''LLM generates summary for a given content'''

        response = retryInvoke(self.summarize_chain, input={'content': state['content_pre']})

        try:
            response = dict(response)['summary']
        except:
            raise Exception(f'Summarize response does not have content, response: {response}')
        
        return {'content_pre': response, 'steps': ['Summarize']}